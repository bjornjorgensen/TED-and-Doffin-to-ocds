# converters/BT_196_BT_636_LotResult.py 

from lxml import etree

def parse_bt_196_lot_result(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    result = {"withheldInformation": []}

    # Find all LotResult elements
    lot_results = root.xpath("//efac:NoticeResult/efac:LotResult", namespaces=namespaces)

    for lot_result in lot_results:
        # Find the relevant FieldsPrivacy element
        fields_privacy = lot_result.xpath(
            ".//efac:AppealRequestsStatistics[efbc:StatisticsCode/@listName='irregularity-type']"
            "/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='buy-rev-typ']",
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

def merge_bt_196_lot_result(release_json, bt_196_data):
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