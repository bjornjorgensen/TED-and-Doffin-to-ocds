# converters/bt_22_Lot.py

from lxml import etree


def parse_lot_internal_identifier(xml_content):
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

    result = {"tender": {"lots": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        internal_id = lot.xpath(
            "cac:ProcurementProject/cbc:ID[@schemeName='InternalID']/text()",
            namespaces=namespaces,
        )

        if internal_id:
            result["tender"]["lots"].append(
                {
                    "id": lot_id,
                    "identifiers": {"id": internal_id[0], "scheme": "internal"},
                },
            )

    return result if result["tender"]["lots"] else None


def merge_lot_internal_identifier(release_json, lot_internal_identifier_data) -> None:
    if not lot_internal_identifier_data:
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in lot_internal_identifier_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot["identifiers"] = new_lot["identifiers"]
        else:
            existing_lots.append(new_lot)
