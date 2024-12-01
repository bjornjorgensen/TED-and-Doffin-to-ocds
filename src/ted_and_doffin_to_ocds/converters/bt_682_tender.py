import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_foreign_subsidies_measures(xml_content: str) -> dict | None:
    """
    Parses the XML content to extract the Foreign Subsidies Measures.

    Args:
        xml_content (str): The XML content as a string.

    Returns:
        dict | None: A dictionary containing the parsed data or None if no bids are found.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        return None

    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }
    result = {"bids": {"details": []}}

    lot_tenders = root.xpath(
        "//ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult/efac:LotTender",
        namespaces=namespaces,
    )

    for tender in lot_tenders:
        tender_id = tender.xpath(
            "cbc:ID[@schemeName='tender']/text()", namespaces=namespaces
        )
        lot_id = tender.xpath(
            "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces
        )
        measures_code = tender.xpath(
            "efbc:ForeignSubsidiesMeasuresCode[@listName='foreign-subsidy-measure-conclusion']/text()",
            namespaces=namespaces,
        )

        if tender_id and lot_id and measures_code:
            result["bids"]["details"].append(
                {
                    "id": tender_id[0],
                    "foreignSubsidyMeasures": measures_code[0],
                    "relatedLots": [lot_id[0]],
                }
            )

    return result if result["bids"]["details"] else None


def merge_foreign_subsidies_measures(
    release_json: dict, measures_data: dict | None
) -> None:
    """
    Merges the parsed Foreign Subsidies Measures data into the existing release JSON structure.

    Args:
        release_json (dict): The existing release JSON structure.
        measures_data (dict | None): The parsed measures data.

    Returns:
        None
    """
    if not measures_data:
        logger.warning("No Foreign Subsidies Measures data to merge")
        return

    existing_bids = release_json.setdefault("bids", {}).setdefault("details", [])

    for new_bid in measures_data["bids"]["details"]:
        existing_bid = next(
            (bid for bid in existing_bids if bid["id"] == new_bid["id"]),
            None,
        )
        if existing_bid:
            existing_bid["foreignSubsidyMeasures"] = new_bid["foreignSubsidyMeasures"]
            existing_bid.setdefault("relatedLots", []).extend(new_bid["relatedLots"])
        else:
            existing_bids.append(new_bid)

    logger.info(
        "Merged Foreign Subsidies Measures data for %d bids",
        len(measures_data["bids"]["details"]),
    )
