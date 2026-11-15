# tests/test_bt_01d_procedure.py

import pytest
from src.ted_and_doffin_to_ocds.converters.eforms.bt_01d_procedure import (
    merge_procedure_legal_basis_description,
    parse_procedure_legal_basis_description,
)


def create_xml(content: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingTerms>{content}</cac:TenderingTerms>
    </ContractAwardNotice>
    """


def test_parse_procedure_legal_basis_description() -> None:
    xml_content = create_xml(
        """
        <cac:ProcurementLegislationDocumentReference>
            <cbc:ID schemeName="ELI">dir201424</cbc:ID>
            <cbc:DocumentDescription languageID="ENG">Directive 2014/24/EU</cbc:DocumentDescription>
            <cbc:DocumentDescription languageID="FRA">Directive 2014/24/UE</cbc:DocumentDescription>
        </cac:ProcurementLegislationDocumentReference>
        """
    )

    result = parse_procedure_legal_basis_description(xml_content)

    assert result is not None
    assert result["tender"]["legalBasis"] == {
        "description": "Directive 2014/24/EU",
        "multilingualDescriptions": [
            {"language": "ENG", "text": "Directive 2014/24/EU"},
            {"language": "FRA", "text": "Directive 2014/24/UE"},
        ],
    }


def test_parse_procedure_legal_basis_description_without_language() -> None:
    xml_content = create_xml(
        """
        <cac:ProcurementLegislationDocumentReference>
            <cbc:ID>Anskaffelsesforskriften</cbc:ID>
            <cbc:DocumentDescription>Norwegian procurement law</cbc:DocumentDescription>
        </cac:ProcurementLegislationDocumentReference>
        """
    )

    result = parse_procedure_legal_basis_description(xml_content)

    assert result is not None
    assert result["tender"]["legalBasis"] == {
        "description": "Norwegian procurement law",
    }


@pytest.mark.parametrize("identifier", ["CrossBorderLaw", "LocalLegalBasis"])
def test_parse_procedure_legal_basis_description_skips_reserved_identifiers(
    identifier: str,
) -> None:
    xml_content = create_xml(
        f"""
        <cac:ProcurementLegislationDocumentReference>
            <cbc:ID>{identifier}</cbc:ID>
            <cbc:DocumentDescription>Other description</cbc:DocumentDescription>
        </cac:ProcurementLegislationDocumentReference>
        """
    )

    assert parse_procedure_legal_basis_description(xml_content) is None


def test_parse_procedure_legal_basis_description_no_data() -> None:
    assert parse_procedure_legal_basis_description(create_xml("")) is None


def test_merge_procedure_legal_basis_description() -> None:
    release_json = {"tender": {"legalBasis": {"scheme": "ELI", "id": "dir201424"}}}

    merge_procedure_legal_basis_description(
        release_json,
        {"tender": {"legalBasis": {"description": "Directive 2014/24/EU"}}},
    )

    assert release_json["tender"]["legalBasis"] == {
        "scheme": "ELI",
        "id": "dir201424",
        "description": "Directive 2014/24/EU",
    }


if __name__ == "__main__":
    pytest.main()
