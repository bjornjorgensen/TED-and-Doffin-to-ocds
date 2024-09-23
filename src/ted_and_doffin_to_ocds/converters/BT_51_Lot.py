# converters/BT_51_Lot.py

from lxml import etree


def parse_lot_maximum_candidates(xml_content):
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
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)
        max_candidates = lot.xpath(
            "cac:TenderingProcess/cac:EconomicOperatorShortList/cbc:MaximumQuantity/text()",
            namespaces=namespaces,
        )

        if lot_id and max_candidates:
            result["tender"]["lots"].append(
                {
                    "id": lot_id[0],
                    "secondStage": {"maximumCandidates": int(max_candidates[0])},
                },
            )

    return result if result["tender"]["lots"] else None


def merge_lot_maximum_candidates(release_json, lot_maximum_candidates_data):
    if not lot_maximum_candidates_data:
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in lot_maximum_candidates_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]), None,
        )
        if existing_lot:
            existing_lot.setdefault("secondStage", {})["maximumCandidates"] = new_lot[
                "secondStage"
            ]["maximumCandidates"]
        else:
            existing_lots.append(new_lot)
