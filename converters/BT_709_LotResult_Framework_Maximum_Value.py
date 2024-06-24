# converters/BT_709_LotResult_Framework_Maximum_Value.py
from lxml import etree

def parse_framework_maximum_value(xml_content):
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
        maximum_value = lot_result.xpath("efac:FrameworkAgreementValues/cbc:MaximumValueAmount/text()", namespaces=namespaces)
        currency = lot_result.xpath("efac:FrameworkAgreementValues/cbc:MaximumValueAmount/@currencyID", namespaces=namespaces)

        if result_id and lot_id and maximum_value and currency:
            result.append({
                "id": result_id[0],
                "relatedLots": [lot_id[0]],
                "maximumValue": {
                    "amount": float(maximum_value[0]),
                    "currency": currency[0]
                }
            })

    return result

def merge_framework_maximum_value(release_json, maximum_value_data):
    if maximum_value_data:
        awards = release_json.setdefault("awards", [])

        for data in maximum_value_data:
            award = next((a for a in awards if a.get("id") == data["id"]), None)
            if award:
                award["maximumValue"] = data["maximumValue"]
                award["relatedLots"] = data["relatedLots"]
            else:
                awards.append(data)

    return release_json