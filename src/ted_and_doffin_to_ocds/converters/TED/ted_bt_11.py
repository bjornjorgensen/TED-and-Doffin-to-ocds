"""Converter for TED BT-11: Buyer legal type information for TED notices.

This module handles mapping of buyer legal type codes from TED format XML to OCDS party
classifications using the eu-buyer-legal-type scheme.
"""

import logging

from lxml import etree

from ted_and_doffin_to_ocds.converters.eforms.bt_11_procedure_buyer import (
    BUYER_LEGAL_TYPE_CODES,
    NAMESPACES,
)

logger = logging.getLogger(__name__)


def parse_ted_buyer_legal_type(
    xml_content: str | bytes,
) -> dict[str, list[dict]] | None:
    """Parse buyer legal type information from TED XML and map to OCDS classifications.

    Extracts the organization ID and buyer legal type using various TED XPath expressions.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    try:
        root = etree.fromstring(xml_content)
    except Exception:
        logger.exception("Error parsing XML")
        return None

    org_id_results = root.xpath(
        "//cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()",
        namespaces=NAMESPACES,
    )
    if not org_id_results:
        logger.warning("Organization ID not found")
        return None
    org_id = org_id_results[0]

    xpaths = [
        "TED_EXPORT/FORM_SECTION/F01_2014/CONTRACTING_BODY/CA_TYPE",
        "TED_EXPORT/FORM_SECTION/F02_2014/CONTRACTING_BODY/CA_TYPE",
        "TED_EXPORT/FORM_SECTION/F03_2014/CONTRACTING_BODY/CA_TYPE",
        "TED_EXPORT/FORM_SECTION/F08_2014/CONTRACTING_BODY/CA_TYPE/@VALUE",
        "TED_EXPORT/FORM_SECTION/F12_2014/CONTRACTING_BODY/CA_TYPE",
        "TED_EXPORT/FORM_SECTION/F13_2014/CONTRACTING_BODY/CA_TYPE",
        "TED_EXPORT/FORM_SECTION/F15_2014/CONTRACTING_BODY/CA_TYPE",
        "TED_EXPORT/FORM_SECTION/PRIOR_INFORMATION_DEFENCE/FD_PRIOR_INFORMATION_DEFENCE/AUTHORITY_PRIOR_INFORMATION_DEFENCE/TYPE_AND_ACTIVITIES_OR_CONTRACTING_ENTITY_AND_PURCHASING_ON_BEHALF/TYPE_AND_ACTIVITIES/*[matches(name(),'TYPE_OF_CONTRACTING_AUTHORITY')]/@VALUE",
        "TED_EXPORT/FORM_SECTION/CONTRACT_DEFENCE/FD_CONTRACT_DEFENCE/CONTRACTING_AUTHORITY_INFORMATION_DEFENCE/TYPE_AND_ACTIVITIES_OR_CONTRACTING_ENTITY_AND_PURCHASING_ON_BEHALF/TYPE_AND_ACTIVITIES/*[matches(name(),'TYPE_OF_CONTRACTING_AUTHORITY')]/@VALUE",
        "TED_EXPORT/FORM_SECTION/F21_2014/CONTRACTING_BODY/CA_TYPE",
        "TED_EXPORT/FORM_SECTION/F23_2014/CONTRACTING_BODY/CA_TYPE",
        "TED_EXPORT/FORM_SECTION/F24_2014/CONTRACTING_BODY/CA_TYPE",
    ]

    legal_type = None
    for xp in xpaths:
        try:
            result = root.xpath(xp, namespaces=NAMESPACES)
        except Exception:
            logger.exception("Error evaluating xpath '%s'", xp)
            continue
        if result:
            candidate = result[0].strip() if isinstance(result[0], str) else None
            if candidate:
                legal_type = candidate
                break

    if not legal_type:
        logger.warning("Buyer legal type not found via TED paths")
        return None

    description = BUYER_LEGAL_TYPE_CODES.get(legal_type, "Unknown buyer legal type")

    return {
        "parties": [
            {
                "id": org_id,
                "details": {
                    "classifications": [
                        {
                            "scheme": "eu-buyer-legal-type",
                            "id": legal_type,
                            "description": description,
                        }
                    ]
                },
            }
        ]
    }


if __name__ == "__main__":
    # For testing purposes
    import sys

    content = sys.stdin.read()
    result = parse_ted_buyer_legal_type(content)
    logger.info("Result: %s", result)
