# converters/BT_765_PartFrameworkAgreement.py

import logging
from typing import Optional, Dict
from lxml import etree

logger = logging.getLogger(__name__)


def parse_part_framework_agreement(xml_content: str) -> Optional[Dict]:
    """
    Parse the XML content to extract the Framework Agreement details for the Part.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        Optional[Dict]: A dictionary containing the parsed data if found, None otherwise.
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

    framework_agreement = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingProcess/cac:ContractingSystem[cbc:ContractingSystemTypeCode/@listName='framework-agreement']/cbc:ContractingSystemTypeCode/text()",
        namespaces=namespaces,
    )

    if framework_agreement and framework_agreement[0] != "none":
        mapped_method = method_mapping.get(framework_agreement[0])
        if mapped_method:
            return {
                "tender": {
                    "techniques": {
                        "hasFrameworkAgreement": True,
                        "frameworkAgreement": {"method": mapped_method},
                    }
                }
            }

    return None


def merge_part_framework_agreement(
    release_json: Dict, part_framework_agreement_data: Optional[Dict]
) -> None:
    """
    Merge the parsed Part Framework Agreement data into the main OCDS release JSON.

    Args:
        release_json (Dict): The main OCDS release JSON to be updated.
        part_framework_agreement_data (Optional[Dict]): The parsed Part Framework Agreement data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not part_framework_agreement_data:
        logger.warning("No Part Framework Agreement data to merge")
        return

    tender = release_json.setdefault("tender", {})
    techniques = tender.setdefault("techniques", {})

    techniques.update(part_framework_agreement_data["tender"]["techniques"])

    logger.info("Merged Part Framework Agreement data")
