from lxml import etree

def parse_concession_revenue_buyer(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"contracts": []}

    lot_tenders = root.xpath("//efac:NoticeResult/efac:LotTender", namespaces=namespaces)
    
    for lot_tender in lot_tenders:
        tender_id = lot_tender.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        revenue_buyer_amount = lot_tender.xpath("efac:ConcessionRevenue/efbc:RevenueBuyerAmount/text()", namespaces=namespaces)
        revenue_buyer_currency = lot_tender.xpath("efac:ConcessionRevenue/efbc:RevenueBuyerAmount/@currencyID", namespaces=namespaces)
        
        if revenue_buyer_amount and revenue_buyer_currency:
            # Find the corresponding SettledContract
            settled_contract = root.xpath(f"//efac:NoticeResult/efac:SettledContract[efac:LotTender/cbc:ID/text()='{tender_id}']", namespaces=namespaces)
            if settled_contract:
                contract_id = settled_contract[0].xpath("cbc:ID/text()", namespaces=namespaces)[0]
                
                # Find the corresponding LotResult
                lot_result = root.xpath(f"//efac:NoticeResult/efac:LotResult[efac:SettledContract/cbc:ID/text()='{contract_id}']", namespaces=namespaces)
                
                contract = {
                    "id": contract_id,
                    "implementation": {
                        "charges": [{
                            "id": "government",
                            "title": "The estimated revenue coming from the buyer who granted the concession (e.g. prizes and payments).",
                            "estimatedValue": {
                                "amount": float(revenue_buyer_amount[0]),
                                "currency": revenue_buyer_currency[0]
                            },
                            "paidBy": "government"
                        }]
                    }
                }
                
                if len(lot_result) == 1:
                    contract["awardID"] = lot_result[0].xpath("cbc:ID/text()", namespaces=namespaces)[0]
                elif len(lot_result) > 1:
                    contract["awardIDs"] = [lr.xpath("cbc:ID/text()", namespaces=namespaces)[0] for lr in lot_result]
                
                result["contracts"].append(contract)

    return result if result["contracts"] else None