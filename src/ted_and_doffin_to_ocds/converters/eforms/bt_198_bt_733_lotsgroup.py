# converters/bt_198_bt_733_lotsgroup.py

import logging

from lxml import etree

from ted_and_doffin_to_ocds.utils.date_utils import start_date

logger = logging.getLogger(__name__)


def parse_bt198_bt733_lotsgroup_unpublished_access_date(xml_content):
    """Parse the XML content to extract the unpublished access date for the award criteria order justification in LotsGroup.

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
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    result = {"withheldInformation": []}

    lots_groups = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']",
        namespaces=namespaces,
    )

    for lots_group in lots_groups:
        fields_privacy = lots_group.xpath(
            ".//cac:AwardingCriterion//efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='awa-cri-ord']",
            namespaces=namespaces,
        )

        if fields_privacy:
            publication_date = fields_privacy[0].xpath(
                "efbc:PublicationDate/text()",
                namespaces=namespaces,
            )
            group_id = lots_group.xpath("cbc:ID/text()", namespaces=namespaces)

            if publication_date and group_id:
                iso_date = start_date(publication_date[0])
                withheld_info = {
                    "id": f"awa-cri-ord-{group_id[0]}",
                    "field": "awa-cri-ord",
                    "availabilityDate": iso_date,
                }
                result["withheldInformation"].append(withheld_info)

    return result if result["withheldInformation"] else None


def merge_bt198_bt733_lotsgroup_unpublished_access_date(
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
        logger.warning(
            "No unpublished access date data to merge for BT-198(BT-733)-LotsGroup",
        )
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

    logger.info(
        "Merged %d unpublished access date(s) for BT-198(BT-733)-LotsGroup",
        len(unpublished_access_date_data["withheldInformation"]),
    )