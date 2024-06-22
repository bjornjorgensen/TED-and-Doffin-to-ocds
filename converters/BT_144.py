from lxml import etree

DECISION_REASON_CODES = {
    "all-rej": "All tenders, requests to participate or projects were withdrawn or found inadmissible",
    "chan-need": "Decision of the buyer, because of a change in needs",
    "ins-fund": "Decision of the buyer, because of insufficient funds",
    "no-rece": "No tenders, requests to participate or projects were received",
    "no-signed": "The highest ranked tenderer(s) refused to sign the contract",
    "none-rej": "No tenders or requests to participate were received or all were rejected",
    "one-admis": "Only one admissible tender, request to participate or project was received",
    "other": "Other",
    "rev-body": "Decision of a review body or another judicial body",
    "rev-buyer": "Decision of the buyer following a tenderer's request to review the award",
    "tch-pr-error": "Decision of the buyer, not following a tenderer's request to review the award, because of technical or procedural errors"
}

def parse_not_awarded_reason(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"awards": []}

    lot_results = root.xpath("//efac:NoticeResult/efac:LotResult", namespaces=namespaces)
    
    for lot_result in lot_results:
        award_id = lot_result.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        lot_id = lot_result.xpath("efac:TenderLot/cbc:ID/text()", namespaces=namespaces)[0]
        decision_reason_code = lot_result.xpath("efac:DecisionReason/efbc:DecisionReasonCode/text()", namespaces=namespaces)
        
        if decision_reason_code:
            award = {
                "id": award_id,
                "status": "unsuccessful",
                "statusDetails": DECISION_REASON_CODES.get(decision_reason_code[0], "Unknown reason"),
                "relatedLots": [lot_id]
            }
            result["awards"].append(award)

    return result if result["awards"] else None