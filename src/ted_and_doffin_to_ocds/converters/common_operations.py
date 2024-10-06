# converters/Common_operations.py

import json
import uuid
import logging
import os
from lxml import etree
from pathlib import Path


class NoticeProcessor:
    def __init__(self, ocid_prefix, scheme):
        self.ocid_prefix = ocid_prefix
        self.scheme = scheme
        self.item_id_counter = 1

    def create_release(self, xml_content):
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")

        tree = etree.fromstring(xml_content)

        release = {}
        release["id"] = self.get_notice_identifier(tree)
        release["initiationType"] = "tender"
        release["ocid"] = self.generate_ocid(tree)

        # Reference previous publication
        related_process = self.reference_previous_publication(tree)
        if related_process:
            release["relatedProcesses"] = [related_process]

        return json.dumps(release)

    def get_notice_identifier(self, tree):
        return tree.xpath(
            "string(/*/cbc:ID)",
            namespaces=self.namespaces,
        )

    def generate_ocid(self, tree):
        if self.needs_new_ocid(tree):
            return f"{self.ocid_prefix}-{uuid.uuid4()}"
        return self.get_previous_ocid(tree)

    def needs_new_ocid(self, tree):
        return (
            self.is_first_publication(tree)
            or self.is_can_for_framework_or_dps(tree)
            or self.previous_was_pin_only(tree)
        )

    def is_first_publication(self, tree):  # noqa: ARG002
        # Implement logic to check if it's the first publication
        # This is a placeholder implementation
        return False

    def is_can_for_framework_or_dps(self, tree):  # noqa: ARG002
        # Implement logic to check if it's a CAN for framework or DPS
        # This is a placeholder implementation
        return False

    def previous_was_pin_only(self, tree):  # noqa: ARG002
        # Implement logic to check if previous publication was PIN-only
        # This is a placeholder implementation
        return False

    def get_previous_ocid(self, tree):  # noqa: ARG002
        # Implement logic to retrieve OCID from previous publication
        # This is a placeholder implementation
        return f"{self.ocid_prefix}-placeholder"

    def is_pin_only_notice(self, tree):  # noqa: ARG002
        # Implement logic to check if the notice is a PIN-only notice
        # This is a placeholder implementation
        return False

    def process_notice(self, xml_content):
        tree = etree.fromstring(xml_content)

        if self.is_pin_only_notice(tree):
            parts = tree.xpath(
                "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']",
                namespaces=self.namespaces,
            )
            return [self.create_release_for_part(part) for part in parts]
        return [self.create_release(xml_content)]

    def create_release_for_part(self, part):  # noqa: ARG002
        # Implement logic to create a release for an individual part in a PIN-only notice
        # This is a placeholder implementation
        return json.dumps({})

    def reference_previous_publication(self, tree):
        previous_publication = self.get_previous_publication(tree)
        if not previous_publication:
            return None
        if not self.is_pin(
            previous_publication
        ) or self.has_single_procurement_project_lot(previous_publication):
            return None
        if self.is_pin(
            previous_publication
        ) and self.has_multiple_procurement_project_lots(previous_publication):
            return {
                "id": "1",
                "relationship": ["planning"],
                "scheme": self.scheme,
                "identifier": tree.xpath(
                    "string(/*/cbc:ID)", namespaces=self.namespaces
                ),
            }
        return None

    def get_previous_publication(self, tree):  # noqa: ARG002
        # Implement logic to retrieve the previous publication
        # This is a placeholder implementation
        return None

    def is_pin(self, publication):  # noqa: ARG002
        # Implement logic to check if the publication is a PIN
        # This is a placeholder implementation
        return False

    def has_single_procurement_project_lot(self, publication):
        return (
            len(
                publication.xpath(
                    "/*/cac:ProcurementProjectLot", namespaces=self.namespaces
                )
            )
            == 1
        )

    def has_multiple_procurement_project_lots(self, publication):
        return (
            len(
                publication.xpath(
                    "/*/cac:ProcurementProjectLot", namespaces=self.namespaces
                )
            )
            > 1
        )

    @property
    def namespaces(self):
        return {
            "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
            "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
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
