# converters/BT_735_CVD_Contract_Type.py
from lxml import etree

CVD_CONTRACT_TYPE_MAPPING = {
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
        'lots': {},
        'lotResults': {}
    }

    # Process Lots
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        contract_type = lot.xpath(".//efac:StrategicProcurementInformation/efbc:ProcurementCategoryCode[@listName='cvd-contract-type']/text()", namespaces=namespaces)
        if contract_type:
            result['lots'][lot_id] = contract_type[0]

    # Process Lot Results
    lot_result_elements = root.xpath("//efac:NoticeResult/efac:LotResult", namespaces=namespaces)
    for lot_result in lot_result_elements:
        result_id = lot_result.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        contract_type = lot_result.xpath(".//efac:StrategicProcurementInformation/efbc:ProcurementCategoryCode[@listName='cvd-contract-type']/text()", namespaces=namespaces)
        lot_id = lot_result.xpath("efac:TenderLot/cbc:ID/text()", namespaces=namespaces)
        if contract_type and lot_id:
            result['lotResults'][result_id] = {
                'contractType': contract_type[0],
                'relatedLot': lot_id[0]
            }

    return result

def merge_cvd_contract_type(release_json, cvd_contract_type_data):
    if cvd_contract_type_data:
        tender = release_json.setdefault("tender", {})
        awards = release_json.setdefault("awards", [])

        # Merge Lots
        lots = tender.setdefault("lots", [])
        for lot_id, contract_type in cvd_contract_type_data['lots'].items():
            lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
            if not lot:
                lot = {"id": lot_id}
                lots.append(lot)
            additional_classifications = lot.setdefault("additionalClassifications", [])
            additional_classifications.append({
                "id": contract_type,
                "scheme": "eu-cvd-contract-type",
                "description": CVD_CONTRACT_TYPE_MAPPING.get(contract_type, "Unknown contract type")
            })

        # Merge Lot Results
        for result_id, data in cvd_contract_type_data['lotResults'].items():
            award = next((award for award in awards if award.get("id") == result_id), None)
            if not award:
                award = {"id": result_id, "relatedLots": [data['relatedLot']]}
                awards.append(award)
            
            items = award.setdefault("items", [])
            if not items:
                items.append({"id": "1"})
            
            item = items[0]
            additional_classifications = item.setdefault("additionalClassifications", [])
            additional_classifications.append({
                "id": data['contractType'],
                "scheme": "eu-cvd-contract-type",
                "description": CVD_CONTRACT_TYPE_MAPPING.get(data['contractType'], "Unknown contract type")
            })

    return release_json