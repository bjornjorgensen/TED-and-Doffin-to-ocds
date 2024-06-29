# converters/BT_735_CVD_Contract_Type.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

CVD_CONTRACT_TYPE_LABELS = {
    "oth-serv-contr": "Other service contract",
    "pass-tran-serv": "Passenger road transport services",
    "veh-acq": "Vehicle purchase, lease or rent"
}

def parse_cvd_contract_type(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    result = {
        'tender': {'lots': []},
        'awards': []
    }

    # Process Lots (BT-735-Lot)
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lot_elements:
        lot_id_elements = lot.xpath("cbc:ID/text()", namespaces=namespaces)
        if not lot_id_elements:
            logger.warning("Lot ID not found for a ProcurementProjectLot")
            continue
        lot_id = lot_id_elements[0]
        
        contract_type = lot.xpath(".//efac:StrategicProcurementInformation/efbc:ProcurementCategoryCode[@listName='cvd-contract-type']/text()", namespaces=namespaces)
        if contract_type:
            contract_type_code = contract_type[0]
            result['tender']['lots'].append({
                'id': lot_id,
                'additionalClassifications': [{
                    'id': contract_type_code,
                    'scheme': 'eu-cvd-contract-type',
                    'description': CVD_CONTRACT_TYPE_LABELS.get(contract_type_code, "Unknown")
                }]
            })

    # Process Lot Results (BT-735-LotResult)
    lot_result_elements = root.xpath("//efac:NoticeResult/efac:LotResult", namespaces=namespaces)
    for lot_result in lot_result_elements:
        result_id_elements = lot_result.xpath("cbc:ID/text()", namespaces=namespaces)
        if not result_id_elements:
            logger.warning("Result ID not found for a LotResult")
            continue
        result_id = result_id_elements[0]
        
        lot_id_elements = lot_result.xpath("efac:TenderLot/cbc:ID/text()", namespaces=namespaces)
        if not lot_id_elements:
            logger.warning(f"Lot ID not found for LotResult {result_id}")
            continue
        lot_id = lot_id_elements[0]
        
        contract_type = lot_result.xpath(".//efac:StrategicProcurementInformation/efbc:ProcurementCategoryCode[@listName='cvd-contract-type']/text()", namespaces=namespaces)
        if contract_type:
            contract_type_code = contract_type[0]
            award = {
                'id': result_id,
                'items': [{
                    'id': '1',
                    'additionalClassifications': [{
                        'id': contract_type_code,
                        'scheme': 'eu-cvd-contract-type',
                        'description': CVD_CONTRACT_TYPE_LABELS.get(contract_type_code, "Unknown")
                    }]
                }]
            }
            result['awards'].append(award)
            
            # Add lot information if it doesn't exist
            if not any(lot['id'] == lot_id for lot in result['tender']['lots']):
                result['tender']['lots'].append({
                    'id': lot_id
                })

    return result if (result['tender']['lots'] or result['awards']) else None

def merge_cvd_contract_type(release_json, cvd_contract_type_data):
    if not cvd_contract_type_data:
        logger.warning("No CVD Contract Type data to merge")
        return

    # Merge Lot data
    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])
    for new_lot in cvd_contract_type_data['tender']['lots']:
        existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_classifications = existing_lot.setdefault("additionalClassifications", [])
            existing_classifications.extend(new_lot["additionalClassifications"])
        else:
            existing_lots.append(new_lot)

    # Merge Award data
    existing_awards = release_json.setdefault("awards", [])
    for new_award in cvd_contract_type_data['awards']:
        existing_award = next((award for award in existing_awards if award["id"] == new_award["id"]), None)
        if existing_award:
            existing_items = existing_award.setdefault("items", [])
            for new_item in new_award["items"]:
                existing_item = next((item for item in existing_items if item["id"] == new_item["id"]), None)
                if existing_item:
                    existing_classifications = existing_item.setdefault("additionalClassifications", [])
                    existing_classifications.extend(new_item["additionalClassifications"])
                else:
                    existing_items.append(new_item)
        else:
            existing_awards.append(new_award)

    logger.info(f"Merged CVD Contract Type for {len(cvd_contract_type_data['tender']['lots'])} lots and {len(cvd_contract_type_data['awards'])} awards")