# converters/bt_01_procedure.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_procedure_legal_basis(xml_content):
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

    result = {"tender": {"legalBasis": {}}}

    # Parse legal basis ID
    legal_basis_id = root.xpath(
        "//cac:ProcurementLegislationDocumentReference[not(cbc:ID='CrossBorderLaw' or cbc:ID='LocalLegalBasis')]/cbc:ID",
        namespaces=namespaces,
    )
    if legal_basis_id:
        result["tender"]["legalBasis"]["scheme"] = "ELI"
        result["tender"]["legalBasis"]["id"] = legal_basis_id[0].text

    # Parse legal basis description
    legal_basis_description = root.xpath(
        "//cac:ProcurementLegislationDocumentReference[not(cbc:ID='CrossBorderLaw' or cbc:ID='LocalLegalBasis')]/cbc:DocumentDescription",
        namespaces=namespaces,
    )
    if legal_basis_description:
        result["tender"]["legalBasis"]["description"] = legal_basis_description[0].text

    # Parse legal basis NoID
    legal_basis_noid = root.xpath(
        "//cac:ProcurementLegislationDocumentReference[cbc:ID='LocalLegalBasis']/cbc:ID",
        namespaces=namespaces,
    )
    if legal_basis_noid:
        result["tender"]["legalBasis"]["id"] = legal_basis_noid[0].text

    # Parse legal basis NoID description
    legal_basis_noid_description = root.xpath(
        "//cac:ProcurementLegislationDocumentReference[cbc:ID='LocalLegalBasis']/cbc:DocumentDescription",
        namespaces=namespaces,
    )
    if legal_basis_noid_description:
        result["tender"]["legalBasis"]["description"] = legal_basis_noid_description[
            0
        ].text

    # Parse legal basis notice
    regulatory_domain = root.xpath("//cbc:RegulatoryDomain", namespaces=namespaces)
    if regulatory_domain:
        result["tender"]["legalBasis"]["scheme"] = "CELEX"
        result["tender"]["legalBasis"]["id"] = regulatory_domain[0].text

    if result["tender"]["legalBasis"]:
        logger.info("Parsed procedure Legal Basis data")
        return result
    logger.info("No procedure Legal Basis data found")
    return None


def merge_procedure_legal_basis(release_json, legal_basis_data) -> None:
    if not legal_basis_data:
        return

    tender = release_json.setdefault("tender", {})
    legal_basis = tender.setdefault("legalBasis", {})
    legal_basis.update(legal_basis_data["tender"]["legalBasis"])
    logger.info("Merged procedure Legal Basis data")
