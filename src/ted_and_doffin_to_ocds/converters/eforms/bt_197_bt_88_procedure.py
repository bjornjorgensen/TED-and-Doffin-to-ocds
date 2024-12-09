# converters/bt_197_bt_88_procedure.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)

# Lookup table for justification codes
JUSTIFICATION_CODES = {
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


def parse_bt197_bt88_procedure_unpublished_justification_code(
    xml_content: str | bytes,
) -> dict | None:
    """Parse the XML content to extract the unpublished justification code for the procedure features.

    This function extracts BT-197 (justification code) data related to BT-88 (Procedure) from the XML.
    It looks for FieldsPrivacy elements containing codes for why certain procedure feature information is withheld.

    Args:
        xml_content: The XML content to parse, either as a string or bytes object.
            Must be valid XML containing eForms namespaces and procedure data.

    Returns:
        Optional[Dict]: A dictionary containing the parsed unpublished justification code data in the format:
            {
                "withheldInformation": [
                    {
                        "id": "pro-fea-{contract_id}",
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

    xpath_query = "/*/cac:TenderingProcess/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='pro-fea']/cbc:ReasonCode"

    reason_code_elements = root.xpath(xpath_query, namespaces=namespaces)

    for reason_code_element in reason_code_elements:
        code = reason_code_element.text
        if code in JUSTIFICATION_CODES:
            withheld_info = {
                "id": f"pro-fea-{contract_folder_id[0]}",
                "rationaleClassifications": [
                    {
                        "scheme": "non-publication-justification",
                        "id": code,
                        "description": JUSTIFICATION_CODES[code]["description"],
                        "uri": JUSTIFICATION_CODES[code]["uri"],
                    }
                ],
            }
            result["withheldInformation"].append(withheld_info)

    if not result["withheldInformation"]:
        logger.debug(
            "No unpublished justification code data found for BT-197(BT-88) Procedure"
        )
        return None

    return result


def merge_bt197_bt88_procedure_unpublished_justification_code(
    release_json: dict,
    unpublished_justification_code_data: dict | None,
) -> None:
    """Merge the parsed unpublished justification code data into the main OCDS release JSON.

    This function updates the withheldInformation array in the release_json with justification
    codes from unpublished fields related to procedure features.

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
            "No unpublished justification code data to merge for BT-197(BT-88) Procedure",
        )
        return

    withheld_info = release_json.setdefault("withheldInformation", [])

    for new_item in unpublished_justification_code_data["withheldInformation"]:
        existing_item = next(
            (item for item in withheld_info if item.get("id") == new_item["id"]),
            None,
        )
        if existing_item:
            existing_item.setdefault("rationaleClassifications", []).extend(
                new_item["rationaleClassifications"]
            )
        else:
            withheld_info.append(new_item)

    logger.info(
        "Merged unpublished justification code data for BT-197(BT-88) Procedure",
    )
