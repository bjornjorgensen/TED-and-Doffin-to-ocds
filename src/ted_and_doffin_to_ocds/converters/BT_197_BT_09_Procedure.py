# converters/BT_197_BT_09_Procedure.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

# Authority table for non-publication-justification codes
NON_PUBLICATION_JUSTIFICATION = {
    "eo-int": {
        "description": "Commercial interests of an economic operator",
        "uri": "http://publications.europa.eu/resource/authority/non-publication-justification/eo-int",
    },
    "fair-comp": {
        "description": "Fair competition",
        "uri": "http://publications.europa.eu/resource/authority/non-publication-justification/fair-comp",
    },
    "law-enf": {
        "description": "Law enforcement",
        "uri": "http://publications.europa.eu/resource/authority/non-publication-justification/law-enf",
    },
    "oth-int": {
        "description": "Other public interest",
        "uri": "http://publications.europa.eu/resource/authority/non-publication-justification/oth-int",
    },
    "rd-ser": {
        "description": "Research and development (R&D) services",
        "uri": "http://publications.europa.eu/resource/authority/non-publication-justification/rd-ser",
    },
}


def bt_197_parse_unpublished_justification_code_bt_09_procedure(xml_content):
    """
    Parse the XML content to extract the unpublished justification code for the procedure.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed unpublished justification code data.
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

    reason_code = root.xpath(
        "//cac:TenderingTerms/cac:ProcurementLegislationDocumentReference[cbc:ID/text()='CrossBorderLaw']/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='cro-bor-law']/cbc:ReasonCode/text()",
        namespaces=namespaces,
    )

    if reason_code:
        code = reason_code[0]
        if code in NON_PUBLICATION_JUSTIFICATION:
            withheld_item = {
                "rationaleClassifications": [
                    {
                        "scheme": "non-publication-justification",
                        "id": code,
                        "description": NON_PUBLICATION_JUSTIFICATION[code][
                            "description"
                        ],
                        "uri": NON_PUBLICATION_JUSTIFICATION[code]["uri"],
                    },
                ],
            }
            result["withheldInformation"].append(withheld_item)

    return result if result["withheldInformation"] else None


def bt_197_merge_unpublished_justification_code_bt_09_procedure(
    release_json, unpublished_justification_code_data,
):
    """
    Merge the parsed unpublished justification code data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        unpublished_justification_code_data (dict): The parsed unpublished justification code data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not unpublished_justification_code_data:
        logger.warning("No unpublished justification code data to merge")
        return

    withheld_information = release_json.setdefault("withheldInformation", [])

    for item in unpublished_justification_code_data["withheldInformation"]:
        if withheld_information:
            withheld_information[0].setdefault("rationaleClassifications", []).extend(
                item["rationaleClassifications"],
            )
        else:
            withheld_information.append(item)

    logger.info("Merged unpublished justification code data")
