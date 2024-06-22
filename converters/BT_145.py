from lxml import etree
from datetime import datetime, timezone

def parse_contract_conclusion_date(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"contracts": []}

    settled_contracts = root.xpath("//efac:NoticeResult/efac:SettledContract", namespaces=namespaces)
    
    for settled_contract in settled_contracts:
        contract_id = settled_contract.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        issue_date = settled_contract.xpath("cbc:IssueDate/text()", namespaces=namespaces)[0]
        
        # Convert date to ISO format
        date = datetime.fromisoformat(issue_date)
        if date.tzinfo is None:
            date = date.replace(tzinfo=timezone.utc)
        formatted_date = date.isoformat()

        contract = {
            "id": contract_id,
            "dateSigned": formatted_date
        }

        # Find related LotResults
        lot_results = root.xpath(f"//efac:NoticeResult/efac:LotResult[efac:SettledContract/cbc:ID/text()='{contract_id}']", namespaces=namespaces)
        
        if len(lot_results) == 1:
            contract["awardID"] = lot_results[0].xpath("cbc:ID/text()", namespaces=namespaces)[0]
        elif len(lot_results) > 1:
            contract["awardIDs"] = [lot_result.xpath("cbc:ID/text()", namespaces=namespaces)[0] for lot_result in lot_results]

        result["contracts"].append(contract)

    return result if result["contracts"] else None