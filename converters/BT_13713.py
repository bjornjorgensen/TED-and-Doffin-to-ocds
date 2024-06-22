from lxml import etree

def parse_result_lot_identifier(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    awards = []
    lot_results = root.xpath("//efac:LotResult", namespaces=namespaces)
    
    for lot_result in lot_results:
        award_id = lot_result.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        lot_id = lot_result.xpath("efac:TenderLot/cbc:ID/text()", namespaces=namespaces)[0]
        
        award = next((a for a in awards if a["id"] == award_id), None)
        if award is None:
            award = {"id": award_id, "relatedLots": []}
            awards.append(award)
        
        if lot_id not in award["relatedLots"]:
            award["relatedLots"].append(lot_id)

    return {"awards": awards} if awards else None