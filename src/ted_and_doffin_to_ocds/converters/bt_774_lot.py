# converters/bt_774_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

ENVIRONMENTAL_IMPACT_MAPPING = {
    "biodiv-eco": "environmental.biodiversityProtectionRestoration",
    "circ-econ": "environmental.circularEconomy",
    "clim-adapt": "environmental.climateChangeAdaptation",
    "clim-mitig": "environmental.climateChangeMitigation",
    "other": "environmental",
    "pollu-prev": "environmental.pollutionPrevention",
    "water-mar": "environmental.waterResources",
}


def parse_green_procurement(xml_content: str | bytes) -> dict | None:
    """
    Parse the XML content to extract the green procurement information for each lot.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse.

    Returns:
        Optional[Dict]: A dictionary containing the parsed green procurement data in the format:
              {
                  "tender": {
                      "lots": [
                          {
                              "id": "lot_id",
                              "hasSustainability": true,
                              "sustainability": [
                                  {
                                      "goal": "environmental goal"
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
        environmental_impacts: list[str] = lot.xpath(
            "cac:ProcurementProject/cac:ProcurementAdditionalType[cbc:ProcurementTypeCode/@listName='environmental-impact']/cbc:ProcurementTypeCode/text()",
            namespaces=namespaces,
        )

        if environmental_impacts:
            lot_data = {"id": lot_id, "hasSustainability": True, "sustainability": []}

            for impact in environmental_impacts:
                goal = ENVIRONMENTAL_IMPACT_MAPPING.get(impact, "environmental")
                lot_data["sustainability"].append({"goal": goal})

            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_green_procurement(
    release_json: dict,
    green_procurement_data: dict | None,
) -> None:
    """
    Merge the parsed green procurement data into the main OCDS release JSON.

    Args:
        release_json (Dict): The main OCDS release JSON to be updated.
        green_procurement_data (Optional[Dict]): The parsed green procurement data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not green_procurement_data:
        logger.warning("No green procurement data to merge")
        return

    tender: dict = release_json.setdefault("tender", {})
    existing_lots: list[dict] = tender.setdefault("lots", [])

    for new_lot in green_procurement_data["tender"]["lots"]:
        existing_lot: dict | None = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot["hasSustainability"] = new_lot["hasSustainability"]
            existing_lot["sustainability"] = new_lot["sustainability"]
        else:
            existing_lots.append(new_lot)

    logger.info(
        f"Merged green procurement data for {len(green_procurement_data['tender']['lots'])} lots",
    )
