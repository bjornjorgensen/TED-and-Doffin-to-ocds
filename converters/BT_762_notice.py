# converters/BT_762_notice.py

from lxml import etree

def parse_change_reason_description(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    change_reasons = root.xpath("//efac:ChangeReason/efbc:ReasonDescription/text()", namespaces=namespaces)
    
    return change_reasons

def merge_change_reason_description(release_json, change_reasons):
    if not change_reasons:
        return release_json

    tender = release_json.setdefault("tender", {})
    amendments = tender.setdefault("amendments", [])

    for index, reason in enumerate(change_reasons):
        if index < len(amendments):
            amendments[index]["rationale"] = reason
        else:
            amendments.append({"rationale": reason})

    if amendments:
        tender["amendments"] = amendments
    elif "amendments" in tender:
        del tender["amendments"]

    return release_json