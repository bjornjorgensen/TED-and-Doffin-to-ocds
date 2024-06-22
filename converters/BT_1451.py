from lxml import etree
from datetime import datetime, timezone

def parse_winner_decision_date(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"awards": []}

    settled_contracts = root.xpath("//efac:NoticeResult/efac:SettledContract", namespaces=namespaces)
    
    for settled_contract in settled_contracts:
        contract_id = settled_contract.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        award_date = settled_contract.xpath("cbc:AwardDate/text()", namespaces=namespaces)
        
        if award_date:
            # Convert date to ISO format
            date = datetime.fromisoformat(award_date[0])
            if date.tzinfo is None:
                date = date.replace(tzinfo=timezone.utc)
            formatted_date = date.isoformat()

            # Find related LotResults
            lot_results = root.xpath(f"//efac:NoticeResult/efac:LotResult[efac:SettledContract/cbc:ID/text()='{contract_id}']", namespaces=namespaces)
            
            for lot_result in lot_results:
                award_id = lot_result.xpath("cbc:ID/text()", namespaces=namespaces)[0]
                lot_id = lot_result.xpath("efac:TenderLot/cbc:ID/text()", namespaces=namespaces)[0]

                award = next((a for a in result["awards"] if a["id"] == award_id), None)
                if award is None:
                    award = {
                        "id": award_id,
                        "relatedLots": [lot_id],
                        "date": formatted_date
                    }
                    result["awards"].append(award)
                else:
                    if "date" not in award or formatted_date < award["date"]:
                        award["date"] = formatted_date

    return result if result["awards"] else None