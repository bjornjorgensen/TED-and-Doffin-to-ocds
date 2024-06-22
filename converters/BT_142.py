from lxml import etree

WINNER_STATUS_CODES = {
    "clos-nw": "No winner was chosen and the competition is closed.",
    "open-nw": "The winner was not yet chosen, but the competition is still ongoing.",
    "selec-w": "At least one winner was chosen."
}

def parse_winner_chosen(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"awards": [], "tender": {"lots": []}}

    lot_results = root.xpath("//efac:NoticeResult/efac:LotResult", namespaces=namespaces)
    
    for lot_result in lot_results:
        result_code = lot_result.xpath("cbc:TenderResultCode/text()", namespaces=namespaces)[0]
        lot_id = lot_result.xpath("efac:TenderLot/cbc:ID/text()", namespaces=namespaces)[0]
        award_id = lot_result.xpath("cbc:ID/text()", namespaces=namespaces)[0]

        if result_code == "open-nw":
            result["tender"]["lots"].append({
                "id": lot_id,
                "status": "active"
            })
        else:
            award = {
                "id": award_id,
                "relatedLots": [lot_id],
                "statusDetails": WINNER_STATUS_CODES.get(result_code, "Unknown status")
            }
            if result_code == "selec-w":
                award["status"] = "active"
            elif result_code == "clos-nw":
                award["status"] = "unsuccessful"
            
            result["awards"].append(award)

    return result if result["awards"] or result["tender"]["lots"] else None