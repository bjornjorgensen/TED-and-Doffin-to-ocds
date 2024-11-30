# converters/bt_27_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_lot_estimated_value(xml_content):
    """
    Parse the XML content to extract the estimated value for each lot.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed data in the format:
              {
                  "tender": {
                      "lots": [
                          {
                              "id": "lot_id",
                              "value": {
                                  "amount": float_value,
                                  "currency": "currency_code"
                              }
                          }
                      ]
                  }
              }
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
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        estimated_value = lot.xpath(
            "cac:ProcurementProject/cac:RequestedTenderTotal/cbc:EstimatedOverallContractAmount/text()",
            namespaces=namespaces,
        )
        currency = lot.xpath(
            "cac:ProcurementProject/cac:RequestedTenderTotal/cbc:EstimatedOverallContractAmount/@currencyID",
            namespaces=namespaces,
        )

        if estimated_value and currency:
            lot_data = {
                "id": lot_id,
                "value": {"amount": float(estimated_value[0]), "currency": currency[0]},
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_lot_estimated_value(release_json, lot_estimated_value_data) -> None:
    """
    Merge the parsed lot estimated value data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        lot_estimated_value_data (dict): The parsed lot estimated value data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not lot_estimated_value_data:
        logger.warning("No Lot Estimated Value data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in lot_estimated_value_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot["value"] = new_lot["value"]
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged Lot Estimated Value data for %(num_lots)d lots",
        {"num_lots": len(lot_estimated_value_data["tender"]["lots"])},
    )
