# tests/test_bt_01e_procedure.py

import pytest
from src.ted_and_doffin_to_ocds.converters.eforms.bt_01e_procedure import (
    merge_procedure_legal_basis_noid,
    parse_procedure_legal_basis_noid,
)


def create_xml(content: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingTerms>{content}</cac:TenderingTerms>
    </ContractAwardNotice>
    """


def test_parse_procedure_legal_basis_noid() -> None:
    xml_content = create_xml(
        """
        <cac:ProcurementLegislationDocumentReference>
            <cbc:ID>LocalLegalBasis</cbc:ID>
            <cbc:DocumentDescription>Local procurement law</cbc:DocumentDescription>
        </cac:ProcurementLegislationDocumentReference>
        """
    )

    result = parse_procedure_legal_basis_noid(xml_content)

    assert result is not None
    assert result["tender"]["legalBasis"] == {"id": "LocalLegalBasis"}


def test_parse_procedure_legal_basis_noid_ignores_identified_legal_basis() -> None:
    xml_content = create_xml(
        """
        <cac:ProcurementLegislationDocumentReference>
            <cbc:ID schemeName="ELI">dir201424</cbc:ID>
        </cac:ProcurementLegislationDocumentReference>
        """
    )

    assert parse_procedure_legal_basis_noid(xml_content) is None


def test_parse_procedure_legal_basis_noid_no_data() -> None:
    assert parse_procedure_legal_basis_noid(create_xml("")) is None


def test_merge_procedure_legal_basis_noid() -> None:
    release_json = {"tender": {"legalBasis": {"scheme": "ELI", "id": "dir201424"}}}

    merge_procedure_legal_basis_noid(
        release_json,
        {"tender": {"legalBasis": {"id": "LocalLegalBasis"}}},
    )

    assert release_json["tender"]["legalBasis"] == {
        "scheme": "ELI",
        "id": "LocalLegalBasis",
    }


if __name__ == "__main__":
    pytest.main()
