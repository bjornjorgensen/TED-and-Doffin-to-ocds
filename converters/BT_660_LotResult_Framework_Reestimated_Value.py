# converters/BT_660_LotResult_Framework_Reestimated_Value.py
from lxml import etree

def parse_framework_reestimated_value(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'
    }

    result = []

    lot_results = root.xpath("//efac:NoticeResult/efac:LotResult", namespaces=namespaces)
    for lot_result in lot_results:
        result_id = lot_result.xpath("cbc:ID[@schemeName='result']/text()", namespaces=namespaces)
        lot_id = lot_result.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
        reestimated_value = lot_result.xpath("efac:FrameworkAgreementValues/cbc:ReestimatedValueAmount/text()", namespaces=namespaces)
        currency = lot_result.xpath("efac:FrameworkAgreementValues/cbc:ReestimatedValueAmount/@currencyID", namespaces=namespaces)

        if result_id and lot_id and reestimated_value and currency:
            result.append({
                "id": result_id[0],
                "relatedLots": [lot_id[0]],
                "estimatedValue": {
                    "amount": float(reestimated_value[0]),
                    "currency": currency[0]
                }
            })

    return result

def merge_framework_reestimated_value(release_json, reestimated_value_data):
    if reestimated_value_data:
        awards = release_json.setdefault("awards", [])

        for data in reestimated_value_data:
            award = next((a for a in awards if a.get("id") == data["id"]), None)
            if award:
                award["estimatedValue"] = data["estimatedValue"]
                award["relatedLots"] = data["relatedLots"]
            else:
                awards.append(data)

    return release_json