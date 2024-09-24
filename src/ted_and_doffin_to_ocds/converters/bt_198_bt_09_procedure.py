# converters/bt_198_bt_09_procedure.py

import logging
from lxml import etree
from ted_and_doffin_to_ocds.utils.date_utils import start_date

logger = logging.getLogger(__name__)


def bt_198_parse_unpublished_access_date_bt_09_procedure(xml_content):
    """
    Parse the XML content to extract the unpublished access date for the procedure.

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

    publication_date = root.xpath(
        "//cac:TenderingTerms/cac:ProcurementLegislationDocumentReference[cbc:ID/text()='CrossBorderLaw']/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='cro-bor-law']/efbc:PublicationDate/text()",
        namespaces=namespaces,
    )

    if publication_date:
        try:
            iso_date = start_date(publication_date[0])
            withheld_item = {"availabilityDate": iso_date}
            result["withheldInformation"].append(withheld_item)
        except ValueError:
            logger.exception("Error converting date")

    return result if result["withheldInformation"] else None


def bt_198_merge_unpublished_access_date_bt_09_procedure(
    release_json,
    unpublished_access_date_data,
):
    """
    Merge the parsed unpublished access date data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        unpublished_access_date_data (dict): The parsed unpublished access date data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not unpublished_access_date_data:
        logger.warning("No unpublished access date data to merge")
        return

    withheld_information = release_json.setdefault("withheldInformation", [])

    for item in unpublished_access_date_data["withheldInformation"]:
        if withheld_information:
            withheld_information[0]["availabilityDate"] = item["availabilityDate"]
        else:
            withheld_information.append(item)

    logger.info("Merged unpublished access date data")
