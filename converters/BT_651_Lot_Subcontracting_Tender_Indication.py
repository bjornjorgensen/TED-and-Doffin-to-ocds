# converters/BT_651_Lot_Subcontracting_Tender_Indication.py
from lxml import etree

def parse_subcontracting_tender_indication(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    result = {}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        subcontracting_codes = lot.xpath(".//efac:TenderSubcontractingRequirements/efbc:TenderSubcontractingRequirementsCode[@listName='subcontracting-indication']/text()", namespaces=namespaces)
        
        if subcontracting_codes:
            result[lot_id] = subcontracting_codes

    return result

def merge_subcontracting_tender_indication(release_json, subcontracting_data):
    if subcontracting_data:
        tender = release_json.setdefault("tender", {})
        lots = tender.setdefault("lots", [])

        for lot_id, clauses in subcontracting_data.items():
            lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
            if not lot:
                lot = {"id": lot_id}
                lots.append(lot)
            
            submission_terms = lot.setdefault("submissionTerms", {})
            subcontracting_clauses = submission_terms.setdefault("subcontractingClauses", [])
            
            for clause in clauses:
                if clause not in subcontracting_clauses:
                    subcontracting_clauses.append(clause)

    return release_json