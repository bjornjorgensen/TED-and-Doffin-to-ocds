# converters/bt_805_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}

GPP_CRITERIA_MAPPING = {
    "eu": "euGPPCriteria",
    "national": "nationalGPPCriteria",
    "other": "otherGPPCriteria",
}


def parse_gpp_criteria(xml_content: str | bytes) -> dict | None:
    """Parse BT-805: Green public procurement criteria for lots.

    Extracts information about established GPP criteria usage, including national,
    Union or other level criteria.

    Args:
        xml_content: XML content to parse, either as string or bytes

    Returns:
        Optional[Dict]: Parsed data in format:
            {
                "tender": {
                    "lots": [
                        {
                            "id": str,
                            "hasSustainability": bool,
                            "sustainability": [
                                {
                                    "strategies": [str]  # from GPP_CRITERIA_MAPPING
                                }
                            ]
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
        result = {"tender": {"lots": []}}

        lots = root.xpath(
            "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
            namespaces=NAMESPACES,
        )

        for lot in lots:
            lot_id = lot.xpath("cbc:ID/text()", namespaces=NAMESPACES)[0]
            criteria = lot.xpath(
                "cac:ProcurementProject/cac:ProcurementAdditionalType"
                "/cbc:ProcurementTypeCode[@listName='gpp-criteria']/text()",
                namespaces=NAMESPACES,
            )

            lot_data = {"id": lot_id, "hasSustainability": False, "sustainability": []}

            for criterion in criteria:
                if criterion != "none":
                    strategy = GPP_CRITERIA_MAPPING.get(criterion)
                    if strategy:
                        lot_data["hasSustainability"] = True
                        lot_data["sustainability"].append({"strategies": [strategy]})
                        logger.info(
                            "Found GPP criterion %s for lot %s", strategy, lot_id
                        )
                    else:
                        logger.warning("Unknown GPP criterion code: %s", criterion)

            if lot_data["hasSustainability"]:
                result["tender"]["lots"].append(lot_data)

        return result if result["tender"]["lots"] else None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing GPP criteria")
        return None


def merge_gpp_criteria(release_json: dict, gpp_data: dict | None) -> None:
    """Merge GPP criteria data into the release JSON.

    Updates or adds sustainability information to lots.

    Args:
        release_json: Main OCDS release JSON to update
        gpp_data: GPP criteria data to merge, can be None

    Note:
        - Updates release_json in-place
        - Creates tender.lots array if needed
        - Updates existing lots' sustainability info
        - Removes lots without sustainability criteria

    """
    if not gpp_data:
        logger.warning("No GPP criteria data to merge")
        return

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for new_lot in gpp_data["tender"]["lots"]:
        existing_lot = next((lot for lot in lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_lot["hasSustainability"] = new_lot["hasSustainability"]
            sustainability = existing_lot.setdefault("sustainability", [])
            sustainability.extend(new_lot["sustainability"])
        else:
            lots.append(new_lot)

    # Clean up lots without sustainability
    lots[:] = [lot for lot in lots if lot.get("hasSustainability", False)]

    logger.info("Merged GPP criteria data for %d lots", len(gpp_data["tender"]["lots"]))
