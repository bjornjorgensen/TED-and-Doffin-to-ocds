# converters/BT_536_Part.py

import logging
from lxml import etree
from utils.date_utils import StartDate

logger = logging.getLogger(__name__)

def parse_part_contract_start_date(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    result = {"tender": {}}

    start_date = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cac:PlannedPeriod/cbc:StartDate/text()", namespaces=namespaces)
    
    if start_date:
        iso_date = StartDate(start_date[0])
        result["tender"]["contractPeriod"] = {
            "startDate": iso_date
        }

    return result if result["tender"] else None

def merge_part_contract_start_date(release_json, part_contract_start_date_data):
    if not part_contract_start_date_data:
        logger.warning("No Part Contract Start Date data to merge")
        return

    tender = release_json.setdefault("tender", {})
    
    if "contractPeriod" in part_contract_start_date_data["tender"]:
        tender.setdefault("contractPeriod", {}).update(part_contract_start_date_data["tender"]["contractPeriod"])
        logger.info("Merged Part Contract Start Date data")
    else:
        logger.info("No Part Contract Start Date data to merge")