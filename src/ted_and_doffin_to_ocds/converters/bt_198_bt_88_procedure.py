# converters/bt_198_bt_88_procedure.py

import logging

from lxml import etree

from ted_and_doffin_to_ocds.utils.date_utils import start_date

logger = logging.getLogger(__name__)


def parse_bt198_bt88_procedure_unpublished_access_date(
    xml_content: str | bytes,
) -> dict | None:
    """
    Parse the XML content to extract the unpublished access date for the procedure features.

    This function extracts BT-198 (access date) data related to BT-88 (Procedure) from the XML.
    It looks for FieldsPrivacy elements containing dates when certain procedure feature information will be made available.

    Args:
        xml_content: The XML content to parse, either as a string or bytes object.
            Must be valid XML containing eForms namespaces and procedure data.

    Returns:
        Optional[Dict]: A dictionary containing the parsed unpublished access date data in the format:
            {
                "withheldInformation": [
                    {
                        "id": "pro-fea-{contract_id}",
                        "availabilityDate": "2025-03-31T00:00:00+01:00"
                    }
                ]
            }
        Returns None if no relevant data is found or if XML parsing fails.
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
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    result = {"withheldInformation": []}

    # Get ContractFolderID for generating IDs
    contract_folder_id = root.xpath(
        "/*/cbc:ContractFolderID/text()",
        namespaces=namespaces,
    )
    if not contract_folder_id:
        logger.warning("No ContractFolderID found")
        return None

    xpath_query = "/*/cac:TenderingProcess/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='pro-fea']/efbc:PublicationDate"

    publication_date_elements = root.xpath(xpath_query, namespaces=namespaces)

    for date_element in publication_date_elements:
        try:
            iso_date = start_date(date_element.text)
            withheld_info = {
                "id": f"pro-fea-{contract_folder_id[0]}",
                "availabilityDate": iso_date,
            }
            result["withheldInformation"].append(withheld_info)
        except ValueError:
            logger.exception("Error converting date: %s", date_element.text)
            continue

    if not result["withheldInformation"]:
        logger.debug(
            "No unpublished access date data found for BT-198(BT-88) Procedure"
        )
        return None

    return result


def merge_bt198_bt88_procedure_unpublished_access_date(
    release_json: dict,
    unpublished_access_date_data: dict | None,
) -> None:
    """
    Merge the parsed unpublished access date data into the main OCDS release JSON.

    This function updates the withheldInformation array in the release_json with access dates
    from unpublished fields related to procedure features.

    Args:
        release_json: The main OCDS release JSON document to be updated.
            Must be a mutable dictionary that may contain a withheldInformation array.
        unpublished_access_date_data: The parsed unpublished access date data to be merged.
            Should contain a withheldInformation array with objects having availabilityDate.
            Can be None, in which case no changes are made.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not unpublished_access_date_data:
        logger.warning(
            "No unpublished access date data to merge for BT-198(BT-88) Procedure",
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
        "Merged unpublished access date data for BT-198(BT-88) Procedure",
    )
