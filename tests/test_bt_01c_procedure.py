# tests/test_bt_01c_procedure.py

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.converters.eforms.bt_01c_procedure import (
    ELI_PREFIXES,
    merge_procedure_legal_basis_id,
    parse_procedure_legal_basis_id,
)
from src.ted_and_doffin_to_ocds.main import main


def create_xml(content: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        {content}
    </ContractAwardNotice>
    """


def create_tendering_terms(content: str) -> str:
    return create_xml(f"<cac:TenderingTerms>{content}</cac:TenderingTerms>")


def test_parse_procedure_legal_basis_id() -> None:
    xml_content = create_tendering_terms(
        """
        <cac:ProcurementLegislationDocumentReference>
            <cbc:ID schemeName="ELI">https://www.legislation.gov.uk/id/uksi/2015/102</cbc:ID>
        </cac:ProcurementLegislationDocumentReference>
        """
    )

    result = parse_procedure_legal_basis_id(xml_content)

    assert result is not None
    assert result["tender"]["legalBasis"] == {
        "scheme": "ELI",
        "id": "https://www.legislation.gov.uk/id/uksi/2015/102",
    }


@pytest.mark.parametrize("eli_prefix", ELI_PREFIXES)
def test_parse_procedure_legal_basis_id_derives_eli_scheme(eli_prefix: str) -> None:
    xml_content = create_tendering_terms(
        f"""
        <cac:ProcurementLegislationDocumentReference>
            <cbc:ID>{eli_prefix}/2014/24/oj</cbc:ID>
        </cac:ProcurementLegislationDocumentReference>
        """
    )

    result = parse_procedure_legal_basis_id(xml_content)

    assert result is not None
    assert result["tender"]["legalBasis"] == {
        "scheme": "ELI",
        "id": f"{eli_prefix}/2014/24/oj",
    }


def test_parse_procedure_legal_basis_id_without_scheme_name() -> None:
    xml_content = create_tendering_terms(
        """
        <cac:ProcurementLegislationDocumentReference>
            <cbc:ID>Anskaffelsesforskriften</cbc:ID>
        </cac:ProcurementLegislationDocumentReference>
        """
    )

    result = parse_procedure_legal_basis_id(xml_content)

    assert result is not None
    assert result["tender"]["legalBasis"] == {"id": "Anskaffelsesforskriften"}


@pytest.mark.parametrize("identifier", ["CrossBorderLaw", "LocalLegalBasis"])
def test_parse_procedure_legal_basis_id_skips_reserved_identifiers(
    identifier: str,
) -> None:
    xml_content = create_tendering_terms(
        f"""
        <cac:ProcurementLegislationDocumentReference>
            <cbc:ID>{identifier}</cbc:ID>
        </cac:ProcurementLegislationDocumentReference>
        """
    )

    assert parse_procedure_legal_basis_id(xml_content) is None


def test_parse_procedure_legal_basis_id_requires_tendering_terms() -> None:
    xml_content = create_xml(
        """
        <cac:ProcurementProjectLot>
            <cac:ProcurementLegislationDocumentReference>
                <cbc:ID schemeName="ELI">dir201424</cbc:ID>
            </cac:ProcurementLegislationDocumentReference>
        </cac:ProcurementProjectLot>
        """
    )

    assert parse_procedure_legal_basis_id(xml_content) is None


def test_parse_procedure_legal_basis_id_invalid_xml() -> None:
    assert parse_procedure_legal_basis_id("<?xml version='1.0'><invalid>") is None


def test_merge_procedure_legal_basis_id() -> None:
    release_json = {
        "tender": {"legalBasis": {"description": "Directive 2014/24/EU"}},
    }

    merge_procedure_legal_basis_id(
        release_json,
        {"tender": {"legalBasis": {"scheme": "ELI", "id": "dir201424"}}},
    )

    assert release_json["tender"]["legalBasis"] == {
        "scheme": "ELI",
        "id": "dir201424",
        "description": "Directive 2014/24/EU",
    }


def test_merge_procedure_legal_basis_id_no_data() -> None:
    release_json = {"tender": {"legalBasis": {"id": "dir201424"}}}

    merge_procedure_legal_basis_id(release_json, None)

    assert release_json["tender"]["legalBasis"] == {"id": "dir201424"}


def test_bt_01c_procedure_integration(tmp_path) -> None:
    xml_content = create_xml(
        """
        <cbc:RegulatoryDomain>32014L0024</cbc:RegulatoryDomain>
        <cac:TenderingTerms>
            <cac:ProcurementLegislationDocumentReference>
                <cbc:ID schemeName="ELI">https://www.legislation.gov.uk/id/uksi/2015/102</cbc:ID>
                <cbc:DocumentDescription languageID="ENG">UK procurement law</cbc:DocumentDescription>
            </cac:ProcurementLegislationDocumentReference>
        </cac:TenderingTerms>
        """
    )
    xml_file = tmp_path / "notice.xml"
    xml_file.write_text(xml_content, encoding="utf-8")

    with tempfile.TemporaryDirectory() as output_dir:
        main(str(xml_file), output_dir, "ocds-test-prefix", "test-scheme")
        output_files = list(Path(output_dir).glob("*_release_0.json"))
        assert len(output_files) == 1
        release = json.loads(output_files[0].read_text(encoding="utf-8"))

    assert release["tender"]["legalBasis"] == {
        "id": "https://www.legislation.gov.uk/id/uksi/2015/102",
        "scheme": "ELI",
        "description": "UK procurement law",
        "multilingualDescriptions": [
            {"language": "ENG", "text": "UK procurement law"},
        ],
        "wasDerivedFrom": {"scheme": "CELEX", "id": "32014L0024"},
    }


if __name__ == "__main__":
    pytest.main()
