# converters/BT_765_FrameworkAgreement.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_framework_agreement(xml_content: str) -> dict[str, dict] | None:
    """
    Parse the XML content to extract the Framework Agreement details for each lot.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        Optional[Dict[str, Dict]]: A dictionary mapping lot IDs to their framework agreement data if found, None otherwise.
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

    method_mapping = {
        "fa-mix": "withAndWithoutReopeningCompetition",
        "fa-w-rc": "withReopeningCompetition",
        "fa-wo-rc": "withoutReopeningCompetition",
    }

    lots_data = {}
    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        framework_agreement = lot.xpath(
            "cac:TenderingProcess/cac:ContractingSystem[cbc:ContractingSystemTypeCode/@listName='framework-agreement']/cbc:ContractingSystemTypeCode/text()",
            namespaces=namespaces,
        )

        if framework_agreement and framework_agreement[0] in method_mapping:
            mapped_method = method_mapping[framework_agreement[0]]
            lots_data[lot_id] = {
                "techniques": {
                    "hasFrameworkAgreement": True,
                    "frameworkAgreement": {"method": mapped_method},
                },
            }

    return lots_data if lots_data else None


def merge_framework_agreement(
    release_json: dict, framework_agreement_data: dict[str, dict] | None,
) -> None:
    """
    Merge the parsed Framework Agreement data into the main OCDS release JSON.

    Args:
        release_json (Dict): The main OCDS release JSON to be updated.
        framework_agreement_data (Optional[Dict[str, Dict]]): The parsed Framework Agreement data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not framework_agreement_data:
        logger.warning("No Framework Agreement data to merge")
        return

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    updated_lots = []
    for lot in lots:
        lot_id = lot["id"]
        if lot_id in framework_agreement_data:
            lot.update(framework_agreement_data[lot_id])
            updated_lots.append(lot)

    tender["lots"] = updated_lots

    logger.info(f"Merged Framework Agreement data for {len(updated_lots)} lots")
