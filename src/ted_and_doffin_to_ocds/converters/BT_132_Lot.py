# converters/BT_132_Lot.py

from lxml import etree
from ted_and_doffin_to_ocds.utils.date_utils import convert_to_iso_format


def parse_lot_public_opening_date(xml_content):
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

    lot_elements = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces,
    )

    for lot_element in lot_elements:
        lot_id = lot_element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        date = lot_element.xpath(
            "cac:TenderingProcess/cac:OpenTenderEvent/cbc:OccurrenceDate/text()",
            namespaces=namespaces,
        )
        time = lot_element.xpath(
            "cac:TenderingProcess/cac:OpenTenderEvent/cbc:OccurrenceTime/text()",
            namespaces=namespaces,
        )

        if date and time:
            # Remove timezone info from date before combining
            date_without_tz = date[0].split("+")[0]
            iso_date = convert_to_iso_format(f"{date_without_tz}T{time[0]}")
            lot = {
                "id": lot_id,
                "awardPeriod": {"startDate": iso_date},
                "bidOpening": {"date": iso_date},
            }
            result["tender"]["lots"].append(lot)

    return result if result["tender"]["lots"] else None


def merge_lot_public_opening_date(release_json, lot_public_opening_date_data):
    if not lot_public_opening_date_data:
        return

    tender_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in lot_public_opening_date_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in tender_lots if lot["id"] == new_lot["id"]), None,
        )
        if existing_lot:
            existing_lot.setdefault("awardPeriod", {}).update(new_lot["awardPeriod"])
            existing_lot["bidOpening"] = new_lot["bidOpening"]
        else:
            tender_lots.append(new_lot)
