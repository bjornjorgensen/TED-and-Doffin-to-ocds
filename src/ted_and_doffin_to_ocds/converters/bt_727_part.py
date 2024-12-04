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


def parse_part_place_performance(xml_content: str | bytes) -> dict | None:
    """
    Parse BT-727: Other restrictions on the place of performance.

    This field maps to the same Address objects as created for BT-728-Part,
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
        Returns None if no data found or on error.
    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")

        root = etree.fromstring(xml_content)
        result = {"tender": {"deliveryLocations": []}}

        region_elements = root.xpath(
            "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']"
            "/cac:ProcurementProject/cac:RealizedLocation"
            "/cac:Address/cbc:Region",
            namespaces=NAMESPACES,
        )

        for region_elem in region_elements:
            clean_code = region_elem.text.strip()
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


def merge_part_place_performance(
    release_json: dict, part_place_data: dict | None
) -> None:
    """
    Merge place of performance data into the release JSON.

    Updates or adds delivery locations in the tender section.
    Handles concatenation of multiple location descriptions if needed.

    Args:
        release_json: Main OCDS release JSON to update
        part_place_data: Place of performance data to merge, can be None

    Note:
        - Updates release_json in-place
        - Creates tender.deliveryLocations if needed
        - Avoids duplicate locations
    """
    if not part_place_data:
        logger.warning("No procurement part place of performance data to merge")
        return

    tender = release_json.setdefault("tender", {})
    tender.setdefault("deliveryLocations", [])

    for new_location in part_place_data["tender"]["deliveryLocations"]:
        if new_location not in tender["deliveryLocations"]:
            tender["deliveryLocations"].append(new_location)

    logger.info(
        "Merged place of performance data for %d locations",
        len(part_place_data["tender"]["deliveryLocations"]),
    )
