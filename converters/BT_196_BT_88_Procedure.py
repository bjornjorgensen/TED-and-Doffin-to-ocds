# converters/BT_196_BT_88_Procedure.py

from lxml import etree

def parse_bt_196_bt_88_procedure(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    result = {"withheldInformation": []}

    # Find the relevant FieldsPrivacy element
    fields_privacy = root.xpath(
        "//cac:TenderingProcess/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='pro-fea']",
        namespaces=namespaces
    )

    if fields_privacy:
        reason_description = fields_privacy[0].xpath(
            "efbc:ReasonDescription/text()",
            namespaces=namespaces
        )

        if reason_description:
            result["withheldInformation"].append({
                "id": "pro-fea-1",
                "field": "pro-fea",
                "name": "Procedure Features Justification",
                "rationale": reason_description[0]
            })

    return result if result["withheldInformation"] else None

def merge_bt_196_bt_88_procedure(release_json, bt_196_data):
    if not bt_196_data:
        return

    existing_withheld_info = release_json.setdefault("withheldInformation", [])

    for new_item in bt_196_data["withheldInformation"]:
        existing_item = next((item for item in existing_withheld_info if item["id"] == new_item["id"]), None)

        if existing_item:
            existing_item.update(new_item)
        else:
            existing_withheld_info.append(new_item)