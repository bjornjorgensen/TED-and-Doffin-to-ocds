# converters/bt_163_Tender.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_concession_value_description(
    xml_content: str | bytes,
) -> dict | None:
    """
    Parse concession value description from XML data.

    Args:
        xml_content (Union[str, bytes]): The XML content containing tender information

    Returns:
        Optional[Dict]: Dictionary containing award information, or None if no data found
        The structure follows the format:
        {
            "awards": [
                {
                    "id": str,
                    "relatedLots": [str],
                    "valueCalculationMethod": str
                }
            ]
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

    result = {"awards": []}

    # Process lot tenders with value descriptions
    lot_tenders = root.xpath(
        "//efac:NoticeResult/efac:LotTender",
        namespaces=namespaces,
    )

    for lot_tender in lot_tenders:
        tender_id = lot_tender.xpath(
            "cbc:ID[@schemeName='tender']/text()",
            namespaces=namespaces,
        )
        value_desc = lot_tender.xpath(
            "efac:ConcessionRevenue/efbc:ValueDescription/text()",
            namespaces=namespaces,
        )

        if tender_id and value_desc:
            # Find corresponding lot result
            lot_result = root.xpath(
                f"//efac:NoticeResult/efac:LotResult[efac:LotTender/cbc:ID[@schemeName='tender']='{tender_id[0]}']",
                namespaces=namespaces,
            )
            if lot_result:
                result_id = lot_result[0].xpath(
                    "cbc:ID[@schemeName='result']/text()",
                    namespaces=namespaces,
                )
                lot_id = lot_result[0].xpath(
                    "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()",
                    namespaces=namespaces,
                )

                if result_id and lot_id:
                    award = {
                        "id": result_id[0],
                        "relatedLots": [lot_id[0]],
                        "valueCalculationMethod": value_desc[0],
                    }
                    result["awards"].append(award)

    return result if result["awards"] else None


def merge_concession_value_description(
    release_json: dict, value_description_data: dict | None
) -> None:
    """
    Merge concession value description data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        value_description_data (Optional[Dict]): The source data containing awards
            to be merged. If None, function returns without making changes.
    """
    if not value_description_data:
        return

    existing_awards = release_json.setdefault("awards", [])
    for new_award in value_description_data["awards"]:
        existing_award = next(
            (a for a in existing_awards if a["id"] == new_award["id"]),
            None,
        )
        if existing_award:
            existing_award["valueCalculationMethod"] = new_award[
                "valueCalculationMethod"
            ]
            existing_lots = set(existing_award.get("relatedLots", []))
            existing_lots.update(new_award["relatedLots"])
            existing_award["relatedLots"] = list(existing_lots)
        else:
            existing_awards.append(new_award)
