# converters/bt_735_LotResult.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

CVD_CONTRACT_TYPE_LABELS = {
    "oth-serv-contr": "Other service contract",
    "pass-tran-serv": "Passenger road transport services",
    "veh-acq": "Vehicle purchase, lease or rent",
}


def parse_cvd_contract_type_lotresult(xml_content):
    """
    Parse the XML content to extract the CVD contract type for each LotResult.

    Args:
        xml_content (str or bytes): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed CVD contract type data for LotResults.
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

    result = {"awards": []}

    lot_results = root.xpath("//efac:LotResult", namespaces=namespaces)

    for lot_result in lot_results:
        lot_result_id = lot_result.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        cvd_code = lot_result.xpath(
            ".//efac:StrategicProcurementInformation/efbc:ProcurementCategoryCode[@listName='cvd-contract-type']/text()",
            namespaces=namespaces,
        )

        if cvd_code:
            cvd_code = cvd_code[0]
            award_data = {
                "id": lot_result_id,
                "items": [
                    {
                        "id": "1",
                        "additionalClassifications": [
                            {
                                "id": cvd_code,
                                "scheme": "eu-cvd-contract-type",
                                "description": CVD_CONTRACT_TYPE_LABELS.get(
                                    cvd_code,
                                    "Unknown CVD contract type",
                                ),
                            },
                        ],
                    },
                ],
            }
            result["awards"].append(award_data)

    return result if result["awards"] else None


def merge_cvd_contract_type_lotresult(release_json, cvd_contract_type_data):
    """
    Merge the parsed CVD contract type data for LotResults into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        cvd_contract_type_data (dict): The parsed CVD contract type data for LotResults to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not cvd_contract_type_data:
        logger.warning("No CVD contract type data for LotResults to merge")
        return

    existing_awards = release_json.setdefault("awards", [])

    for new_award in cvd_contract_type_data["awards"]:
        existing_award = next(
            (award for award in existing_awards if award["id"] == new_award["id"]),
            None,
        )
        if existing_award:
            existing_items = existing_award.setdefault("items", [])
            if existing_items:
                existing_item = existing_items[0]
                existing_classifications = existing_item.setdefault(
                    "additionalClassifications",
                    [],
                )
                new_classification = new_award["items"][0]["additionalClassifications"][
                    0
                ]
                existing_classification = next(
                    (
                        c
                        for c in existing_classifications
                        if c["scheme"] == "eu-cvd-contract-type"
                    ),
                    None,
                )
                if existing_classification:
                    existing_classification.update(new_classification)
                else:
                    existing_classifications.append(new_classification)
            else:
                existing_items.extend(new_award["items"])
        else:
            existing_awards.append(new_award)

    logger.info(
        "Merged CVD contract type data for %d LotResults",
        len(cvd_contract_type_data["awards"]),
    )
