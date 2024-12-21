import logging

from lxml import etree

from ted_and_doffin_to_ocds.utils.date_utils import start_date

logger = logging.getLogger(__name__)


def parse_lot_public_opening_date(xml_content: str | bytes) -> dict | None:
    """Parse the public opening date from lot-level XML data.

    Args:
        xml_content (Union[str, bytes]): The XML content containing lot information

    Returns:
        Optional[Dict]: Dictionary containing tender lot information, or None if no data found
        The structure follows the format:
        {
            "tender": {
                "lots": [
                    {
                        "id": str,
                        "awardPeriod": {
                            "startDate": str # ISO formatted date with time
                        },
                        "bidOpening": {
                            "date": str # Same as awardPeriod.startDate
                        }
                    }
                ]
            }
        }

    """
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
        lot_id = lot.xpath("cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)[0]
        date = lot.xpath(
            "cac:TenderingProcess/cac:OpenTenderEvent/cbc:OccurrenceDate/text()",
            namespaces=namespaces,
        )
        time = lot.xpath(
            "cac:TenderingProcess/cac:OpenTenderEvent/cbc:OccurrenceTime/text()",
            namespaces=namespaces,
        )

        if date:
            try:
                # Combine date and time if available
                date_str = date[0]
                if time:
                    date_str = f"{date_str.split('+')[0]}T{time[0]}"
                iso_date = start_date(date_str)
                lot_data = {
                    "id": lot_id,
                    "awardPeriod": {"startDate": iso_date},
                    "bidOpening": {"date": iso_date},
                }
                result["tender"]["lots"].append(lot_data)
            except ValueError as e:
                logger.warning("Error parsing opening date for lot %s: %s", lot_id, e)

    return result if result["tender"]["lots"] else None


def merge_lot_public_opening_date(
    release_json: dict, lot_public_opening_date_data: dict | None
) -> None:
    """Merge public opening date data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        lot_public_opening_date_data (Optional[Dict]): The source data containing tender lots
            to be merged. If None, function returns without making changes.

    Note:
        The function modifies release_json in-place by adding or updating the
        tender.lots.awardPeriod.startDate and tender.lots.bidOpening.date fields.

    """
    if not lot_public_opening_date_data:
        return

    tender_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in lot_public_opening_date_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in tender_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("awardPeriod", {}).update(new_lot["awardPeriod"])
            existing_lot["bidOpening"] = new_lot["bidOpening"]
        else:
            tender_lots.append(new_lot)
