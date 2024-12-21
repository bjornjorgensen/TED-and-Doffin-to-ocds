"""Converter for BT-735-Lot: CVD contract type information.

This module handles the extraction and mapping of Clean Vehicle Directive (CVD)
contract type information from eForms notices to OCDS format.
"""

import logging

from lxml import etree

logger = logging.getLogger(__name__)

# Mapping of CVD (Clean Vehicle Directive) contract type codes to descriptions
CVD_CONTRACT_TYPE_LABELS = {
    "oth-serv-contr": "Other service contract",
    "pass-tran-serv": "Passenger road transport services",
    "veh-acq": "Vehicle purchase, lease or rent",
}


def parse_cvd_contract_type(
    xml_content: str | bytes,
) -> dict[str, dict[str, list[dict[str, str]]]] | None:
    """Parse the CVD (Clean Vehicle Directive) contract type for each lot.

    This function extracts the contract type according to table 1 CVD, which includes
    purchase, lease, rent, hired-purchase, public service contracts and service contracts.

    Args:
        xml_content (str or bytes): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed CVD contract type data for lots in format:
            {
                "tender": {
                    "lots": [
                        {
                            "id": str,
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

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        cvd_code = lot.xpath(
            ".//cac:TenderingTerms/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:StrategicProcurement/efac:StrategicProcurementInformation/efbc:ProcurementCategoryCode[@listName='cvd-contract-type']/text()",
            namespaces=namespaces,
        )

        if cvd_code:
            cvd_code = cvd_code[0]
            lot_data = {
                "id": lot_id,
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
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_cvd_contract_type(
    release_json: dict,
    cvd_contract_type_data: dict[str, dict[str, list[dict[str, str]]]] | None,
) -> None:
    """Merge the CVD (Clean Vehicle Directive) contract type data into the OCDS release.

    Adds or updates the additionalClassifications array in each lot with CVD contract
    type information according to Table 1 of the Clean Vehicle Directive.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        cvd_contract_type_data (dict): The parsed CVD contract type data for lots.

    Returns:
        None: The function updates the release_json in-place.

    """
    if not cvd_contract_type_data:
        logger.warning("No CVD contract type data for lots to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in cvd_contract_type_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_classifications = existing_lot.setdefault(
                "additionalClassifications",
                [],
            )
            new_classification = new_lot["additionalClassifications"][0]
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
            existing_lots.append(new_lot)

    logger.info(
        "Merged CVD contract type data for %d lots",
        len(cvd_contract_type_data["tender"]["lots"]),
    )
