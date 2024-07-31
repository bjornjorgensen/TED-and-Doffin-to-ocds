# converters/BT_196_BT_733_Lot.py

from lxml import etree

def parse_bt_196_bt_733_lot(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    result = {"withheldInformation": []}

    # Find all ProcurementProjectLot elements with schemeName="Lot"
    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)

    for lot in lots:
        # Find the relevant FieldsPrivacy element
        fields_privacy = lot.xpath(
            ".//cac:AwardingTerms/cac:AwardingCriterion/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='awa-cri-ord']",
            namespaces=namespaces
        )

        if fields_privacy:
            reason_description = fields_privacy[0].xpath(
                "efbc:ReasonDescription/text()",
                namespaces=namespaces
            )

            if reason_description:
                result["withheldInformation"].append({
                    "id": "awa-cri-ord-" + lot.xpath("cbc:ID/text()", namespaces=namespaces)[0],
                    "field": "awa-cri-ord",
                    "name": "Award Criteria Order Justification",
                    "rationale": reason_description[0]
                })

    return result if result["withheldInformation"] else None

def merge_bt_196_bt_733_lot(release_json, bt_196_data):
    if not bt_196_data:
        return

    existing_withheld_info = release_json.setdefault("withheldInformation", [])

    for new_item in bt_196_data["withheldInformation"]:
        existing_item = next((item for item in existing_withheld_info if item["id"] == new_item["id"]), None)

        if existing_item:
            existing_item.update(new_item)
        else:
            existing_withheld_info.append(new_item)