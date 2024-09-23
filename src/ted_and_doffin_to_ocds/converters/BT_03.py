# converters/BT_03.py

from lxml import etree


def parse_form_type(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    form_type_codes = root.xpath(
        "//cbc:NoticeTypeCode[@listName]",
        namespaces=namespaces,
    )

    form_type_mapping = {
        "planning": {"tag": ["tender"], "status": "planned"},
        "competition": {"tag": ["tender"], "status": "active"},
        "change": {"tag": ["tenderUpdate"], "status": None},
        "result": {"tag": ["award", "contract"], "status": "complete"},
        "dir-awa-pre": {"tag": ["award", "contract"], "status": "complete"},
        "cont-modif": {"tag": ["awardUpdate", "contractUpdate"], "status": None},
    }

    result = {"tag": set(), "tender": {}}

    for form_type_code in form_type_codes:
        list_name = form_type_code.get("listName")
        if list_name in form_type_mapping:
            result["tag"].update(form_type_mapping[list_name]["tag"])
            if form_type_mapping[list_name]["status"]:
                result["tender"]["status"] = form_type_mapping[list_name]["status"]

    if result["tag"]:
        result["tag"] = list(result["tag"])
        return result

    return None


def merge_form_type(release_json, form_type_data):
    if form_type_data.get("tag"):
        release_json.setdefault("tag", []).extend(
            tag
            for tag in form_type_data["tag"]
            if tag not in release_json.get("tag", [])
        )
    if form_type_data.get("tender"):
        release_json.setdefault("tender", {}).update(form_type_data["tender"])
