"""Converter for BT-735-LotResult: CVD contract type information for awarded lots.

This module handles the extraction and mapping of Clean Vehicle Directive (CVD)
contract type information from eForms LotResult elements to OCDS award items.
"""

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

CVD_CONTRACT_TYPE_LABELS = {
    "oth-serv-contr": "Other service contract",
    "pass-tran-serv": "Passenger road transport services",
    "veh-acq": "Vehicle purchase, lease or rent",
}


def parse_cvd_contract_type_lotresult(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the CVD contract type for each LotResult into award items.

    This function extracts the contract type according to table 1 CVD from LotResult
    elements and maps them to items in the awards array. Each item gets an incrementally
    assigned ID and the CVD contract type as an additional classification.

    Args:
        xml_content (str | bytes): The XML content to parse.

    Returns:
        dict | None: A dictionary containing award items with CVD classifications:
            {
                "awards": [
                    {
                        "id": str,  # LotResult ID
                        "items": [
                            {
                                "id": str,  # Incremental item ID
                                "additionalClassifications": [
                                    {
                                        "id": str,  # CVD contract type code
                                        "scheme": "eu-cvd-contract-type",
                                        "description": str  # Human readable description
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
            Returns None if no relevant data is found.

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
        namespaces = {
            "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
            "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
            "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
            "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
            "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
        }

        result = {"awards": []}
        lot_results = root.xpath("//efac:LotResult", namespaces=namespaces)

        for lot_result in lot_results:
            try:
                lot_result_ids = lot_result.xpath(
                    "cbc:ID/text()", namespaces=namespaces
                )
                if not lot_result_ids:
                    logger.warning("Skipping lot result without ID")
                    continue

                lot_result_id = lot_result_ids[0]
                cvd_code = lot_result.xpath(
                    "efac:StrategicProcurement/efac:StrategicProcurementInformation/efbc:ProcurementCategoryCode[@listName='cvd-contract-type']/text()",
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
                                            cvd_code, "Unknown CVD contract type"
                                        ),
                                    }
                                ],
                            }
                        ],
                    }
                    result["awards"].append(award_data)

            except (IndexError, AttributeError) as e:
                logger.warning("Error processing lot result: %s", e)
                continue

        return result if result["awards"] else None

    except Exception:
        logger.exception("Error parsing CVD contract type from lot results")
        return None


def merge_cvd_contract_type_lotresult(
    release_json: dict,
    cvd_contract_type_data: dict[str, list[dict[str, str | list[dict[str, str]]]]]
    | None,
) -> None:
    """Merge CVD contract type data into award items in the OCDS release.

    For each LotResult, adds or updates items in the corresponding award with CVD
    contract type information according to Table 1 of the Clean Vehicle Directive.

    Args:
        release_json (dict): The main OCDS release JSON to be updated
        cvd_contract_type_data (dict | None): Award items with CVD contract type data

    Returns:
        None: The function updates the release_json in-place

    """
    if not cvd_contract_type_data:
        logger.warning("No CVD contract type data for LotResults to merge")
        return

    existing_awards = release_json.setdefault("awards", [])

    for new_award in cvd_contract_type_data["awards"]:
        existing_award = next(
            (award for award in existing_awards if award["id"] == new_award["id"]), None
        )
        if existing_award:
            existing_items = existing_award.setdefault("items", [])
            if existing_items:
                existing_item = existing_items[0]
                existing_classifications = existing_item.setdefault(
                    "additionalClassifications", []
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
