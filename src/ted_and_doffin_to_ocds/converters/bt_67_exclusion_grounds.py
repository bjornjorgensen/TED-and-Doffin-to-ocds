# converters/bt_67_Exclusion_Grounds.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

EXCLUSION_GROUND_MAPPING = {
    "bankr-nat": "Analogous situation like bankruptcy under national law",
    "bankruptcy": "Bankruptcy",
    "corruption": "Corruption",
    "cred-arran": "Arrangement with creditors",
    "crime-org": "participation in a criminal organisation",
    "distorsion": "Agreements with other economic operators aimed at distorting competition",
    "envir-law": "Breaching of obligations in the fields of environmental law",
    "finan-laund": "Money laundering or terrorist financing",
    "fraud": "Fraud",
    "human-traffic": "Child labour and other forms of trafficking in human beings",
    "insolvency": "Insolvency",
    "labour-law": "Breaching of obligations in the fields of labour law",
    "liq-admin": "Assets being administered by liquidator",
    "misrepresent": "Guilty of misrepresentation, withheld information, unable to provide required documents and obtained confidential information of this procedure",
    "nati-ground": "Purely national exclusion grounds",
    "partic-confl": "Conflict of interest due to its participation in the procurement procedure",
    "prep-confl": "Direct or indirect involvement in the preparation of this procurement procedure",
    "prof-misconduct": "Guilty of grave professional misconduct",
    "sanction": "Early termination, damages or other comparable sanctions",
    "socsec-law": "Breaching of obligations in the fields of social law",
    "socsec-pay": "Payment of social security contributions",
    "susp-act": "Business activities are suspended",
    "tax-pay": "Payment of taxes",
    "terr-offence": "Terrorist offences or offences linked to terrorist activities",
}


def parse_exclusion_grounds(xml_content):
    """
    Parse the XML content to extract exclusion grounds information.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed exclusion grounds data.
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

    result = {"tender": {"exclusionGrounds": {"criteria": []}}}

    exclusion_grounds = root.xpath(
        "//cac:TenderingTerms/cac:TendererQualificationRequest/cac:SpecificTendererRequirement",
        namespaces=namespaces,
    )

    for ground in exclusion_grounds:
        type_code = ground.xpath(
            "cbc:TendererRequirementTypeCode[@listName='exclusion-ground']/text()",
            namespaces=namespaces,
        )
        description = ground.xpath("cbc:Description/text()", namespaces=namespaces)

        if type_code:
            criterion = {
                "type": type_code[0],
                "description": EXCLUSION_GROUND_MAPPING.get(type_code[0], ""),
            }

            if description:
                criterion["description"] += f": {description[0]}"

            result["tender"]["exclusionGrounds"]["criteria"].append(criterion)

    return result if result["tender"]["exclusionGrounds"]["criteria"] else None


def merge_exclusion_grounds(release_json, exclusion_grounds_data):
    """
    Merge the parsed exclusion grounds data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        exclusion_grounds_data (dict): The parsed exclusion grounds data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not exclusion_grounds_data:
        logger.warning("No exclusion grounds data to merge")
        return

    tender = release_json.setdefault("tender", {})
    exclusion_grounds = tender.setdefault("exclusionGrounds", {})
    criteria = exclusion_grounds.setdefault("criteria", [])

    criteria.extend(exclusion_grounds_data["tender"]["exclusionGrounds"]["criteria"])

    logger.info(f"Merged exclusion grounds data: {len(criteria)} criteria added")
