# converters/bt_775_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)

SOCIAL_OBJECTIVE_MAPPING = {
    "acc-all": "social.accessibility",
    "et-eq": "social.ethnicEquality",
    "gen-eq": "social.genderEquality",
    "hum-right": "social.humanRightsInSupplyChain",
    "opp": "social.disadvantagedEmploymentOpportunities",
    "other": "social",
    "work-cond": "social.laborRightsPromotion",
}

SUSTAINABILITY_STRATEGIES = [
    "awardCriteria",
    "contractPerformanceConditions",
    "selectionCriteria",
    "technicalSpecifications",
]


def parse_social_procurement(xml_content: str | bytes) -> dict | None:
    """Parse the XML content to extract the social procurement information for each lot.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse.

    Returns:
        Optional[Dict]: A dictionary containing the parsed social procurement data in the format:
              {
                  "tender": {
                      "lots": [
                          {
                              "id": "lot_id",
                              "hasSustainability": true,
                              "sustainability": [
                                  {
                                      "goal": "social goal",
                                      "strategies": ["strategy1", "strategy2", ...]
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
        social_objectives: list[str] = lot.xpath(
            "cac:ProcurementProject/cac:ProcurementAdditionalType[cbc:ProcurementTypeCode/@listName='social-objective']/cbc:ProcurementTypeCode/text()",
            namespaces=namespaces,
        )

        if social_objectives:
            lot_data = {"id": lot_id, "hasSustainability": True, "sustainability": []}

            for objective in social_objectives:
                goal = SOCIAL_OBJECTIVE_MAPPING.get(objective, "social")
                lot_data["sustainability"].append(
                    {"goal": goal, "strategies": SUSTAINABILITY_STRATEGIES},
                )

            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_social_procurement(
    release_json: dict,
    social_procurement_data: dict | None,
) -> None:
    """Merge the parsed social procurement data into the main OCDS release JSON.

    Args:
        release_json (Dict): The main OCDS release JSON to be updated.
        social_procurement_data (Optional[Dict]): The parsed social procurement data to be merged.

    Returns:
        None: The function updates the release_json in-place.

    """
    if not social_procurement_data:
        logger.warning("No social procurement data to merge")
        return

    tender: dict = release_json.setdefault("tender", {})
    existing_lots: list[dict] = tender.setdefault("lots", [])

    for new_lot in social_procurement_data["tender"]["lots"]:
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
        "Merged social procurement data for %d lots",
        len(social_procurement_data["tender"]["lots"]),
    )
