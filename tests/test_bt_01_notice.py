# tests/test_bt_01_notice.py

import pytest
from src.ted_and_doffin_to_ocds.converters.eforms.bt_01_notice import (
    merge_procedure_legal_basis_regulatory_domain,
    parse_procedure_legal_basis_regulatory_domain,
)


def create_xml(content: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        {content}
    </ContractAwardNotice>
    """


def test_parse_procedure_legal_basis_regulatory_domain() -> None:
    xml_content = create_xml("<cbc:RegulatoryDomain>32014L0024</cbc:RegulatoryDomain>")

    result = parse_procedure_legal_basis_regulatory_domain(xml_content)

    assert result is not None
    assert result["tender"]["legalBasis"] == {
        "wasDerivedFrom": {"scheme": "CELEX", "id": "32014L0024"},
    }


def test_parse_procedure_legal_basis_regulatory_domain_other() -> None:
    xml_content = create_xml("<cbc:RegulatoryDomain>other</cbc:RegulatoryDomain>")

    assert parse_procedure_legal_basis_regulatory_domain(xml_content) is None


def test_parse_procedure_legal_basis_regulatory_domain_no_data() -> None:
    assert parse_procedure_legal_basis_regulatory_domain(create_xml("")) is None


def test_merge_procedure_legal_basis_regulatory_domain() -> None:
    release_json = {"tender": {"legalBasis": {"id": "dir201424"}}}

    merge_procedure_legal_basis_regulatory_domain(
        release_json,
        {
            "tender": {
                "legalBasis": {
                    "wasDerivedFrom": {"scheme": "CELEX", "id": "32014L0024"},
                },
            },
        },
    )

    assert release_json["tender"]["legalBasis"] == {
        "id": "dir201424",
        "wasDerivedFrom": {"scheme": "CELEX", "id": "32014L0024"},
    }


if __name__ == "__main__":
    pytest.main()
