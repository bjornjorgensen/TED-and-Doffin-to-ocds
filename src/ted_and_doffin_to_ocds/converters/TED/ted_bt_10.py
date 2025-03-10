"""BT-10 Authority Activity converter for TED format.

Maps contracting authority main activities to OCDS party classifications.
Handles both COFOG and EU-specific activity classifications.
Also extracts contracting authority type information.
"""

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

# TED namespaces
NAMESPACES = {
    "ted": "http://publications.europa.eu/resource/schema/ted/R2.0.9/publication",
    "n2016": "http://publications.europa.eu/resource/schema/ted/2016/nuts",
    "n2016b": "http://publications.europa.eu/resource/schema/ted/2016/nuts",
    "xs": "http://www.w3.org/2001/XMLSchema",
}

# Mapping of TED activity codes to standard codes
TED_ACTIVITY_MAPPING = {
    "GENERAL_PUBLIC_SERVICES": "general_public_services",
    "DEFENCE": "defence",
    "PUBLIC_ORDER_AND_SAFETY": "public_order_safety",
    "ECONOMIC_AND_FINANCIAL_AFFAIRS": "economic_financial",
    "ENVIRONMENT": "environment",
    "HOUSING_AND_COMMUNITY_AMENITIES": "housing_community",
    "HEALTH": "health",
    "RECREATION_CULTURE_AND_RELIGION": "recreation_culture_religion",
    "EDUCATION": "education",
    "SOCIAL_PROTECTION": "social_protection",
    "OTHER": "other",
}

# Classification of the Functions of Government (COFOG) mappings
COFOG_TABLE = {
    "general_public_services": ("01", "General public services"),
    "defence": ("02", "Defence"),
    "public_order_safety": ("03", "Public order and safety"),
    "economic_financial": ("04", "Economic affairs"),
    "environment": ("05", "Environmental protection"),
    "housing_community": ("06", "Housing and community amenities"),
    "health": ("07", "Health"),
    "recreation_culture_religion": ("08", "Recreation, culture and religion"),
    "education": ("09", "Education"),
    "social_protection": ("10", "Social protection"),
}

# Authority-specific activity classifications (non-COFOG)
AUTHORITY_TABLE = {
    # For activities that don't have COFOG mappings
    "other": "Other activity",
}

# Contracting authority types
CA_TYPE_TABLE = {
    "MINISTRY": "Ministry or any other national or federal authority, including their regional or local subdivisions",
    "NATIONAL_AGENCY": "National or federal agency/office",
    "REGIONAL_AUTHORITY": "Regional or local authority",
    "REGIONAL_AGENCY": "Regional or local agency/office",
    "BODY_PUBLIC": "Body governed by public law",
    "EU_INSTITUTION": "European institution/agency or international organisation",
    "OTHER": "Other type",
}


def _extract_xpath_values(root, xpaths) -> list:
    """Helper function to extract values using multiple XPath expressions."""
    values = []
    for xpath in xpaths:
        found_values = root.xpath(xpath)
        if found_values:
            values.extend(found_values)
    return values


def _process_activity_codes(activity_codes, org_classifications, org_id) -> None:
    """Process activity codes and add appropriate classifications."""
    for activity_code in activity_codes:
        # Map TED activity code to standard code
        std_code = TED_ACTIVITY_MAPPING.get(activity_code)
        if not std_code:
            logger.warning("Unknown TED activity code: %s", activity_code)
            continue

        classification = None

        # Handle COFOG classifications
        if std_code in COFOG_TABLE:
            cofog_id, description = COFOG_TABLE[std_code]
            classification = {
                "scheme": "COFOG",
                "id": cofog_id,
                "description": description,
            }
        # Handle non-COFOG classifications
        elif std_code in AUTHORITY_TABLE:
            classification = {
                "scheme": "eu-main-activity",
                "id": std_code,
                "description": AUTHORITY_TABLE.get(
                    std_code, f"Activity code: {std_code}"
                ),
            }
        elif std_code == "other":
            classification = {
                "scheme": "eu-main-activity",
                "id": "other",
                "description": "Other activity",
            }

        if classification:
            if org_id not in org_classifications:
                org_classifications[org_id] = []
            org_classifications[org_id].append(classification)


