# converters/BT_777_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_strategic_procurement_description(xml_content):
    """
    Parse the XML content to extract the Strategic Procurement Description for each lot.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed data in the format:
              {
                  "tender": {
                      "lots": [
                          {
                              "id": "lot_id",
                              "sustainability": [
                                  {
                                      "description": "strategic_procurement_description"
                                  }
                              ]
                          }
                      ]
                  }
              }
        None: If no relevant data is found.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    result = {"tender": {"lots": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        descriptions = lot.xpath(
            "cac:ProcurementProject/cac:ProcurementAdditionalType[cbc:ProcurementTypeCode/@listName='strategic-procurement']/cbc:ProcurementType/text()",
            namespaces=namespaces,
        )

        if descriptions:
            lot_data = {
                "id": lot_id,
                "sustainability": [{"description": desc} for desc in descriptions],
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_strategic_procurement_description(release_json, strategic_procurement_data):
    """
    Merge the parsed Strategic Procurement Description data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        strategic_procurement_data (dict): The parsed Strategic Procurement Description data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not strategic_procurement_data:
        logger.warning("No Strategic Procurement Description data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in strategic_procurement_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_sustainability = existing_lot.setdefault("sustainability", [])
            existing_sustainability.extend(new_lot["sustainability"])
        else:
            existing_lots.append(new_lot)

    logger.info(
        f"Merged Strategic Procurement Description data for {len(strategic_procurement_data['tender']['lots'])} lots",
    )
