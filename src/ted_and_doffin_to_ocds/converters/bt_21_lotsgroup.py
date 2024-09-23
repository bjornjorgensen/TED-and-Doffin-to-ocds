# converters/bt_21_LotsGroup.py

from lxml import etree


def parse_lots_group_title(xml_content):
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

    result = {"tender": {"lotGroups": []}}

    lot_groups = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']",
        namespaces=namespaces,
    )

    for lot_group in lot_groups:
        lot_group_id = lot_group.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        lot_group_title = lot_group.xpath(
            "cac:ProcurementProject/cbc:Name/text()",
            namespaces=namespaces,
        )

        if lot_group_title:
            result["tender"]["lotGroups"].append(
                {"id": lot_group_id, "title": lot_group_title[0]},
            )

    return result if result["tender"]["lotGroups"] else None


def merge_lots_group_title(release_json, lots_group_title_data):
    if not lots_group_title_data:
        return

    existing_lot_groups = release_json.setdefault("tender", {}).setdefault(
        "lotGroups",
        [],
    )

    for new_lot_group in lots_group_title_data["tender"]["lotGroups"]:
        existing_lot_group = next(
            (
                group
                for group in existing_lot_groups
                if group["id"] == new_lot_group["id"]
            ),
            None,
        )
        if existing_lot_group:
            existing_lot_group["title"] = new_lot_group["title"]
        else:
            existing_lot_groups.append(new_lot_group)