def _process_ca_types(ca_types, ca_type_others, org_classifications, org_id) -> None:
    """Process contracting authority types and add appropriate classifications."""
    for ca_type in ca_types:
        if ca_type in CA_TYPE_TABLE:
            classification = {
                "scheme": "TED_CA_TYPE",
                "id": ca_type,
                "description": CA_TYPE_TABLE[ca_type],
            }
            if org_id not in org_classifications:
                org_classifications[org_id] = []
            org_classifications[org_id].append(classification)

    # Process "other" type descriptions
    if ca_type_others and "OTHER" in ca_types:
        classification = {
            "scheme": "TED_CA_TYPE",
            "description": ca_type_others[0].strip(),
        }
        if org_id not in org_classifications:
            org_classifications[org_id] = []
        org_classifications[org_id].append(classification)


def parse_authority_activity(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse the authority activity (BT-10) and authority type from TED XML content.

    Extracts authority activity codes and authority types for each contracting party and maps them
    to OCDS party classifications using appropriate schemes.

    Args:
        xml_content: XML string or bytes to parse

    Returns:
        Dictionary containing party classifications or None if no relevant data found
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)

    # Define XPaths for various TED form sections that contain activity information
    activity_xpaths = [
        # F01, F02, F03 forms (CA_ACTIVITY)
        "//TED_EXPORT/FORM_SECTION/F01_2014/CONTRACTING_BODY/CA_ACTIVITY/@VALUE",
        "//TED_EXPORT/FORM_SECTION/F02_2014/CONTRACTING_BODY/CA_ACTIVITY/@VALUE",
        "//TED_EXPORT/FORM_SECTION/F03_2014/CONTRACTING_BODY/CA_ACTIVITY/@VALUE",
        # F04, F05, F07 forms (CE_ACTIVITY)
        "//TED_EXPORT/FORM_SECTION/F04_2014/CONTRACTING_BODY/CE_ACTIVITY/@VALUE",
        "//TED_EXPORT/FORM_SECTION/F05_2014/CONTRACTING_BODY/CE_ACTIVITY/@VALUE",
        "//TED_EXPORT/FORM_SECTION/F07_2014/CONTRACTING_BODY/CE_ACTIVITY/@VALUE",
        # F08 form (both CA and CE activities)
        "//TED_EXPORT/FORM_SECTION/F08_2014/CONTRACTING_BODY/CA_ACTIVITY/@VALUE",
        "//TED_EXPORT/FORM_SECTION/F08_2014/CONTRACTING_BODY/CE_ACTIVITY/@VALUE",
        # F12, F13, F15 forms
        "//TED_EXPORT/FORM_SECTION/F12_2014/CONTRACTING_BODY/CA_ACTIVITY/@VALUE",
        "//TED_EXPORT/FORM_SECTION/F12_2014/CONTRACTING_BODY/CE_ACTIVITY/@VALUE",
        "//TED_EXPORT/FORM_SECTION/F13_2014/CONTRACTING_BODY/CA_ACTIVITY/@VALUE",
        "//TED_EXPORT/FORM_SECTION/F13_2014/CONTRACTING_BODY/CE_ACTIVITY/@VALUE",
        "//TED_EXPORT/FORM_SECTION/F15_2014/CONTRACTING_BODY/CA_ACTIVITY/@VALUE",
        "//TED_EXPORT/FORM_SECTION/F15_2014/CONTRACTING_BODY/CE_ACTIVITY/@VALUE",
        # Defense contract form
        "//TED_EXPORT/FORM_SECTION/CONTRACT_DEFENCE/FD_CONTRACT_DEFENCE/CONTRACTING_AUTHORITY_INFORMATION_DEFENCE/TYPE_AND_ACTIVITIES_OR_CONTRACTING_ENTITY_AND_PURCHASING_ON_BEHALF/*[matches(name(),'ACTIVITIES')]/*[matches(name(),'ACTIVITY')]/@VALUE",
        # F21, F22, F23, F24, F25 forms
        "//TED_EXPORT/FORM_SECTION/F21_2014/CONTRACTING_BODY/CA_ACTIVITY/@VALUE",
        "//TED_EXPORT/FORM_SECTION/F22_2014/CONTRACTING_BODY/CE_ACTIVITY/@VALUE",
        "//TED_EXPORT/FORM_SECTION/F23_2014/CONTRACTING_BODY/CA_ACTIVITY/@VALUE",
        "//TED_EXPORT/FORM_SECTION/F23_2014/CONTRACTING_BODY/CE_ACTIVITY/@VALUE",
        "//TED_EXPORT/FORM_SECTION/F24_2014/CONTRACTING_BODY/CA_ACTIVITY/@VALUE",
        "//TED_EXPORT/FORM_SECTION/F24_2014/CONTRACTING_BODY/CE_ACTIVITY/@VALUE",
        "//TED_EXPORT/FORM_SECTION/F25_2014/CONTRACTING_BODY/CA_ACTIVITY/@VALUE",
        "//TED_EXPORT/FORM_SECTION/F25_2014/CONTRACTING_BODY/CE_ACTIVITY/@VALUE",
    ]

    # Define XPaths for contracting authority types
    ca_type_xpaths = [
        "//TED_EXPORT/FORM_SECTION/F01_2014/CONTRACTING_BODY/CA_TYPE/@VALUE",
        "//TED_EXPORT/FORM_SECTION/F02_2014/CONTRACTING_BODY/CA_TYPE/@VALUE",
        "//TED_EXPORT/FORM_SECTION/F03_2014/CONTRACTING_BODY/CA_TYPE/@VALUE",
        "//TED_EXPORT/FORM_SECTION/F04_2014/CONTRACTING_BODY/CA_TYPE/@VALUE",
        "//TED_EXPORT/FORM_SECTION/F05_2014/CONTRACTING_BODY/CA_TYPE/@VALUE",
        "//TED_EXPORT/FORM_SECTION/F08_2014/CONTRACTING_BODY/CA_TYPE/@VALUE",
        "//TED_EXPORT/FORM_SECTION/F12_2014/CONTRACTING_BODY/CA_TYPE/@VALUE",
        "//TED_EXPORT/FORM_SECTION/F13_2014/CONTRACTING_BODY/CA_TYPE/@VALUE",
        "//TED_EXPORT/FORM_SECTION/F15_2014/CONTRACTING_BODY/CA_TYPE/@VALUE",
        "//TED_EXPORT/FORM_SECTION/F21_2014/CONTRACTING_BODY/CA_TYPE/@VALUE",
        "//TED_EXPORT/FORM_SECTION/F23_2014/CONTRACTING_BODY/CA_TYPE/@VALUE",
        "//TED_EXPORT/FORM_SECTION/F24_2014/CONTRACTING_BODY/CA_TYPE/@VALUE",
        "//TED_EXPORT/FORM_SECTION/F25_2014/CONTRACTING_BODY/CA_TYPE/@VALUE",
    ]

    # XPaths for other authority type text (when type is "OTHER")
    ca_type_other_xpaths = [
        "//TED_EXPORT/FORM_SECTION/F01_2014/CONTRACTING_BODY/CA_TYPE_OTHER/text()",
        "//TED_EXPORT/FORM_SECTION/F02_2014/CONTRACTING_BODY/CA_TYPE_OTHER/text()",
        "//TED_EXPORT/FORM_SECTION/F03_2014/CONTRACTING_BODY/CA_TYPE_OTHER/text()",
        "//TED_EXPORT/FORM_SECTION/F04_2014/CONTRACTING_BODY/CA_TYPE_OTHER/text()",
        "//TED_EXPORT/FORM_SECTION/F05_2014/CONTRACTING_BODY/CA_TYPE_OTHER/text()",
        "//TED_EXPORT/FORM_SECTION/F08_2014/CONTRACTING_BODY/CA_TYPE_OTHER/text()",
        "//TED_EXPORT/FORM_SECTION/F12_2014/CONTRACTING_BODY/CA_TYPE_OTHER/text()",
        "//TED_EXPORT/FORM_SECTION/F13_2014/CONTRACTING_BODY/CA_TYPE_OTHER/text()",
        "//TED_EXPORT/FORM_SECTION/F15_2014/CONTRACTING_BODY/CA_TYPE_OTHER/text()",
        "//TED_EXPORT/FORM_SECTION/F21_2014/CONTRACTING_BODY/CA_TYPE_OTHER/text()",
        "//TED_EXPORT/FORM_SECTION/F23_2014/CONTRACTING_BODY/CA_TYPE_OTHER/text()",
        "//TED_EXPORT/FORM_SECTION/F24_2014/CONTRACTING_BODY/CA_TYPE_OTHER/text()",
        "//TED_EXPORT/FORM_SECTION/F25_2014/CONTRACTING_BODY/CA_TYPE_OTHER/text()",
    ]

    # XPaths for organization IDs
    org_id_xpath = "//TED_EXPORT/CODED_DATA_SECTION/NOTICE_DATA/ISO_COUNTRY_CODE/text()"

    # Extract values using helper function
    activity_values = _extract_xpath_values(root, activity_xpaths)
    ca_type_values = _extract_xpath_values(root, ca_type_xpaths)
    ca_type_other_values = _extract_xpath_values(root, ca_type_other_xpaths)

    if not activity_values and not ca_type_values and not ca_type_other_values:
        logger.info("No authority activity or type data found in TED XML. Skipping.")
        return None

    # Get organization ID (country code is used as fallback organization ID in TED)
    org_id = root.xpath(org_id_xpath)
    if not org_id:
        logger.warning(
            "No organization ID found in TED XML. Using 'unknown' as fallback."
        )
        org_id_value = "unknown"
    else:
        org_id_value = org_id[0]

    result = {"parties": []}

    # Create a dictionary to track classifications by organization ID
    org_classifications = {}

    # Process activity codes and CA types
    _process_activity_codes(activity_values, org_classifications, org_id_value)
    _process_ca_types(
        ca_type_values, ca_type_other_values, org_classifications, org_id_value
    )

    # Create party objects from collected classifications
    for org_id, classifications in org_classifications.items():
        party_data = {
            "id": org_id,
            "details": {"classifications": classifications},
        }
        result["parties"].append(party_data)

    return result if result["parties"] else None


def merge_authority_activity(
    release_json: dict[str, Any], authority_activity_data: dict[str, Any] | None
) -> None:
    """Merge authority activity data into the release JSON.

    Updates party details with authority activity classifications.
    Preserves existing classifications while adding new ones.

    Args:
        release_json: The target release JSON to update
        authority_activity_data: The authority activity data to merge
    """
    if not authority_activity_data:
        logger.info("No authority activity data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in authority_activity_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )

        if existing_party:
            existing_details = existing_party.setdefault("details", {})
            existing_classifications = existing_details.setdefault(
                "classifications", []
            )
            new_classifications = new_party["details"]["classifications"]

            for new_classification in new_classifications:
                if not any(
                    cls["scheme"] == new_classification["scheme"]
                    and cls["id"] == new_classification["id"]
                    for cls in existing_classifications
                ):
                    existing_classifications.append(new_classification)
        else:
            existing_parties.append(new_party)

    logger.info(
        "Merged authority activity data for %d parties",
        len(authority_activity_data["parties"]),
    )
