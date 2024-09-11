# converters/BT_198_160_Tender.py

import logging
from lxml import etree
from ted_and_doffin_to_ocds.utils.date_utils import start_date

logger = logging.getLogger(__name__)


def bt_198_bt_160_parse_unpublished_access_date(xml_content):
    """
    Parse the XML content to extract the unpublished access date for BT-198 and BT-160.

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

    xpath_query = "//efac:NoticeResult/efac:LotTender/efac:ConcessionRevenue/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='con-rev-buy']"
    field_privacy_elements = root.xpath(xpath_query, namespaces=namespaces)

    for element in field_privacy_elements:
        lot_tender_id = element.xpath(
            "ancestor::efac:LotTender/cbc:ID/text()", namespaces=namespaces
        )
        publication_date = element.xpath(
            "efbc:PublicationDate/text()", namespaces=namespaces
        )

        if lot_tender_id and publication_date:
            iso_date = start_date(publication_date[0])
            withheld_item = {
                "id": f"con-rev-buy-{lot_tender_id[0]}",
                "availabilityDate": iso_date,
            }
            result["withheldInformation"].append(withheld_item)

    return result if result["withheldInformation"] else None


def bt_198_bt_160_merge_unpublished_access_date(
    release_json, unpublished_access_date_data
):
    """
    Merge the parsed unpublished access date data for BT-198 and BT-160 into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        unpublished_access_date_data (dict): The parsed unpublished access date data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not unpublished_access_date_data:
        logger.warning("No unpublished access date data to merge for BT-198 and BT-160")
        return

    withheld_information = release_json.setdefault("withheldInformation", [])

    for new_item in unpublished_access_date_data["withheldInformation"]:
        existing_item = next(
            (item for item in withheld_information if item["id"] == new_item["id"]),
            None,
        )
        if existing_item:
            existing_item["availabilityDate"] = new_item["availabilityDate"]
        else:
            withheld_information.append(new_item)

    logger.info(
        f"Merged unpublished access date data for BT-198 and BT-160: {len(unpublished_access_date_data['withheldInformation'])} items"
    )
