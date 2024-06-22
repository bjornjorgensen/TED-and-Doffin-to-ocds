from lxml import etree

def parse_dps_termination(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    lots = []
    lot_results = root.xpath("//efac:NoticeResult/efac:LotResult", namespaces=namespaces)
    
    for lot_result in lot_results:
        dps_termination = lot_result.xpath("efbc:DPSTerminationIndicator/text()", namespaces=namespaces)
        if dps_termination and dps_termination[0].lower() == 'true':
            lot_id = lot_result.xpath("../efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
            if lot_id:
                lots.append({
                    "id": lot_id[0],
                    "techniques": {
                        "dynamicPurchasingSystem": {
                            "status": "terminated"
                        }
                    }
                })

    return {"tender": {"lots": lots}} if lots else None