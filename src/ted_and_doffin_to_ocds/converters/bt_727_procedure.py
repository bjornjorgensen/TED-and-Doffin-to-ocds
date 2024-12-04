# converters/bt_727_procedure.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
    "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
}

REGION_MAPPING = {
    "anyw": "Anywhere",
    "anyw-cou": "Anywhere in the given country",
    "anyw-eea": "Anywhere in the European Economic Area",
}


def parse_procedure_place_performance(xml_content: str | bytes) -> dict | None:
    """
    Parse BT-727: Other restrictions on the place of performance.

    This field maps to the same Address objects as created for BT-728-Procedure,
    BT-5121-Procedure, BT-5131-Procedure, BT-5071-Procedure, BT-5101-Procedure
    and BT-5141-Procedure.

    Args:
        xml_content: XML content to parse, either as string or bytes

    Returns:
        Optional[Dict]: Parsed data in format:
            {
                "tender": {
                    "deliveryLocations": [
                        {
                            "description": str
                        }
                    ]
                }
            }
        Returns None if no data found or on error.
    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")

        root = etree.fromstring(xml_content)
        result = {"tender": {"deliveryLocations": []}}

        regions = root.xpath(
            "//cac:ProcurementProject/cac:RealizedLocation/cac:Address/cbc:Region/text()",
            namespaces=NAMESPACES,
        )

        for region in regions:
            clean_code = region.strip()
            if clean_code:
                description = REGION_MAPPING.get(clean_code.lower(), clean_code)
                if description:
                    logger.info(
                        "Found region code '%s', mapped to '%s'",
                        clean_code,
                        description,
                    )
                    result["tender"]["deliveryLocations"].append(
                        {"description": description}
                    )

        return result if result["tender"]["deliveryLocations"] else None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing place of performance")
        return None


def merge_procedure_place_performance(
    release_json: dict, procedure_place_data: dict | None
) -> None:
    """
    Merge place of performance data into the release JSON.

    Updates or adds delivery locations in the tender section, handling duplicate
    locations appropriately.

    Args:
        release_json: Main OCDS release JSON to update
        procedure_place_data: Place of performance data to merge, can be None

    Note:
        - Updates release_json in-place
        - Creates tender.deliveryLocations if needed
        - Avoids duplicate locations
    """
    if not procedure_place_data:
        logger.warning("No procurement procedure place of performance data to merge")
        return

    if "tender" not in release_json:
        release_json["tender"] = {}
    if "deliveryLocations" not in release_json["tender"]:
        release_json["tender"]["deliveryLocations"] = []

    for new_location in procedure_place_data["tender"]["deliveryLocations"]:
        existing_location = next(
            (
                loc
                for loc in release_json["tender"]["deliveryLocations"]
                if loc.get("description") == new_location["description"]
            ),
            None,
        )
        if not existing_location:
            release_json["tender"]["deliveryLocations"].append(new_location)

    logger.info(
        "Merged place of performance data for %d locations",
        len(procedure_place_data["tender"]["deliveryLocations"]),
    )
