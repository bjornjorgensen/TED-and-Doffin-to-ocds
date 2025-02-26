"""Tests for BT-10 Authority Activity parser.

Tests the parsing and conversion of contracting authority main activities 
to OCDS party classifications using both COFOG and EU-specific schemes.
"""

import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import configure_logging, main


@pytest.fixture(scope="module")
def setup_logging():
    logger = logging.getLogger(__name__)
    logger.disabled = True
    return logger


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


def run_main_and_get_result(xml_file, output_dir):
    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    output_files = list(output_dir.glob("*.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_10_multiple_authorities(tmp_path, setup_logging, temp_output_dir) -> None:
    """Test handling multiple contracting authorities with different activities"""
    logger = setup_logging
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
            <cac:ContractingActivity>
                <cbc:ActivityTypeCode listName="authority-activity">health</cbc:ActivityTypeCode>
            </cac:ContractingActivity>
        </cac:ContractingParty>
        <cac:ContractingParty>
            <cac:Party>
                <cac:PartyIdentification>
                    <cbc:ID schemeName="organization">ORG-0002</cbc:ID>
                </cac:PartyIdentification>
            </cac:Party>
            <cac:ContractingActivity>
                <cbc:ActivityTypeCode listName="authority-activity">gas-oil</cbc:ActivityTypeCode>
            </cac:ContractingActivity>
        </cac:ContractingParty>
    </ContractAwardNotice>
    """
    xml_file = tmp_path / "test_input_multiple_authorities.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Verify results
    assert "parties" in result
    assert len(result["parties"]) == 2

    # Check COFOG authority
    health_party = next(p for p in result["parties"] if p["id"] == "ORG-0001")
    assert health_party["details"]["classifications"][0] == {
        "scheme": "COFOG",
        "id": "07",
        "description": "Health"
    }
    assert "buyer" in health_party["roles"]

    # Check non-COFOG authority
    gas_oil_party = next(p for p in result["parties"] if p["id"] == "ORG-0002")
    assert gas_oil_party["details"]["classifications"][0] == {
        "scheme": "eu-main-activity",
        "id": "gas-oil",
        "description": "Activities related to the exploitation of a geographical area for the purpose of extracting oil or gas."
    }
    assert "buyer" in gas_oil_party["roles"]


def test_bt_10_missing_activity(tmp_path, setup_logging, temp_output_dir) -> None:
    """Test handling a contracting party with no activity code"""
    logger = setup_logging
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
        </cac:ContractingParty>
    </ContractAwardNotice>
    """
    xml_file = tmp_path / "test_input_missing_activity.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)
    party = next((p for p in result.get("parties", []) if p["id"] == "ORG-0001"), None)
    
    # Party should exist but without classifications
    assert party is not None
    assert "details" not in party or "classifications" not in party.get("details", {})
    assert "buyer" in party.get("roles", [])


def test_bt_10_invalid_activity_code(tmp_path, setup_logging, temp_output_dir) -> None:
    """Test handling invalid activity code"""
    logger = setup_logging
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
            <cac:ContractingActivity>
                <cbc:ActivityTypeCode listName="authority-activity">invalid-code</cbc:ActivityTypeCode>
            </cac:ContractingActivity>
        </cac:ContractingParty>
    </ContractAwardNotice>
    """
    xml_file = tmp_path / "test_input_invalid_activity.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)
    party = next((p for p in result.get("parties", []) if p["id"] == "ORG-0001"), None)
    
    # Party should exist but without classifications due to invalid code
    assert party is not None
    assert "details" not in party or "classifications" not in party.get("details", {})
    assert "buyer" in party.get("roles", [])


def test_bt_10_invalid_xml(tmp_path, setup_logging, temp_output_dir) -> None:
    """Test handling invalid XML"""
    logger = setup_logging
    xml_content = "Invalid XML content"
    xml_file = tmp_path / "test_input_invalid_xml.xml"
    xml_file.write_text(xml_content)

    with pytest.raises(ValueError, match="Empty XML document"):
        run_main_and_get_result(xml_file, temp_output_dir)


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
