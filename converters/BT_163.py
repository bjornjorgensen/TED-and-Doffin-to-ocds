from lxml import etree

def parse_concession_value_description(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"awards": []}

    lot_tenders = root.xpath("//efac:NoticeResult/efac:LotTender", namespaces=namespaces)
    
    for lot_tender in lot_tenders:
        tender_id = lot_tender.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        value_description = lot_tender.xpath("efac:ConcessionRevenue/efbc:ValueDescription/text()", namespaces=namespaces)
        
        if value_description:
            # Find the corresponding LotResult
            lot_result = root.xpath(f"//efac:NoticeResult/efac:LotResult[efac:LotTender/cbc:ID/text()='{tender_id}']", namespaces=namespaces)
            
            if lot_result:
                result_id = lot_result[0].xpath("cbc:ID/text()", namespaces=namespaces)[0]
                lot_id = lot_result[0].xpath("efac:TenderLot/cbc:ID/text()", namespaces=namespaces)[0]
                
                award = {
                    "id": result_id,
                    "relatedLots": [lot_id],
                    "valueCalculationMethod": value_description[0]
                }
                
                result["awards"].append(award)

    return result if result["awards"] else None