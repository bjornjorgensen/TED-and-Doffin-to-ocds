# converters/BT_196_BT_720_Tender.py

from lxml import etree

def parse_bt_196_bt_720_tender(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode('utf-8')
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

    # Find all LotTender elements
    lot_tenders = root.xpath("//efac:NoticeResult/efac:LotTender", namespaces=namespaces)

    for lot_tender in lot_tenders:
        # Find the relevant FieldsPrivacy element
        fields_privacy = lot_tender.xpath(
            "./efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='win-ten-val']",
            namespaces=namespaces
        )

        if fields_privacy:
            reason_description = fields_privacy[0].xpath(
                "efbc:ReasonDescription/text()",
                namespaces=namespaces
            )

            if reason_description:
                result["withheldInformation"].append({
                    "rationale": reason_description[0]
                })

    return result if result["withheldInformation"] else None

def merge_bt_196_bt_720_tender(release_json, bt_196_data):
    if not bt_196_data:
        return

    existing_withheld_info = release_json.setdefault("withheldInformation", [])

    for new_item in bt_196_data["withheldInformation"]:
        # Assuming there's a corresponding item already created for BT-195
        # We'll update the first item without a rationale, or add a new one if none exist
        existing_item = next((item for item in existing_withheld_info if "rationale" not in item), None)

        if existing_item:
            existing_item["rationale"] = new_item["rationale"]
        else:
            existing_withheld_info.append(new_item)