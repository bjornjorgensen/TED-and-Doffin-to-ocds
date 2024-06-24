# converters/BT_644_Lot_Prize_Value.py
from lxml import etree

def parse_lot_prize_value(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        prizes = lot.xpath(".//cac:AwardingTerms/cac:Prize/cbc:ValueAmount", namespaces=namespaces)
        
        if prizes:
            result[lot_id] = [
                {
                    "amount": float(prize.text),
                    "currency": prize.get("currencyID")
                }
                for prize in prizes
            ]

    return result

def merge_lot_prize_value(release_json, prize_data):
    if prize_data:
        tender = release_json.setdefault("tender", {})
        lots = tender.setdefault("lots", [])

        for lot_id, prizes in prize_data.items():
            lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
            if not lot:
                lot = {"id": lot_id}
                lots.append(lot)
            
            design_contest = lot.setdefault("designContest", {})
            prizes_obj = design_contest.setdefault("prizes", {})
            details = prizes_obj.setdefault("details", [])

            for index, prize in enumerate(prizes):
                if index < len(details):
                    # Update existing prize
                    details[index]["value"] = prize
                else:
                    # Add new prize
                    details.append({
                        "id": str(len(details)),
                        "value": prize
                    })

    return release_json