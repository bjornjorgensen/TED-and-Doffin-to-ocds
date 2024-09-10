# converters/BT_805_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

GPP_CRITERIA_MAPPING = {
    "eu": "euGPPCriteria",
    "national": "nationalGPPCriteria",
    "other": "otherGPPCriteria",
}


def parse_green_procurement_criteria(xml_content):
    """
    Parse the XML content to extract the green procurement criteria for each lot.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed green procurement criteria data.
        None: If no relevant data is found.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    result = {"tender": {"lots": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces
    )
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        gpp_criteria = lot.xpath(
            "cac:ProcurementProject/cac:ProcurementAdditionalType[cbc:ProcurementTypeCode/@listName='gpp-criteria']/cbc:ProcurementTypeCode/text()",
            namespaces=namespaces,
        )

        lot_data = {"id": lot_id, "hasSustainability": False, "sustainability": []}

        for criterion in gpp_criteria:
            if criterion != "none" and criterion in GPP_CRITERIA_MAPPING:
                lot_data["hasSustainability"] = True
                lot_data["sustainability"].append(
                    {"strategies": [GPP_CRITERIA_MAPPING[criterion]]}
                )

        if lot_data["hasSustainability"]:
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_green_procurement_criteria(release_json, green_procurement_criteria_data):
    """
    Merge the parsed green procurement criteria data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        green_procurement_criteria_data (dict): The parsed green procurement criteria data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not green_procurement_criteria_data:
        logger.warning("No green procurement criteria data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in green_procurement_criteria_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]), None
        )
        if existing_lot:
            existing_lot["hasSustainability"] = new_lot["hasSustainability"]
            existing_sustainability = existing_lot.setdefault("sustainability", [])
            for new_sustainability in new_lot["sustainability"]:
                existing_sustainability.append(new_sustainability)
        else:
            existing_lots.append(new_lot)

    # Remove lots with no sustainability criteria
    existing_lots[:] = [
        lot for lot in existing_lots if lot.get("hasSustainability", False)
    ]

    logger.info(
        f"Merged green procurement criteria data for {len(green_procurement_criteria_data['tender']['lots'])} lots"
    )
