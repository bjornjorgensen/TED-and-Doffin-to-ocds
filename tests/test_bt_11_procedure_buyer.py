# tests/test_bt_11_procedure_buyer.py
import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


def run_main_and_get_result(xml_file, output_dir):
    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    output_files = list(output_dir.glob("*_release_0.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_11_procedure_buyer_integration(
    tmp_path, temp_output_dir
) -> None:
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:ContractingParty>
            <cac:Party>
                <cac:PartyIdentification>
                    <cbc:ID schemeName="organization">ORG-0001</cbc:ID>
                </cac:PartyIdentification>
            </cac:Party>
            <cac:ContractingPartyType>
                <cbc:PartyTypeCode listName="buyer-legal-type">body-pl</cbc:PartyTypeCode>
            </cac:ContractingPartyType>
        </cac:ContractingParty>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_buyer_legal_type.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Verify the results
    assert "parties" in result
    assert len(result["parties"]) == 1
    party = result["parties"][0]
    assert party["id"] == "ORG-0001"
    assert "details" in party
    assert "classifications" in party["details"]
    assert len(party["details"]["classifications"]) == 1
    classification = party["details"]["classifications"][0]
    assert classification["scheme"] == "eu-buyer-legal-type"
    assert classification["id"] == "body-pl"
    assert classification["description"] == "Body governed by public law"

def test_multiple_buyer_legal_types(
    tmp_path, temp_output_dir
) -> None:
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:ContractingParty>
            <cac:Party>
                <cac:PartyIdentification>
                    <cbc:ID schemeName="organization">ORG-0001</cbc:ID>
                </cac:PartyIdentification>
            </cac:Party>
            <cac:ContractingPartyType>
                <cbc:PartyTypeCode listName="buyer-legal-type">cga</cbc:PartyTypeCode>
            </cac:ContractingPartyType>
        </cac:ContractingParty>
        <cac:ContractingParty>
            <cac:Party>
                <cac:PartyIdentification>
                    <cbc:ID schemeName="organization">ORG-0002</cbc:ID>
                </cac:PartyIdentification>
            </cac:Party>
            <cac:ContractingPartyType>
                <cbc:PartyTypeCode listName="buyer-legal-type">ra</cbc:PartyTypeCode>
            </cac:ContractingPartyType>
        </cac:ContractingParty>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_multiple_buyers.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Verify the results
    assert "parties" in result
    assert len(result["parties"]) == 2

    # Check first party
    party1 = next(p for p in result["parties"] if p["id"] == "ORG-0001")
    classification1 = party1["details"]["classifications"][0]
    assert classification1["scheme"] == "eu-buyer-legal-type"
    assert classification1["id"] == "cga"
    assert classification1["description"] == "Central government authority"

    # Check second party
    party2 = next(p for p in result["parties"] if p["id"] == "ORG-0002")
    classification2 = party2["details"]["classifications"][0]
    assert classification2["scheme"] == "eu-buyer-legal-type"
    assert classification2["id"] == "ra"
    assert classification2["description"] == "Regional authority"

def test_invalid_buyer_legal_type(
    tmp_path, temp_output_dir
) -> None:
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:ContractingParty>
            <cac:Party>
                <cac:PartyIdentification>
                    <cbc:ID schemeName="organization">ORG-0001</cbc:ID>
                </cac:PartyIdentification>
            </cac:Party>
            <cac:ContractingPartyType>
                <cbc:PartyTypeCode listName="buyer-legal-type">invalid-type</cbc:PartyTypeCode>
            </cac:ContractingPartyType>
        </cac:ContractingParty>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_invalid_type.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Verify the results
    assert "parties" in result
    assert len(result["parties"]) == 1
    party = result["parties"][0]
    assert party["id"] == "ORG-0001"
    classification = party["details"]["classifications"][0]
    assert classification["scheme"] == "eu-buyer-legal-type"
    assert classification["id"] == "invalid-type"
    assert classification["description"] == "Unknown buyer legal type"

if __name__ == "__main__":
    pytest.main(["-v"])
