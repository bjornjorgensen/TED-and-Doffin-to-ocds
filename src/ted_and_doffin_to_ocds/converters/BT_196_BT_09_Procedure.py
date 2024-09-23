# converters/BT_196_BT_09_Procedure.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def bt_196_parse_unpublished_justification_bt_09_procedure(xml_content):
    """
    Parse the XML content to extract the unpublished justification description for the procedure.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed unpublished justification data.
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

    justification = root.xpath(
        "//cac:TenderingTerms/cac:ProcurementLegislationDocumentReference[cbc:ID/text()='CrossBorderLaw']/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='cro-bor-law']/efbc:ReasonDescription/text()",
        namespaces=namespaces,
    )

    if justification:
        withheld_item = {"rationale": justification[0]}
        result["withheldInformation"].append(withheld_item)

    return result if result["withheldInformation"] else None


def bt_196_merge_unpublished_justification_bt_09_procedure(
    release_json, unpublished_justification_data,
):
    """
    Merge the parsed unpublished justification data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        unpublished_justification_data (dict): The parsed unpublished justification data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not unpublished_justification_data:
        logger.warning("No unpublished justification data to merge")
        return

    withheld_information = release_json.setdefault("withheldInformation", [])

    for item in unpublished_justification_data["withheldInformation"]:
        if withheld_information:
            withheld_information[0]["rationale"] = item["rationale"]
        else:
            withheld_information.append(item)

    logger.info("Merged unpublished justification data")
