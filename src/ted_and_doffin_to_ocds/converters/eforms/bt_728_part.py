# converters/bt_728_part.py

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


def parse_part_place_performance_additional(
    xml_content: str | bytes,
) -> dict | None:
    """Parse BT-728: Additional information about place of performance.

    This field maps to the same Address objects as created for BT-727-Part,
    BT-5121-Part, BT-5131-Part, BT-5071-Part, BT-5101-Part and BT-5141-Part.

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
        Returns None if no relevant data found or on error

    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")

        root = etree.fromstring(xml_content)
        result = {"tender": {"deliveryLocations": []}}

        locations = root.xpath(
            "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']"
            "/cac:ProcurementProject/cac:RealizedLocation",
            namespaces=NAMESPACES,
        )

        for location in locations:
            description = location.xpath(
                "string(cbc:Description)", namespaces=NAMESPACES
            )
            if description.strip():
                result["tender"]["deliveryLocations"].append(
                    {"description": description.strip()}
                )
                logger.info(
                    "Found additional place description: %s", description.strip()
                )

        return result if result["tender"]["deliveryLocations"] else None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing additional place of performance")
        return None


def merge_part_place_performance_additional(
    release_json: dict, additional_data: dict | None
) -> None:
    """Merge additional place of performance data into the release JSON.

    Updates or adds delivery locations to tender section, concatenating descriptions
    if locations already exist.

    Args:
        release_json: Main OCDS release JSON to update
        additional_data: Additional place performance data to merge, can be None

    Note:
        - Updates release_json in-place
        - Creates tender.deliveryLocations if needed
        - Concatenates descriptions for existing locations

    """
    if not additional_data:
        return

    tender = release_json.setdefault("tender", {})
    locations = tender.setdefault("deliveryLocations", [])

    for new_location in additional_data["tender"]["deliveryLocations"]:
        # Check if there's an existing location to update
        existing = next((loc for loc in locations if loc.get("description")), None)

        if existing:
            # Concatenate the description
            existing["description"] = (
                f"{existing['description']}; {new_location['description']}"
            )
        else:
            # Add as new location
            locations.append(new_location)

    logger.info(
        "Merged additional place of performance data for %d locations",
        len(additional_data["tender"]["deliveryLocations"]),
    )
