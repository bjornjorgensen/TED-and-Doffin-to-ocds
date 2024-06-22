from lxml import etree

def parse_concession_revenue_user(xml_content):
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
        revenue_user_amount = lot_tender.xpath("efac:ConcessionRevenue/efbc:RevenueUserAmount/text()", namespaces=namespaces)
        revenue_user_currency = lot_tender.xpath("efac:ConcessionRevenue/efbc:RevenueUserAmount/@currencyID", namespaces=namespaces)
        
        if revenue_user_amount and revenue_user_currency:
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
                            "id": "user",
                            "title": "The estimated revenue coming from the users of the concession (e.g. fees and fines).",
                            "estimatedValue": {
                                "amount": float(revenue_user_amount[0]),
                                "currency": revenue_user_currency[0]
                            },
                            "paidBy": "user"
                        }]
                    }
                }
                
                if len(lot_result) == 1:
                    contract["awardID"] = lot_result[0].xpath("cbc:ID/text()", namespaces=namespaces)[0]
                elif len(lot_result) > 1:
                    contract["awardIDs"] = [lr.xpath("cbc:ID/text()", namespaces=namespaces)[0] for lr in lot_result]
                
                result["contracts"].append(contract)

    return result if result["contracts"] else None