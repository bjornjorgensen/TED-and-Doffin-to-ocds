# converters/BT_195_BT_5422_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_bt195_bt5422_lot(xml_content):
    """
    Parse the XML content to extract the unpublished identifier for the lot.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed unpublished identifier data.
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

    xpath_query = (
        "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']"
        "/cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion"
        "/cac:SubordinateAwardingCriterion/ext:UBLExtensions/ext:UBLExtension"
        "/ext:ExtensionContent/efext:EformsExtension/efac:AwardCriterionParameter"
        "[efbc:ParameterCode/@listName='number-fixed']"
        "/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='awa-cri-fix']"
        "/efbc:FieldIdentifierCode"
    )

    field_identifier_codes = root.xpath(xpath_query, namespaces=namespaces)

    for field_identifier_code in field_identifier_codes:
        lot_id = field_identifier_code.xpath(
            "ancestor::cac:ProcurementProjectLot/cbc:ID/text()", namespaces=namespaces
        )[0]

        withheld_info = {
            "id": f"{field_identifier_code.text}-{lot_id}",
            "field": "awa-cri-fix",
            "name": "Award Criterion Number Fixed",
        }
        result["withheldInformation"].append(withheld_info)

    return result if result["withheldInformation"] else None


def merge_bt195_bt5422_lot(release_json, unpublished_identifier_data):
    """
    Merge the parsed unpublished identifier data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        unpublished_identifier_data (dict): The parsed unpublished identifier data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not unpublished_identifier_data:
        logger.warning(
            "No unpublished identifier data to merge for BT-195(BT-5422)-Lot"
        )
        return

    withheld_info = release_json.setdefault("withheldInformation", [])
    withheld_info.extend(unpublished_identifier_data["withheldInformation"])

    logger.info("Merged unpublished identifier data for BT-195(BT-5422)-Lot")
