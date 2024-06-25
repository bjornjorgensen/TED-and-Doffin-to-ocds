from lxml import etree

def parse_submission_electronic_signature(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = []

    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        esignature = lot.xpath(".//cac:ContractExecutionRequirement[cbc:ExecutionRequirementCode/@listName='esignature-submission']/cbc:ExecutionRequirementCode/text()", namespaces=namespaces)
        
        if esignature:
            result.append({
                'id': lot_id,
                'esignature_required': esignature[0].lower() == 'true'
            })

    return result

def merge_submission_electronic_signature(release_json, esignature_data):
    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for esignature in esignature_data:
        lot = next((l for l in lots if l.get('id') == esignature['id']), None)
        if not lot:
            lot = {'id': esignature['id']}
            lots.append(lot)

        submission_terms = lot.setdefault('submissionTerms', {})
        submission_terms['advancedElectronicSignatureRequired'] = esignature['esignature_required']

    return release_json