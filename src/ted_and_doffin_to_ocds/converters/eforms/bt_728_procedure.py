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
                    "deliveryAddresses": [
                        {
                            "description": str,
                            "language": str  # Optional, present when languageID is available
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
        result = {"tender": {"deliveryAddresses": []}}

        description_elements = root.xpath(
            "/*/cac:ProcurementProject/cac:RealizedLocation/cbc:Description",
            namespaces=NAMESPACES,
        )

        for element in description_elements:
            description = element.text
            if description:
                clean_desc = description.strip()
                if clean_desc:
                    location_data = {"description": clean_desc}

                    language_id = element.get("languageID")
                    if language_id:
                        location_data["language"] = language_id
                        logger.info(
                            "Found additional place description in language %s: %s",
                            language_id,
                            clean_desc,
                        )
                    else:
                        logger.info(
                            "Found additional place description: %s", clean_desc
                        )

                    result["tender"]["deliveryAddresses"].append(location_data)

        return result if result["tender"]["deliveryAddresses"] else None

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

    Updates or adds delivery addresses in the tender section. Each RealizedLocation
    from the XML becomes a separate entry in the deliveryAddresses array.

    Args:
        release_json: Main OCDS release JSON to update
        place_data: Additional place performance data to merge, can be None

    Note:
        - Updates release_json in-place
        - Creates tender.deliveryAddresses if needed
        - As per eForms guidance, each RealizedLocation maps to an Address object
        - Preserves each description as a separate entry

    """
    if not place_data:
        logger.warning(
            "No procurement procedure additional place performance data to merge"
        )
        return

    tender = release_json.setdefault("tender", {})
    addresses = tender.setdefault("deliveryAddresses", [])

    # Simply append all the new addresses without trying to match existing ones
    for new_address in place_data["tender"]["deliveryAddresses"]:
        addresses.append(new_address)

    logger.info(
        "Added %d additional place performance descriptions",
        len(place_data["tender"]["deliveryAddresses"]),
    )
