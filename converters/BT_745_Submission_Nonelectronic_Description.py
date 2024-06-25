from lxml import etree

def parse_submission_nonelectronic_description(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = []

    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        description = lot.xpath(".//cac:TenderingProcess/cac:ProcessJustification[cbc:ProcessReasonCode/@listName='no-esubmission-justification']/cbc:Description/text()", namespaces=namespaces)
        
        if description:
            result.append({
                'id': lot_id,
                'description': description[0]
            })

    return result

def merge_submission_nonelectronic_description(release_json, description_data):
    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for description in description_data:
        lot = next((l for l in lots if l.get('id') == description['id']), None)
        if not lot:
            lot = {'id': description['id']}
            lots.append(lot)

        lot['submissionMethodDetails'] = description['description']

    return release_json