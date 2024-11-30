# converters/bt_71_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_reserved_participation(xml_content):
    """
    Parse the XML content to extract reserved participation information for each lot.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed reserved participation data in the format:
              {
                  "tender": {
                      "lots": [
                          {
                              "id": "lot_id",
                              "otherRequirements": {
                                  "reservedparticipation": ["participation_type"]
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
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    result = {"tender": {"lots": []}}

    xpath_query = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']"
    lots = root.xpath(xpath_query, namespaces=namespaces)

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]

        xpath_reserved = "cac:TenderingTerms/cac:TendererQualificationRequest[not(cbc:companyLegalFormCode)][not(cac:SpecificTendererRequirement/cbc:TendererRequirementTypeCode[@listName='missing-info-submission'])]/cac:SpecificTendererRequirement[cbc:TendererRequirementTypeCode/@listName='reserved-procurement']/cbc:TendererRequirementTypeCode/text()"
        reserved_code = lot.xpath(xpath_reserved, namespaces=namespaces)

        if reserved_code:
            reserved_type = None
            if reserved_code[0] == "res-pub-ser":
                reserved_type = "publicServiceMissionorganization"
            elif reserved_code[0] == "res-ws":
                reserved_type = "shelteredWorkshop"

            if reserved_type:
                result["tender"]["lots"].append(
                    {
                        "id": lot_id,
                        "otherRequirements": {"reservedparticipation": [reserved_type]},
                    },
                )

    return result if result["tender"]["lots"] else None


def merge_reserved_participation(release_json, reserved_participation_data) -> None:
    """
    Merge the parsed reserved participation data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        reserved_participation_data (dict): The parsed reserved participation data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not reserved_participation_data:
        logger.warning("No reserved participation data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in reserved_participation_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("otherRequirements", {}).update(
                new_lot["otherRequirements"],
            )
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged reserved participation data for %d lots",
        len(reserved_participation_data["tender"]["lots"]),
    )
