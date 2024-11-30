# converters/utils/Common_operations.py

import json
import logging
import os
import uuid
from pathlib import Path
from typing import Any

from lxml import etree

from .notice_tracker import NoticeTracker
from .xml_processor import XMLProcessor

logger = logging.getLogger(__name__)


class NoticeProcessor:
    """Process XML notices and convert them to OCDS releases."""

    def __init__(
        self, ocid_prefix: str, scheme: str = "eu-oj", db_path: str | None = None
    ) -> None:
        """
        Initialize the NoticeProcessor.

        Args:
            ocid_prefix: Prefix for OCIDs
            scheme: Scheme for related processes (default: eu-oj)
            db_path: Optional path to the SQLite database
        """
        self.ocid_prefix = ocid_prefix
        self.scheme = scheme
        self._db_path = db_path or "notices.db"
        self._tracker = None
        self.xml_processor = XMLProcessor()

    @property
    def tracker(self) -> NoticeTracker:
        """Get thread-local tracker instance."""
        if self._tracker is None:
            self._tracker = NoticeTracker(self._db_path)
        return self._tracker

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

    def process_notice(self, xml_content: str | bytes) -> list[str]:
        """
        Main entry point for notice processing following specification rules.
        Creates separate releases for PIN-only parts, single release otherwise.
        """
        tree = self.xml_processor.parse_xml(xml_content)
        notice_info = self.xml_processor.extract_notice_info(tree)
        releases = self._process_notice(tree, notice_info)

        # Track notices in database
        for release_str in releases:
            release = json.loads(release_str)
            self._track_notice(notice_info, release["ocid"])

        return releases

    def _process_notice(
        self, tree: etree._Element, notice_info: dict[str, Any]
    ) -> list[str]:
        """
        Process a notice following the specification rules:
        - Separate release for each part in PIN-only notices
        - Single release with appropriate OCID for other notices
        """
        if notice_info["is_pin_only"]:
            parts = self.get_notice_parts(tree)
            if not parts:
                return [self._create_single_release(tree, notice_info)]

            # Process each part separately for PIN-only
            releases = []
            for part in parts:
                part_id = part.xpath("string(cbc:ID)", namespaces=self.namespaces)
                ocid = f"{self.ocid_prefix}-{uuid.uuid4()}"

                # Track the part
                self.tracker.track_part(notice_info["notice_id"], part_id, ocid)

                # Create release for part
                release = {
                    "id": notice_info["notice_id"],
                    "initiationType": "tender",
                    "ocid": ocid,
                }

                # Add references if needed
                part_refs = self.get_part_previous_references(part)
                if part_refs:
                    release["relatedProcesses"] = part_refs

                releases.append(json.dumps(release))
            return releases

        # Create single release for non-PIN-only notices
        return [self._create_single_release(tree, notice_info)]

    def _create_single_release(
        self, tree: etree._Element, notice_info: dict[str, Any]
    ) -> str:
        """Create a single release with appropriate OCID and references."""
        ocid = self.determine_ocid(tree)
        release = {
            "id": notice_info["notice_id"],
            "initiationType": "tender",
            "ocid": ocid,
        }

        # Add related processes if needed
        prev_refs = self.get_previous_references(tree)
        if prev_refs:
            release["relatedProcesses"] = prev_refs

        return json.dumps(release)

    def determine_ocid(self, tree: etree._Element) -> str:
        """
        Determine OCID following specification rules:
        - New OCID if first publication
        - New OCID if CAN for framework/DPS
        - New OCID if previous was PIN-only
        - Previous OCID otherwise
        """
        # Check if this is first publication
        prev_pub_ref = tree.xpath(
            "//cac:NoticeDocumentReference", namespaces=self.namespaces
        )
        if not prev_pub_ref:
            logger.info("First publication - generating new OCID")
            return f"{self.ocid_prefix}-{uuid.uuid4()}"

        # Check if this is CAN for framework/DPS
        if self.is_can_for_framework_or_dps(tree):
            logger.info("CAN for framework/DPS - generating new OCID")
            return f"{self.ocid_prefix}-{uuid.uuid4()}"

        # Get previous publication reference
        prev_pub_id = self.get_previous_publication_id(tree)
        if not prev_pub_id:
            logger.info("No previous publication ID - generating new OCID")
            return f"{self.ocid_prefix}-{uuid.uuid4()}"

        # Check if previous was PIN-only
        prev_notice = self.tracker.get_previous_notice(prev_pub_id)
        if prev_notice:
            if prev_notice[3]:  # is_pin_only
                logger.info("Previous was PIN-only - generating new OCID")
                return f"{self.ocid_prefix}-{uuid.uuid4()}"
            if prev_notice[1]:  # has ocid
                logger.info("Using previous OCID: %s", prev_notice[1])
                return prev_notice[1]

        logger.warning("Previous notice referenced but OCID not found")
        return f"{self.ocid_prefix}-{uuid.uuid4()}"

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
                "scheme": self.scheme,
                "identifier": prev_pub_id,
            }
        ]

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
                        "scheme": self.scheme,
                        "identifier": identifier,
                    }
                )
        return refs

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
            logger.info("Found previous planning notice ID: %s", refs[0])
            return refs[0]
        return None

    def get_notice_parts(self, tree: etree._Element) -> list[etree._Element]:
        """Get all parts from a notice."""
        return tree.xpath(
            "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']",
            namespaces=self.namespaces,
        )

    def _extract_notice_info(self, tree: etree._Element) -> dict[str, Any]:
        """Extract basic information from notice."""
        return {
            "notice_id": tree.xpath("string(/*/cbc:ID)", namespaces=self.namespaces),
            "publication_date": tree.xpath(
                "string(/*/cbc:IssueDate)", namespaces=self.namespaces
            ),
            "notice_type": tree.xpath(
                "string(/*/cbc:NoticeTypeCode)", namespaces=self.namespaces
            )
            or "Unknown",
            "is_pin_only": self.is_pin_only(tree),
        }

    def _track_notice(self, notice_info: dict[str, Any], ocid: str) -> None:
        """Track notice in database."""
        self.tracker.track_notice(
            notice_id=notice_info["notice_id"],
            ocid=ocid,
            notice_type=notice_info["notice_type"],
            is_pin_only=notice_info["is_pin_only"],
            publication_date=notice_info["publication_date"],
        )


