# converters/Common_operations.py

import json
import uuid
import logging
import os
from lxml import etree
from pathlib import Path


logger = logging.getLogger(__name__)


class NoticeProcessor:
    def __init__(self, ocid_prefix: str, scheme: str = "eu-oj"):
        self.ocid_prefix = ocid_prefix
        self.scheme = scheme

    def process_notice(self, xml_content: str | bytes) -> list[str]:
        """Process the notice and return a list of OCDS releases."""
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")

        tree = etree.fromstring(xml_content)

        # Check if this is a PIN-only notice
        if self.is_pin_only(tree):
            # Look for parts (not lots)
            parts = tree.xpath(
                "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']",
                namespaces=self.namespaces,
            )

            if parts:
                # Create separate release for each part
                releases = []
                for _part in parts:  # Using _part to indicate unused variable
                    release = self.create_base_release(tree)
                    # For PIN-only parts, always generate new OCID
                    release["ocid"] = f"{self.ocid_prefix}-{uuid.uuid4()}"
                    releases.append(json.dumps(release))
                return releases
            # PIN-only but no parts - create single release
            release = self.create_base_release(tree)
            release["ocid"] = f"{self.ocid_prefix}-{uuid.uuid4()}"
            return [json.dumps(release)]

        # For non-PIN-only notices
        release = self.create_base_release(tree)

        # Generate new OCID if it's a CAN for framework/DPS
        if self.is_can_for_framework_or_dps(tree):
            release["ocid"] = f"{self.ocid_prefix}-{uuid.uuid4()}"
        else:
            release["ocid"] = self.determine_ocid(tree)

        # Handle previous publication reference
        prev_pub = self.get_previous_publication(tree)
        if prev_pub is not None:
            related_process = self.create_related_process(tree, prev_pub)
            if related_process:
                release["relatedProcesses"] = [related_process]

        return [json.dumps(release)]

    def create_base_release(self, tree: etree._Element) -> dict:
        """Create the base release object with common fields."""
        notice_id = tree.xpath("string(/*/cbc:ID)", namespaces=self.namespaces)
        return {"id": notice_id, "initiationType": "tender"}

    def determine_ocid(self, tree: etree._Element) -> str:
        """Determine the OCID based on notice conditions."""
        if (
            self.is_first_publication(tree)
            or self.is_can_for_framework_or_dps(tree)
            or self.previous_was_pin_only(tree)
        ):
            return f"{self.ocid_prefix}-{uuid.uuid4()}"

        # Try to get previous publication's OCID
        prev_ocid = self.get_previous_ocid(tree)
        return prev_ocid if prev_ocid else f"{self.ocid_prefix}-{uuid.uuid4()}"

    def create_related_process(
        self, tree: etree._Element, prev_pub: etree._Element
    ) -> dict | None:
        """Create related process object if needed."""
        # Check if previous publication is PIN
        if not self.is_pin(prev_pub):
            return None

        # Count procurement project lots in previous publication
        lots = prev_pub.xpath(
            "/*/cac:ProcurementProjectLot", namespaces=self.namespaces
        )

        # If PIN has single lot or is not PIN, return None
        if len(lots) <= 1:
            return None

        # For PIN with multiple lots, create related process
        return {
            "id": "1",
            "relationship": ["planning"],
            "scheme": self.scheme,
            "identifier": tree.xpath("string(/*/cbc:ID)", namespaces=self.namespaces),
        }

    def is_pin_only(self, tree: etree._Element) -> bool:
        """Check if notice is a PIN used only for information."""
        notice_type = tree.xpath(
            "string(/*/cbc:NoticeTypeCode[@listName='planning'])",
            namespaces=self.namespaces,
        )
        return notice_type == "pin-only"

    def is_first_publication(self, tree: etree._Element) -> bool:
        """Check if this is the first publication for the procedure."""
        prev_pub_ref = tree.xpath(
            "/*/cac:PreviousDocumentReference", namespaces=self.namespaces
        )
        return not bool(prev_pub_ref)

    def is_can(self, tree: etree._Element) -> bool:
        """
        Check if this is a Contract Award Notice (CAN).
        """
        # Get the root element tag without namespace
        root_tag = etree.QName(tree).localname
        return root_tag == "ContractAwardNotice"

    def is_can_for_framework_or_dps(self, tree: etree._Element) -> bool:
        """
        Check if this is a Contract Award Notice (CAN) for framework agreement or DPS.

        Args:
            tree (etree._Element): The XML element tree to check

        Returns:
            bool: True if this is a CAN for framework agreement or DPS, False otherwise
        """
        # First check if this is a CAN at all
        if not self.is_can(tree):
            return False

        # Check for framework agreement at both project and lot levels
        is_framework = tree.xpath(
            """boolean(/*/cac:ProcurementProject//cbc:ProcurementTypeCode[
                @listName='contract-nature' and text()='framework-agreement'] |
            /*/cac:ProcurementProjectLot//cbc:ProcurementTypeCode[
                @listName='contract-nature' and text()='framework-agreement'])""",
            namespaces=self.namespaces,
        )

        # Check for DPS both in procurement type codes and contracting system
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

    def previous_was_pin_only(self, tree: etree._Element) -> bool:
        """Check if previous publication was a PIN-only notice."""
        prev_pub = self.get_previous_publication(tree)
        if prev_pub is not None:
            return self.is_pin_only(prev_pub)
        return False

    def get_previous_publication(self, tree: etree._Element) -> etree._Element | None:
        """Get the previous publication referenced by this notice."""
        prev_pub_id = tree.xpath(
            "string(/*/cac:PreviousDocumentReference/cbc:ID)",
            namespaces=self.namespaces,
        )
        if prev_pub_id:
            # In a real implementation, this would retrieve the actual previous
            # publication document. For this example, we'll return None
            return None
        return None

    def get_previous_ocid(self, tree: etree._Element) -> str | None:
        """Get the OCID from the previous publication."""
        prev_pub = self.get_previous_publication(tree)
        if prev_pub is not None:
            # In a real implementation, this would extract the OCID from
            # the previous publication. For this example, we'll return None
            return None
        return None

    def is_pin(self, tree: etree._Element) -> bool:
        """Check if the notice is a PIN."""
        notice_type = tree.xpath(
            "string(/*/cbc:NoticeTypeCode)", namespaces=self.namespaces
        )
        return notice_type in ["PIN", "Periodic"]

    @property
    def namespaces(self) -> dict:
        """XML namespaces used in eForms."""
        return {
            "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
            "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
            "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
            "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
            "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
            "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
        }


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
):
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


def configure_logging():
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
