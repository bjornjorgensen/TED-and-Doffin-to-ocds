from lxml import etree

def parse_electronic_auction_description(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    lots = []
    procurement_project_lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in procurement_project_lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        auction_description = lot.xpath(
            "cac:TenderingProcess/cac:AuctionTerms/cbc:Description/text()",
            namespaces=namespaces
        )
        
        if auction_description:
            lots.append({
                "id": lot_id,
                "techniques": {
                    "electronicAuction": {
                        "description": auction_description[0]
                    }
                }
            })

    return {"tender": {"lots": lots}} if lots else None