import logging

from lxml import etree

from ted_and_doffin_to_ocds.utils.date_utils import start_date

logger = logging.getLogger(__name__)


def bt_198_parse_unpublished_access_date_bt_09_procedure(
    xml_content: str | bytes,
) -> dict | None:
    """Parse the XML content to extract the unpublished access date for the procedure.

    This function extracts BT-198 (access date) data related to BT-09 (Procedure) from the XML.
    It looks for FieldsPrivacy elements containing dates when certain information will be made available.

    Args:
        xml_content: The XML content to parse, either as a string or bytes object.
            Must be valid XML containing eForms namespaces and procedure data.

    Returns:
        Optional[Dict]: A dictionary containing the parsed unpublished access date data in the format:
            {
                "withheldInformation": [
                    {
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
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    result = {"withheldInformation": []}

    xpath_query = "/*/cac:TenderingTerms/cac:ProcurementLegislationDocumentReference[cbc:ID/text()='CrossBorderLaw']/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='cro-bor-law']/efbc:PublicationDate"

    publication_date_elements = root.xpath(xpath_query, namespaces=namespaces)

    for date_element in publication_date_elements:
        try:
            iso_date = start_date(date_element.text)
            withheld_info = {
                "availabilityDate": iso_date,
            }
            result["withheldInformation"].append(withheld_info)
        except ValueError:
            logger.exception("Error converting date: %s", date_element.text)
            continue

    if not result["withheldInformation"]:
        logger.debug(
            "No unpublished access date data found for BT-198(BT-09) Procedure"
        )
        return None

    return result


def bt_198_merge_unpublished_access_date_bt_09_procedure(
    release_json: dict,
    unpublished_access_date_data: dict | None,
) -> None:
    """Merge the parsed unpublished access date data into the main OCDS release JSON.

    This function updates the withheldInformation array in the release_json with access dates
    from unpublished fields related to procedure information.

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
            "No unpublished access date data to merge for BT-198(BT-09) Procedure",
        )
        return

    withheld_information = release_json.setdefault("withheldInformation", [])

    for item in unpublished_access_date_data["withheldInformation"]:
        if withheld_information:
            withheld_information[0]["availabilityDate"] = item["availabilityDate"]
        else:
            withheld_information.append(item)

    logger.info(
        "Merged unpublished access date data for BT-198(BT-09) Procedure",
    )