def remove_empty_elements(data):
    """
    Recursively remove empty lists, empty dicts, or None elements from a dictionary or list.
    Preserves False boolean values and zero numeric values.
    """
    if isinstance(data, dict):
        return {
            key: remove_empty_elements(value)
            for key, value in data.items()
            if value is not None and (value or isinstance(value, bool | int | float))
        }
    if isinstance(data, list):
        return [
            remove_empty_elements(item)
            for item in data
            if item is not None and (item or isinstance(item, bool | int | float))
        ]
    return data


# Additional step to remove keys with empty dictionaries
def remove_empty_dicts(data):
    if isinstance(data, dict):
        return {
            key: remove_empty_dicts(value)
            for key, value in data.items()
            if value or isinstance(value, bool | int | float)
        }
    if isinstance(data, list):
        return [
            remove_empty_dicts(item)
            for item in data
            if item or isinstance(item, bool | int | float)
        ]
    return data


def process_bt_section(
    release_json, xml_content, parse_funcs, merge_func, section_name
) -> None:
    logger = logging.getLogger(__name__)
    try:
        logger.info("Starting %s processing", section_name)
        for parse_function in parse_funcs:
            parsed_data = parse_function(xml_content)
            logger.info("Parsed data for %s: %s", section_name, parsed_data)
            if parsed_data:
                merge_func(release_json, parsed_data)
                logger.info("Successfully merged data for %s", section_name)
                return
        logger.warning("No data found for %s", section_name)
    except Exception:
        logger.exception("Error processing %s data", section_name)


def configure_logging() -> None:
    """Configures logging to write to a log file, unless running on GitHub Actions."""
    # Check if running on GitHub Actions
    if os.environ.get("GITHUB_ACTIONS") == "true":
        # Disable logging
        logging.disable(logging.CRITICAL)
        return

    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Create file handler and set level to info
    log_file = Path("app.log")
    file_handler = logging.FileHandler(log_file, mode="w")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Remove any existing handlers (like console handlers)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Add file handler to logger
    logger.addHandler(file_handler)
