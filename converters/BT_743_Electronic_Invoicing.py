from lxml import etree

def parse_electronic_invoicing(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = []

    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        einvoicing = lot.xpath(".//cac:ContractExecutionRequirement[cbc:ExecutionRequirementCode/@listName='einvoicing']/cbc:ExecutionRequirementCode/text()", namespaces=namespaces)
        
        if einvoicing:
            result.append({
                'id': lot_id,
                'einvoicing': einvoicing[0]
            })

    return result

def merge_electronic_invoicing(release_json, einvoicing_data):
    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    einvoicing_mapping = {
        'required': 'Required',
        'allowed': 'Allowed',
        'notAllowed': 'Not allowed'
    }

    for einvoicing in einvoicing_data:
        lot = next((l for l in lots if l.get('id') == einvoicing['id']), None)
        if not lot:
            lot = {'id': einvoicing['id']}
            lots.append(lot)

        contract_terms = lot.setdefault('contractTerms', {})
        contract_terms['electronicInvoicingPolicy'] = einvoicing_mapping.get(einvoicing['einvoicing'], einvoicing['einvoicing'])

    return release_json