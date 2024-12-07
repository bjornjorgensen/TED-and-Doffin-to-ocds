# converters/bt_196_bt_09_procedure.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def bt_196_parse_unpublished_justification_bt_09_procedure(
    xml_content: str | bytes,
) -> dict | None:
    """Parse the XML content to extract unpublished justification description.

    Processes XML content to find unpublished justification related to cross border law
    and creates a structured dictionary containing withheld information.

    Args:
        xml_content: The XML content to parse, either as string or bytes.

    Returns:
        Optional[Dict]: A dictionary containing withheld information with structure:
            {
                "withheldInformation": [
                    {
                        "rationale": str
                    }
                ]
            }
        Returns None if no relevant data is found.
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
        "/*/cac:TenderingTerms/cac:ProcurementLegislationDocumentReference"
        "[cbc:ID/text()='CrossBorderLaw']/ext:UBLExtensions/ext:UBLExtension"
        "/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy"
        "[efbc:FieldIdentifierCode/text()='cro-bor-law']"
        "/efbc:ReasonDescription/text()"
    )

    justification = root.xpath(xpath_query, namespaces=namespaces)

    if justification:
        withheld_item = {"rationale": justification[0]}
        result["withheldInformation"].append(withheld_item)

    return result if result["withheldInformation"] else None


def bt_196_merge_unpublished_justification_bt_09_procedure(
    release_json: dict, unpublished_justification_data: dict | None
) -> None:
    """Merge the parsed unpublished justification data into the main OCDS release JSON.

    Takes the unpublished justification data and merges it into the main OCDS release JSON
    by updating the withheldInformation array's first item with the rationale.

    Args:
        release_json: The main OCDS release JSON to be updated.
        unpublished_justification_data: The parsed unpublished justification data to be merged.
            Should contain a 'withheldInformation' list of dictionaries with rationale.

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
