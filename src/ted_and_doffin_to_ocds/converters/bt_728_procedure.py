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


def parse_procedure_place_performance_additional(
    xml_content: str | bytes,
) -> dict | None:
    """Parse BT-728: Additional information about place of performance.

    This field maps to the same Address objects as created for BT-727-Part,
    BT-5121-Part, BT-5071-Part, BT-727-Part, BT-5101-Part and BT-5141-Part.

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

        descriptions = root.xpath(
            "/*/cac:ProcurementProject/cac:RealizedLocation/cbc:Description/text()",
            namespaces=NAMESPACES,
        )

        for description in descriptions:
            clean_desc = description.strip()
            if clean_desc:
                logger.info("Found additional place description: %s", clean_desc)
                result["tender"]["deliveryLocations"].append(
                    {"description": clean_desc}
                )

        return result if result["tender"]["deliveryLocations"] else None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing additional place performance")
        return None


def merge_procedure_place_performance_additional(
    release_json: dict, place_data: dict | None
) -> None:
    """Merge additional place performance data into the release JSON.

    Updates or adds delivery locations in the tender section, concatenating
    descriptions if locations already exist.

    Args:
        release_json: Main OCDS release JSON to update
        place_data: Additional place performance data to merge, can be None

    Note:
        - Updates release_json in-place
        - Creates tender.deliveryLocations if needed
        - Handles concatenation of descriptions

    """
    if not place_data:
        logger.warning(
            "No procurement procedure additional place performance data to merge"
        )
        return

    tender = release_json.setdefault("tender", {})
    locations = tender.setdefault("deliveryLocations", [])

    for new_location in place_data["tender"]["deliveryLocations"]:
        # Try to find existing location to concatenate description
        existing = next((loc for loc in locations if loc.get("description")), None)

        if existing:
            # Concatenate descriptions
            existing["description"] = (
                f"{existing['description']}; {new_location['description']}"
            )
        else:
            # Add new location
            locations.append(new_location)

    logger.info(
        "Merged additional place performance data for %d locations",
        len(place_data["tender"]["deliveryLocations"]),
    )
