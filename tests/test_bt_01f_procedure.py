# tests/test_bt_01f_procedure.py

import pytest
from src.ted_and_doffin_to_ocds.converters.eforms.bt_01f_procedure import (
    merge_procedure_legal_basis_noid_description,
    parse_procedure_legal_basis_noid_description,
)


def create_xml(content: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingTerms>{content}</cac:TenderingTerms>
    </ContractAwardNotice>
    """


def test_parse_procedure_legal_basis_noid_description() -> None:
    xml_content = create_xml(
        """
        <cac:ProcurementLegislationDocumentReference>
            <cbc:ID>LocalLegalBasis</cbc:ID>
            <cbc:DocumentDescription languageID="ENG">Local procurement law</cbc:DocumentDescription>
            <cbc:DocumentDescription languageID="FRA">Loi locale sur les marchés publics</cbc:DocumentDescription>
        </cac:ProcurementLegislationDocumentReference>
        """
    )

    result = parse_procedure_legal_basis_noid_description(xml_content)

    assert result is not None
    assert result["tender"]["legalBasis"] == {
        "description": "Local procurement law",
        "multilingualDescriptions": [
            {"language": "ENG", "text": "Local procurement law"},
            {"language": "FRA", "text": "Loi locale sur les marchés publics"},
        ],
    }


def test_parse_procedure_legal_basis_noid_description_ignores_identified_basis() -> None:
    xml_content = create_xml(
        """
        <cac:ProcurementLegislationDocumentReference>
            <cbc:ID schemeName="ELI">dir201424</cbc:ID>
            <cbc:DocumentDescription>Directive 2014/24/EU</cbc:DocumentDescription>
        </cac:ProcurementLegislationDocumentReference>
        """
    )

    assert parse_procedure_legal_basis_noid_description(xml_content) is None


def test_parse_procedure_legal_basis_noid_description_no_data() -> None:
    assert parse_procedure_legal_basis_noid_description(create_xml("")) is None


def test_merge_procedure_legal_basis_noid_description() -> None:
    release_json = {"tender": {"legalBasis": {"id": "LocalLegalBasis"}}}

    merge_procedure_legal_basis_noid_description(
        release_json,
        {"tender": {"legalBasis": {"description": "Local procurement law"}}},
    )

    assert release_json["tender"]["legalBasis"] == {
        "id": "LocalLegalBasis",
        "description": "Local procurement law",
    }


if __name__ == "__main__":
    pytest.main()
