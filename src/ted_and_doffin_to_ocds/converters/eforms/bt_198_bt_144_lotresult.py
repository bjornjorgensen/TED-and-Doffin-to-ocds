# converters/bt_198_bt_144_LotResult.py

import logging

from lxml import etree

from ted_and_doffin_to_ocds.utils.date_utils import start_date

logger = logging.getLogger(__name__)


def parse_bt198_bt144_unpublished_access_date(xml_content):
    """Parse the XML content to extract the unpublished access date for the not awarded reason.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed unpublished access date data.
        None: If no relevant data is found.

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

    result = {"withheldInformation": []}

    lot_results = root.xpath(
        "//efac:NoticeResult/efac:LotResult",
        namespaces=namespaces,
    )

    for lot_result in lot_results:
        lot_id = lot_result.xpath(
            "cbc:ID[@schemeName='result']/text()",
            namespaces=namespaces,
        )
        publication_date = lot_result.xpath(
            "efac:DecisionReason/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='no-awa-rea']/efbc:PublicationDate/text()",
            namespaces=namespaces,
        )

        if lot_id and publication_date:
            iso_date = start_date(publication_date[0])
            withheld_info = {
                "id": f"no-awa-rea-{lot_id[0]}",
                "availabilityDate": iso_date,
            }
            result["withheldInformation"].append(withheld_info)

    return result if result["withheldInformation"] else None


def merge_bt198_bt144_unpublished_access_date(
    release_json,
    unpublished_access_date_data,
) -> None:
    """Merge the parsed unpublished access date data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        unpublished_access_date_data (dict): The parsed unpublished access date data to be merged.

    Returns:
        None: The function updates the release_json in-place.

    """
    if not unpublished_access_date_data:
        logger.warning("No unpublished access date data to merge for BT-198(BT-144)")
        return

    withheld_info = release_json.setdefault("withheldInformation", [])

    for new_item in unpublished_access_date_data["withheldInformation"]:
        existing_item = next(
            (item for item in withheld_info if item.get("id") == new_item["id"]),
            None,
        )
        if existing_item:
            existing_item["availabilityDate"] = new_item["availabilityDate"]
        else:
            withheld_info.append(new_item)

    logger.info("Merged unpublished access date data for BT-198(BT-144)")
