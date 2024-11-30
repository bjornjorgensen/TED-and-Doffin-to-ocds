# converters/opt_322_lotresult.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_lotresult_technical_identifier(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    }

    result = {"awards": []}

    # Parse LotResult information
    lot_results = root.xpath(
        "//efac:NoticeResult/efac:LotResult", namespaces=namespaces
    )

    for lot_result in lot_results:
        result_id = lot_result.xpath(
            "cbc:ID[@schemeName='result']/text()", namespaces=namespaces
        )

        if result_id:
            award = {"id": result_id[0]}
            result["awards"].append(award)

    return result if result["awards"] else None


def merge_lotresult_technical_identifier(
    release_json, lotresult_technical_identifier_data
) -> None:
    if not lotresult_technical_identifier_data:
        logger.info("No LotResult Technical Identifier data to merge.")
        return

    awards = release_json.setdefault("awards", [])

    for new_award in lotresult_technical_identifier_data["awards"]:
        if not any(award["id"] == new_award["id"] for award in awards):
            awards.append(new_award)

    logger.info(
        "Merged LotResult Technical Identifier data for %d awards.",
        len(lotresult_technical_identifier_data["awards"]),
    )
