# converters/bt_01_procedure.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

# Constants for XML namespaces
NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
    "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
}

# Constants for legal basis identifiers
CROSS_BORDER_LAW = "CrossBorderLaw"
LOCAL_LEGAL_BASIS = "LocalLegalBasis"
ELI_PREFIX = "http://data.europa.eu/eli/dir"
OTHER_VALUE = "other"

# XPath expressions
XPATH_LEGAL_BASIS_ID = f"//cac:ProcurementLegislationDocumentReference[not(cbc:ID='{CROSS_BORDER_LAW}' or cbc:ID='{LOCAL_LEGAL_BASIS}')]/cbc:ID"
XPATH_LEGAL_BASIS_DESC = f"//cac:ProcurementLegislationDocumentReference[not(cbc:ID='{CROSS_BORDER_LAW}' or cbc:ID='{LOCAL_LEGAL_BASIS}')]/cbc:DocumentDescription"
XPATH_LOCAL_LEGAL_BASIS_ID = f"//cac:ProcurementLegislationDocumentReference[cbc:ID='{LOCAL_LEGAL_BASIS}']/cbc:ID"
XPATH_LOCAL_LEGAL_BASIS_DESC = f"//cac:ProcurementLegislationDocumentReference[cbc:ID='{LOCAL_LEGAL_BASIS}']/cbc:DocumentDescription"
XPATH_REGULATORY_DOMAIN = "//cbc:RegulatoryDomain"


def _parse_multilingual_descriptions(descriptions: list) -> list:
    """
    Extract multilingual descriptions from XML nodes.

    Args:
        descriptions: List of description XML nodes

    Returns:
        List of dictionaries with language and text
    """
    multilingual_descriptions = []
    for desc in descriptions:
        lang_id = desc.get("languageID")
        if lang_id:
            multilingual_descriptions.append({"language": lang_id, "text": desc.text})
    return multilingual_descriptions


def _process_legal_basis_id(root: etree.Element, result: dict[str, Any]) -> None:
    """Process legal basis ID from XML."""
    legal_basis_nodes = root.xpath(XPATH_LEGAL_BASIS_ID, namespaces=NAMESPACES)
    if legal_basis_nodes:
        legal_basis_id = legal_basis_nodes[0].text
        result["tender"]["legalBasis"]["id"] = legal_basis_id
        # Only set scheme if ID doesn't start with ELI_PREFIX
        if not legal_basis_id.startswith(ELI_PREFIX):
            scheme = legal_basis_nodes[0].get("schemeName")
            if scheme:
                result["tender"]["legalBasis"]["scheme"] = scheme


def _process_legal_basis_description(
    root: etree.Element, result: dict[str, Any]
) -> None:
    """Process legal basis description from XML."""
    legal_basis_descriptions = root.xpath(XPATH_LEGAL_BASIS_DESC, namespaces=NAMESPACES)
    if legal_basis_descriptions:
        # For simple case, keep backward compatibility
        result["tender"]["legalBasis"]["description"] = legal_basis_descriptions[0].text

        # Store language-specific descriptions
        multilingual_descriptions = _parse_multilingual_descriptions(
            legal_basis_descriptions
        )
        if multilingual_descriptions:
            result["tender"]["legalBasis"]["multilingualDescriptions"] = (
                multilingual_descriptions
            )


def _process_legal_basis_noid(root: etree.Element, result: dict[str, Any]) -> None:
    """Process legal basis NoID from XML."""
    legal_basis_noid = root.xpath(XPATH_LOCAL_LEGAL_BASIS_ID, namespaces=NAMESPACES)
    if legal_basis_noid:
        result["tender"]["legalBasis"]["id"] = legal_basis_noid[0].text


def _process_legal_basis_noid_description(
    root: etree.Element, result: dict[str, Any]
) -> None:
    """Process legal basis NoID description from XML."""
    legal_basis_noid_descriptions = root.xpath(
        XPATH_LOCAL_LEGAL_BASIS_DESC, namespaces=NAMESPACES
    )
    if legal_basis_noid_descriptions:
        result["tender"]["legalBasis"]["description"] = legal_basis_noid_descriptions[
            0
        ].text

        # Store language-specific descriptions
        multilingual_descriptions = _parse_multilingual_descriptions(
            legal_basis_noid_descriptions
        )
        if multilingual_descriptions:
            result["tender"]["legalBasis"]["multilingualDescriptions"] = (
                multilingual_descriptions
            )


def _process_regulatory_domain(root: etree.Element, result: dict[str, Any]) -> None:
    """Process regulatory domain from XML."""
    regulatory_domain = root.xpath(XPATH_REGULATORY_DOMAIN, namespaces=NAMESPACES)
    if regulatory_domain and regulatory_domain[0].text != OTHER_VALUE:
        result["tender"]["legalBasis"]["wasDerivedFrom"] = {
            "scheme": "CELEX",
            "id": regulatory_domain[0].text,
        }


def parse_procedure_legal_basis(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """
    Parse legal basis information from XML content according to BT-01 specifications.

    Args:
        xml_content: The XML content to parse, either as string or bytes

    Returns:
        Dictionary containing legal basis information or None if no data found
    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = etree.fromstring(xml_content)

        result = {"tender": {"legalBasis": {}}}

        # Process each part of the legal basis
        _process_legal_basis_id(root, result)
        _process_legal_basis_description(root, result)
        _process_legal_basis_noid(root, result)
        _process_legal_basis_noid_description(root, result)
        _process_regulatory_domain(root, result)

        # Handle legal basis data
        if result["tender"]["legalBasis"]:
            logger.info("Parsed procedure Legal Basis data")
            return result

        logger.info("No procedure Legal Basis data found")
        return None  # noqa: TRY300

    except etree.XMLSyntaxError:
        logger.exception("XML parsing error")
        return None
    except Exception:
        logger.exception("Error parsing procedure legal basis")
        return None


def merge_procedure_legal_basis(
    release_json: dict[str, Any], legal_basis_data: dict[str, Any] | None
) -> None:
    """
    Merge legal basis data into the release JSON.

    Args:
        release_json: The release JSON to update
        legal_basis_data: The legal basis data to merge
    """
    if not legal_basis_data:
        return

    tender = release_json.setdefault("tender", {})
    legal_basis = tender.setdefault("legalBasis", {})
    legal_basis.update(legal_basis_data["tender"]["legalBasis"])
    logger.info("Merged procedure Legal Basis data")
