import logging
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Final

from lxml import etree
from lxml.etree import ElementBase, _Element  # Import types explicitly

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class XMLError:
    """XML processing error messages."""

    INVALID_CONTENT = "Invalid XML content"
    EMPTY_DOCUMENT = "Empty XML document"
    INVALID_TREE = "Invalid XML tree type"


class XMLProcessor:
    """Handles XML parsing and extraction operations."""

    # Define constants
    MAX_XML_SIZE: Final[int] = 50 * 1024 * 1024  # 50MB limit

    @property
    def namespaces(self) -> dict[str, str]:
        """XML namespaces used in eForms."""
        return {
            "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
            "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
            "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
            "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
            "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
            "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
        }

    def parse_xml(self, content: str | bytes) -> etree._Element:
        """Parse XML content into an element tree."""
        if len(content) > self.MAX_XML_SIZE:
            error_msg = f"XML content exceeds {self.MAX_XML_SIZE} bytes limit"
            raise ValueError(error_msg)

        if isinstance(content, str):
            content = content.encode("utf-8")

        try:
            parser = etree.XMLParser(recover=True, remove_blank_text=True)
            tree = etree.fromstring(content, parser=parser)
            self._validate_tree(tree)
        except etree.XMLSyntaxError as e:
            logger.exception("XML parsing error")
            error_msg = f"{XMLError.INVALID_CONTENT}: {e}"
            raise ValueError(error_msg) from e
        else:
            return tree

    @contextmanager
    def safe_xml_parse(self, content: str | bytes) -> Generator[etree._Element]:
        """Safely parse XML with error handling."""
        try:
            tree = self.parse_xml(content)
            yield tree
        except etree.XMLSyntaxError as e:
            logger.exception("XML parsing error")
            raise ValueError(XMLError.INVALID_CONTENT) from e

    def _validate_tree(self, tree: _Element) -> None:
        """Validate parsed XML tree."""
        if tree is None:
            raise ValueError(XMLError.EMPTY_DOCUMENT)
        # Check for both ElementBase and _Element types
        if not isinstance(tree, _Element | ElementBase):
            error_msg = f"{XMLError.INVALID_TREE}: {type(tree)}"
            raise TypeError(error_msg)

    def extract_notice_info(self, tree: etree._Element) -> dict[str, Any]:
        """Extract basic information from notice."""
        return {
            "notice_id": self._xpath_string(tree, "/*/cbc:ID"),
            "publication_date": self._xpath_string(tree, "/*/cbc:IssueDate"),
            "notice_type": self._xpath_string(tree, "/*/cbc:NoticeTypeCode")
            or "Unknown",
            "is_pin_only": self.is_pin_only(tree),
        }

    def _xpath_string(self, tree: etree._Element, xpath: str) -> str:
        """Helper method for string XPath queries."""
        return tree.xpath(f"string({xpath})", namespaces=self.namespaces)

    def is_pin_only(self, tree: etree._Element) -> bool:
        """Check if notice is a PIN used only for information."""
        notice_type = tree.xpath(
            "string(/*/cbc:NoticeTypeCode[@listName='planning'])",
            namespaces=self.namespaces,
        )
        return notice_type == "pin-only"

    def get_previous_publication_id(self, tree: etree._Element) -> str | None:
        """Get ID of the previous planning notice if it exists."""
        refs = tree.xpath(
            "//cac:NoticeDocumentReference/cbc:ID[@schemeName='notice-id-ref']/text()",
            namespaces=self.namespaces,
        )
        if refs:
            return refs[0]
        return None

    def get_notice_parts(self, tree: etree._Element) -> list[etree._Element]:
        """Get all parts from a notice."""
        return tree.xpath(
            "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']",
            namespaces=self.namespaces,
        )

    def is_can_for_framework_or_dps(self, tree: etree._Element) -> bool:
        """Check if notice is a CAN for framework agreement or DPS."""
        if not self.is_can(tree):
            return False

        is_framework = tree.xpath(
            """boolean(/*/cac:ProcurementProject//cbc:ProcurementTypeCode[
                @listName='contract-nature' and text()='framework-agreement'] |
            /*/cac:ProcurementProjectLot//cbc:ProcurementTypeCode[
                @listName='contract-nature' and text()='framework-agreement'])""",
            namespaces=self.namespaces,
        )

        is_dps = tree.xpath(
            """boolean(
                /*/cac:ProcurementProject//cbc:ProcurementTypeCode[
                    @listName='contract-nature' and text()='dps'] |
                /*/cac:ProcurementProjectLot//cbc:ProcurementTypeCode[
                    @listName='contract-nature' and text()='dps'] |
                /*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/
                    cac:TenderingProcess/cac:ContractingSystem[
                        cbc:ContractingSystemTypeCode/@listName='dps-usage']/
                        cbc:ContractingSystemTypeCode[text()!='none']
            )""",
            namespaces=self.namespaces,
        )

        return is_framework or is_dps

    def is_can(self, tree: etree._Element) -> bool:
        """Check if notice is a Contract Award Notice."""
        return etree.QName(tree).localname == "ContractAwardNotice"

    def get_part_previous_references(
        self, part: etree._Element
    ) -> list[dict[str, Any]]:
        """Get previous document references specific to a part."""
        refs = []
        notice_refs = part.xpath(
            ".//cac:NoticeDocumentReference", namespaces=self.namespaces
        )

        for ref in notice_refs:
            notice_id = ref.xpath("string(cbc:ID)", namespaces=self.namespaces)
            part_id = ref.xpath(
                "string(cbc:ReferencedDocumentInternalAddress)",
                namespaces=self.namespaces,
            )
            if notice_id:
                identifier = f"{notice_id}-{part_id}" if part_id else notice_id
                refs.append(
                    {
                        "id": str(len(refs) + 1),
                        "relationship": ["planning"],
                        "scheme": self.namespaces,
                        "identifier": identifier,
                    }
                )
        return refs

    def get_previous_references(self, tree: etree._Element) -> list[dict[str, Any]]:
        """
        Get references to previous publications per specification:
        - Only for PIN/Periodic with multiple parts
        - Includes id="1" and relationship=["planning"]
        """
        prev_pub_id = self.get_previous_publication_id(tree)
        if not prev_pub_id:
            return []

        prev_notice = self.tracker.get_previous_notice(prev_pub_id)
        if not prev_notice:
            return []

        # Only process PIN/Periodic notices
        if prev_notice[2] not in ["PIN", "Periodic"]:
            return []

        # Check for multiple parts
        prev_parts = self.tracker.get_notice_parts(prev_pub_id)
        if len(prev_parts) <= 1:
            return []

        # Return reference for PIN/Periodic with multiple parts
        return [
            {
                "id": "1",
                "relationship": ["planning"],
                "scheme": self.namespaces,
                "identifier": prev_pub_id,
            }
        ]
