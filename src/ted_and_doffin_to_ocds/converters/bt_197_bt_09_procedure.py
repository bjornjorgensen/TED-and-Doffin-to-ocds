# converters/bt_197_bt_09_procedure.py

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


def bt_197_parse_unpublished_justification_code_bt_09_procedure(
    xml_content: str | bytes,
) -> dict | None:
    """
    Parse the XML content to extract the unpublished justification code for the procedure.

    This function extracts BT-197 (justification code) data related to BT-09 (Procedure) from the XML.
    It looks for FieldsPrivacy elements containing codes for why certain information is withheld.

    Args:
        xml_content: The XML content to parse, either as a string or bytes object.
            Must be valid XML containing eForms namespaces and procedure data.

    Returns:
        Optional[Dict]: A dictionary containing the parsed unpublished justification code data in the format:
            {
                "withheldInformation": [
                    {
                        "rationaleClassifications": [
                            {
                                "scheme": "non-publication-justification",
                                "id": "code",
                                "description": "Description text",
                                "uri": "URI"
                            }
                        ]
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

    xpath_query = "/*/cac:TenderingTerms/cac:ProcurementLegislationDocumentReference[cbc:ID/text()='CrossBorderLaw']/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='cro-bor-law']/cbc:ReasonCode"

    reason_code_elements = root.xpath(xpath_query, namespaces=namespaces)

    for reason_code_element in reason_code_elements:
        code = reason_code_element.text
        if code in NON_PUBLICATION_JUSTIFICATION:
            withheld_info = {
                "rationaleClassifications": [
                    {
                        "scheme": "non-publication-justification",
                        "id": code,
                        "description": NON_PUBLICATION_JUSTIFICATION[code][
                            "description"
                        ],
                        "uri": NON_PUBLICATION_JUSTIFICATION[code]["uri"],
                    }
                ]
            }
            result["withheldInformation"].append(withheld_info)

    if not result["withheldInformation"]:
        logger.debug(
            "No unpublished justification code data found for BT-197(BT-09) Procedure"
        )
        return None

    return result


def bt_197_merge_unpublished_justification_code_bt_09_procedure(
    release_json: dict,
    unpublished_justification_code_data: dict | None,
) -> None:
    """
    Merge the parsed unpublished justification code data into the main OCDS release JSON.

    This function updates the withheldInformation array in the release_json with justification
    codes from unpublished fields related to procedure information.

    Args:
        release_json: The main OCDS release JSON document to be updated.
            Must be a mutable dictionary that may contain a withheldInformation array.
        unpublished_justification_code_data: The parsed unpublished justification code data to be merged.
            Should contain a withheldInformation array with objects having rationaleClassifications.
            Can be None, in which case no changes are made.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not unpublished_justification_code_data:
        logger.warning(
            "No unpublished justification code data to merge for BT-197(BT-09) Procedure",
        )
        return

    withheld_information = release_json.setdefault("withheldInformation", [])

    for item in unpublished_justification_code_data["withheldInformation"]:
        if withheld_information:
            withheld_information[0].setdefault("rationaleClassifications", []).extend(
                item["rationaleClassifications"],
            )
        else:
            withheld_information.append(item)

    logger.info(
        "Merged unpublished justification code data for BT-197(BT-09) Procedure",
    )
