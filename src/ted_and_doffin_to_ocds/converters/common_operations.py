# converters/Common_operations.py

import json
import uuid
import logging
import os
from lxml import etree
from pathlib import Path

logger = logging.getLogger(__name__)


class NoticeProcessor:
    def __init__(self, ocid_prefix, scheme):
        self.ocid_prefix = ocid_prefix
        self.scheme = scheme
        self.item_id_counter = 1
        self.namespaces = {
            "urn": "oasis:names:specification:ubl:schema:xsd:PriorInformationNotice-2",
            "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
            "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
            "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
            "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
            "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
            "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
        }

    def create_release(self, xml_content):
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")

        tree = etree.fromstring(xml_content)

        # Check if it's a PIN-only notice
        if self.is_pin_only_notice(tree):
            parts = tree.xpath(
                "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']",
                namespaces=self.namespaces,
            )
            if parts:
                releases = []
                for part in parts:
                    release = {}
                    release["id"] = self.get_notice_identifier(tree)
                    release["initiationType"] = "tender"
                    release["ocid"] = self.generate_ocid(tree, is_part=True)
                    release["tender"] = self.create_tender_for_part(part)
                    releases.append(release)
                return json.dumps(releases)
            # If no parts found, treat it as a single release
            parts = [
                tree.xpath("/*/cac:ProcurementProjectLot", namespaces=self.namespaces)[
                    0
                ]
            ]

        else:
            parts = [
                tree.xpath("/*/cac:ProcurementProjectLot", namespaces=self.namespaces)[
                    0
                ]
            ]

        releases = []
        for part in parts:
            release = {}
            release["id"] = self.get_notice_identifier(tree)
            release["initiationType"] = "tender"
            release["ocid"] = self.generate_ocid(tree)
            release["tender"] = self.create_tender_for_part(part)

            # Reference previous publication
            related_process = self.reference_previous_publication(tree)
            if related_process:
                release["relatedProcesses"] = [related_process]

            releases.append(release)

        return json.dumps(releases)

    def create_tender_for_part(self, part):
        return {
            "id": part.xpath("string(cbc:ID)", namespaces=self.namespaces),
            "title": part.xpath(
                "string(cac:ProcurementProject/cbc:Name)", namespaces=self.namespaces
            ),
            "description": part.xpath(
                "string(cac:ProcurementProject/cbc:Description)",
                namespaces=self.namespaces,
            ),
            "status": "planning",
            "mainProcurementCategory": part.xpath(
                "string(cac:ProcurementProject/cbc:ProcurementTypeCode)",
                namespaces=self.namespaces,
            ).lower(),
        }

    def get_notice_identifier(self, tree):
        return tree.xpath("string(/*/cbc:ID)", namespaces=self.namespaces)

    def generate_ocid(self, tree, is_part=False):
        if is_part or self.needs_new_ocid(tree):
            return f"{self.ocid_prefix}-{uuid.uuid4()}"
        return self.get_previous_ocid(tree)

    def needs_new_ocid(self, tree):
        return (
            self.is_first_publication(tree)
            or self.is_can_for_framework_or_dps(tree)
            or self.previous_was_pin_only(tree)
        )

    def is_first_publication(self, tree):
        return self.get_previous_publication(tree) is None

    def is_can_for_framework_or_dps(self, tree):
        root_tag = tree.tag
        if not root_tag.endswith("ContractAwardNotice"):
            return False

        framework_indicator = tree.xpath(
            "string(//efbc:ContractFrameworkIndicator)", namespaces=self.namespaces
        )
        return framework_indicator.lower() == "true"

    def previous_was_pin_only(self, tree):
        previous_id = self.get_previous_publication(tree)
        if not previous_id:
            return False
        # Implement logic to check if the previous notice was a PIN-only
        # This might involve fetching the previous notice and checking its type
        return False  # Placeholder

    def get_previous_ocid(self, tree):
        previous_id = self.get_previous_publication(tree)
        if previous_id:
            return f"{self.ocid_prefix}-{previous_id}"
        return None

    def is_pin_only_notice(self, tree):
        notice_type = tree.xpath(
            "string(/*/cbc:NoticeTypeCode)", namespaces=self.namespaces
        ).lower()
        return notice_type == "pin-only"

    def process_notice(self, xml_content):
        tree = etree.fromstring(xml_content)

        if self.is_pin_only_notice(tree):
            parts = tree.xpath(
                "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']",
                namespaces=self.namespaces,
            )
            return [self.create_release_for_part(tree, part) for part in parts]
        return [self.create_release(xml_content)]

    def create_release_for_part(self, tree, part):
        release = json.loads(self.create_release(etree.tostring(tree)))

        part_id = part.xpath("string(cbc:ID)", namespaces=self.namespaces)
        release["tender"] = {
            "id": part_id,
            "title": part.xpath(
                "string(cac:ProcurementProject/cbc:Name)", namespaces=self.namespaces
            ),
            "description": part.xpath(
                "string(cac:ProcurementProject/cbc:Description)",
                namespaces=self.namespaces,
            ),
            "status": "planning",
            "mainProcurementCategory": part.xpath(
                "string(cac:ProcurementProject/cbc:ProcurementTypeCode)",
                namespaces=self.namespaces,
            ).lower(),
        }

        return json.dumps(release)

    def get_previous_publication(self, tree):
        return (
            tree.xpath(
                "string(/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingProcess/cac:NoticeDocumentReference/cbc:ID[@schemeName='notice-id-ref'])",
                namespaces=self.namespaces,
            ).strip()
            or None
        )

    def reference_previous_publication(self, tree):
        previous_publication = self.get_previous_publication(tree)
        if not previous_publication:
            return None

        if self.is_pin(tree) and self.has_multiple_procurement_project_lots(tree):
            return {
                "id": "1",
                "relationship": ["planning"],
                "scheme": self.scheme,
                "identifier": tree.xpath(
                    "string(/*/cbc:ID)", namespaces=self.namespaces
                ),
            }

        return None

    def is_pin(self, tree):
        root_tag = tree.tag.split("}")[-1]
        if root_tag != "PriorInformationNotice":
            return False

        notice_type = tree.xpath(
            "string(/*/cbc:NoticeTypeCode)", namespaces=self.namespaces
        ).lower()
        return notice_type in "pin-only"

    def has_single_procurement_project_lot(self, tree):
        return (
            len(tree.xpath("/*/cac:ProcurementProjectLot", namespaces=self.namespaces))
            == 1
        )

    def has_multiple_procurement_project_lots(self, tree):
        return (
            len(tree.xpath("/*/cac:ProcurementProjectLot", namespaces=self.namespaces))
            > 1
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
