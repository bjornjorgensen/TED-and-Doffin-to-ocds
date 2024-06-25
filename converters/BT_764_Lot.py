# converters/BT_764_Lot.py

from lxml import etree

def parse_submission_electronic_catalogue(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    policy_mapping = {
        'required': 'required',
        'allowed': 'allowed',
        'not-allowed': 'notAllowed'
    }

    result = {}
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)

    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        ecatalog_submission = lot.xpath("cac:TenderingTerms/cac:ContractExecutionRequirement[cbc:ExecutionRequirementCode/@listName='ecatalog-submission']/cbc:ExecutionRequirementCode/text()", namespaces=namespaces)

        if ecatalog_submission:
            policy = policy_mapping.get(ecatalog_submission[0])
            if policy:
                result[lot_id] = policy

    return result

def merge_submission_electronic_catalogue(release_json, ecatalog_data):
    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for lot_id, ecatalog_policy in ecatalog_data.items():
        lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
        if not lot:
            lot = {"id": lot_id}
            lots.append(lot)

        submission_terms = lot.setdefault("submissionTerms", {})
        submission_terms["electronicCatalogPolicy"] = ecatalog_policy

    return release_json