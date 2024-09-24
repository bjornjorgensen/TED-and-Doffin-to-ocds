# converters/bt_776_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

INNOVATIVE_ACQUISITION_MAPPING = {
    "mar-nov": "economic.marketInnovationPromotion",
    "proc-innov": "economic.processInnovation",
    "prod-innov": "economic.productInnovation",
    "rd-act": "economic.researchDevelopmentActivities",
}


def parse_procurement_innovation(xml_content: str | bytes) -> dict | None:
    """
    Parse the XML content to extract the procurement of innovation information for each lot.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse.

    Returns:
        Optional[Dict]: A dictionary containing the parsed procurement of innovation data in the format:
              {
                  "tender": {
                      "lots": [
                          {
                              "id": "lot_id",
                              "hasSustainability": true,
                              "sustainability": [
                                  {
                                      "goal": "economic goal"
                                  }
                              ]
                          }
                      ]
                  }
              }
        None: If no relevant data is found.

    Raises:
        etree.XMLSyntaxError: If the input is not valid XML.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    root: etree._Element = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    result: dict[str, dict] = {"tender": {"lots": []}}

    lots: list[etree._Element] = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id: str = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        innovative_acquisitions: list[str] = lot.xpath(
            "cac:ProcurementProject/cac:ProcurementAdditionalType[cbc:ProcurementTypeCode/@listName='innovative-acquisition']/cbc:ProcurementTypeCode/text()",
            namespaces=namespaces,
        )

        if innovative_acquisitions:
            lot_data = {"id": lot_id, "hasSustainability": True, "sustainability": []}

            for acquisition in innovative_acquisitions:
                goal = INNOVATIVE_ACQUISITION_MAPPING.get(acquisition)
                if goal:
                    lot_data["sustainability"].append({"goal": goal})

            if lot_data["sustainability"]:
                result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_procurement_innovation(
    release_json: dict,
    procurement_innovation_data: dict | None,
) -> None:
    """
    Merge the parsed procurement of innovation data into the main OCDS release JSON.

    Args:
        release_json (Dict): The main OCDS release JSON to be updated.
        procurement_innovation_data (Optional[Dict]): The parsed procurement of innovation data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not procurement_innovation_data:
        logger.warning("No procurement of innovation data to merge")
        return

    tender: dict = release_json.setdefault("tender", {})
    existing_lots: list[dict] = tender.setdefault("lots", [])

    for new_lot in procurement_innovation_data["tender"]["lots"]:
        existing_lot: dict | None = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot["hasSustainability"] = new_lot["hasSustainability"]
            if "sustainability" not in existing_lot:
                existing_lot["sustainability"] = []
            existing_lot["sustainability"].extend(new_lot["sustainability"])
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged procurement of innovation data for %d lots",
        len(procurement_innovation_data["tender"]["lots"]),
    )
