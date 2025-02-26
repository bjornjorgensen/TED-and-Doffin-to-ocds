# tests/test_bt_01_procedure.py

import pytest
from lxml import etree
from src.ted_and_doffin_to_ocds.converters.eforms.bt_01_procedure import (
    merge_procedure_legal_basis,
    parse_procedure_legal_basis,
    ELI_PREFIX,
)


def create_xml_with_namespace(content) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        {content}
    </root>
    """


def test_parse_procedure_legal_basis_with_eli() -> None:
    xml_content = create_xml_with_namespace("""
        <cac:ProcurementLegislationDocumentReference>
            <cbc:ID schemeName="ELI">dir201424</cbc:ID>
            <cbc:DocumentDescription>Directive 2014/24/EU</cbc:DocumentDescription>
        </cac:ProcurementLegislationDocumentReference>
    """)

    result = parse_procedure_legal_basis(xml_content)

    assert result is not None
    assert result["tender"]["legalBasis"]["scheme"] == "ELI"
    assert result["tender"]["legalBasis"]["id"] == "dir201424"
    assert result["tender"]["legalBasis"]["description"] == "Directive 2014/24/EU"


def test_parse_procedure_legal_basis_non_eli_id() -> None:
    xml_content = create_xml_with_namespace("""
        <cac:ProcurementLegislationDocumentReference>
            <cbc:ID schemeName="ELI">https://www.legislation.gov.uk/id/uksi/2015/102</cbc:ID>
            <cbc:DocumentDescription>UK procurement law</cbc:DocumentDescription>
        </cac:ProcurementLegislationDocumentReference>
    """)
    result = parse_procedure_legal_basis(xml_content)
    assert result is not None
    assert result["tender"]["legalBasis"]["scheme"] == "ELI"
    assert result["tender"]["legalBasis"]["id"] == "https://www.legislation.gov.uk/id/uksi/2015/102"
    assert result["tender"]["legalBasis"]["description"] == "UK procurement law"


def test_parse_procedure_legal_basis_with_eli_prefix() -> None:
    xml_content = create_xml_with_namespace(f"""
        <cac:ProcurementLegislationDocumentReference>
            <cbc:ID schemeName="IGNORED">{ELI_PREFIX}/2014/24</cbc:ID>
            <cbc:DocumentDescription>Directive 2014/24/EU</cbc:DocumentDescription>
        </cac:ProcurementLegislationDocumentReference>
    """)
    result = parse_procedure_legal_basis(xml_content)
    assert result is not None
    assert "scheme" not in result["tender"]["legalBasis"]  # Scheme should be ignored for ELI prefix
    assert result["tender"]["legalBasis"]["id"] == f"{ELI_PREFIX}/2014/24"


def test_parse_procedure_legal_basis_with_local_basis() -> None:
    xml_content = create_xml_with_namespace("""
        <cac:ProcurementLegislationDocumentReference>
            <cbc:ID>LocalLegalBasis</cbc:ID>
            <cbc:DocumentDescription>Local procurement law</cbc:DocumentDescription>
        </cac:ProcurementLegislationDocumentReference>
    """)

    result = parse_procedure_legal_basis(xml_content)

    assert result is not None
    assert "scheme" not in result["tender"]["legalBasis"]
    assert result["tender"]["legalBasis"]["id"] == "LocalLegalBasis"
    assert result["tender"]["legalBasis"]["description"] == "Local procurement law"


def test_parse_procedure_legal_basis_with_celex() -> None:
    xml_content = create_xml_with_namespace("""
        <cbc:RegulatoryDomain>32014L0024</cbc:RegulatoryDomain>
    """)

    result = parse_procedure_legal_basis(xml_content)

    assert result is not None
    assert result["tender"]["legalBasis"]["wasDerivedFrom"]["scheme"] == "CELEX"
    assert result["tender"]["legalBasis"]["wasDerivedFrom"]["id"] == "32014L0024"


def test_parse_procedure_legal_basis_multilingual() -> None:
    xml_content = create_xml_with_namespace("""
        <cac:ProcurementLegislationDocumentReference>
            <cbc:ID>LocalLegalBasis</cbc:ID>
            <cbc:DocumentDescription languageID="ENG">Local procurement law</cbc:DocumentDescription>
            <cbc:DocumentDescription languageID="FRA">Loi locale sur les marchés publics</cbc:DocumentDescription>
        </cac:ProcurementLegislationDocumentReference>
    """)
    result = parse_procedure_legal_basis(xml_content)
    assert result is not None
    assert result["tender"]["legalBasis"]["id"] == "LocalLegalBasis"
    assert result["tender"]["legalBasis"]["description"] == "Local procurement law"
    assert "multilingualDescriptions" in result["tender"]["legalBasis"]
    assert len(result["tender"]["legalBasis"]["multilingualDescriptions"]) == 2
    assert result["tender"]["legalBasis"]["multilingualDescriptions"][0]["language"] == "ENG"
    assert result["tender"]["legalBasis"]["multilingualDescriptions"][1]["language"] == "FRA"


def test_parse_procedure_legal_basis_no_data() -> None:
    xml_content = create_xml_with_namespace("""
        <cac:SomeOtherElement>
            <cbc:ID>SomeID</cbc:ID>
        </cac:SomeOtherElement>
    """)

    result = parse_procedure_legal_basis(xml_content)

    assert result is None


def test_parse_procedure_legal_basis_xml_error() -> None:
    # Test with invalid XML to check error handling
    xml_content = "<?xml version='1.0'><invalid>"
    result = parse_procedure_legal_basis(xml_content)
    assert result is None


def test_merge_procedure_legal_basis() -> None:
    release_json = {"tender": {"legalBasis": {"scheme": "ELI", "id": "old_id"}}}

    legal_basis_data = {
        "tender": {
            "legalBasis": {
                "scheme": "CELEX",
                "id": "new_id",
                "description": "New description",
            },
        },
    }

    merge_procedure_legal_basis(release_json, legal_basis_data)

    assert release_json["tender"]["legalBasis"]["scheme"] == "CELEX"
    assert release_json["tender"]["legalBasis"]["id"] == "new_id"
    assert release_json["tender"]["legalBasis"]["description"] == "New description"


def test_merge_procedure_legal_basis_no_data() -> None:
    release_json = {"tender": {"legalBasis": {"scheme": "ELI", "id": "old_id"}}}

    merge_procedure_legal_basis(release_json, None)

    assert release_json["tender"]["legalBasis"]["scheme"] == "ELI"
    assert release_json["tender"]["legalBasis"]["id"] == "old_id"


def test_merge_procedure_legal_basis_with_multilingual() -> None:
    release_json = {"tender": {}}
    legal_basis_data = {
        "tender": {
            "legalBasis": {
                "scheme": "ELI",
                "id": "test_id",
                "description": "Main description",
                "multilingualDescriptions": [
                    {"language": "ENG", "text": "English description"},
                    {"language": "FRA", "text": "French description"}
                ]
            },
        },
    }
    merge_procedure_legal_basis(release_json, legal_basis_data)
    assert release_json["tender"]["legalBasis"]["scheme"] == "ELI"
    assert release_json["tender"]["legalBasis"]["multilingualDescriptions"][0]["language"] == "ENG"
    assert release_json["tender"]["legalBasis"]["multilingualDescriptions"][1]["text"] == "French description"


if __name__ == "__main__":
    pytest.main()
