# tests/test_bt_10_procedure_buyer.py

from pathlib import Path
import pytest
import json
import sys
import logging
import tempfile

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main, configure_logging


@pytest.fixture(scope="module")
def setup_logging():
    configure_logging()
    return logging.getLogger(__name__)


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


def test_bt_10_non_cofog_activity(tmp_path, setup_logging, temp_output_dir):
    """Test non-COFOG authority activity classification (gas-oil case)"""
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
        xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:ContractingParty>
            <cac:Party>
                <cac:PartyIdentification>
                    <cbc:ID schemeName="organization">ORG-0001</cbc:ID>
                </cac:PartyIdentification>
            </cac:Party>
            <cac:ContractingActivity>
                <cbc:ActivityTypeCode listName="authority-activity">gas-oil</cbc:ActivityTypeCode>
            </cac:ContractingActivity>
        </cac:ContractingParty>
    </ContractAwardNotice>
    """
    xml_file = tmp_path / "test_input_non_cofog_activity.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)
    logger.info("Result: %s", json.dumps(result, indent=2))

    # Check specific parts of the result structure
    assert "parties" in result, "Expected 'parties' in result"
    assert (
        len(result["parties"]) == 1
    ), f"Expected 1 party, got {len(result['parties'])}"

    party = result["parties"][0]
    assert party["id"] == "ORG-0001", "Incorrect party ID"
    assert "details" in party, "Missing details in party"
    assert (
        "classifications" in party["details"]
    ), "Missing classifications in party details"
    assert (
        len(party["details"]["classifications"]) == 1
    ), "Expected exactly one classification"

    classification = party["details"]["classifications"][0]
    assert classification["scheme"] == "eu-main-activity", "Incorrect scheme"
    assert classification["id"] == "gas-oil", "Incorrect classification ID"
    assert (
        classification["description"]
        == "Activities related to the exploitation of a geographical area for the purpose of extracting oil or gas."
    ), "Incorrect classification description"

    # Check that roles array contains 'buyer'
    assert "roles" in party, "Missing roles in party"
    assert "buyer" in party["roles"], "Missing 'buyer' role"


def test_bt_10_cofog_activity(tmp_path, setup_logging, temp_output_dir):
    """Test COFOG activity classification"""
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
        xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:ContractingParty>
            <cac:Party>
                <cac:PartyIdentification>
                    <cbc:ID schemeName="organization">ORG-0001</cbc:ID>
                </cac:PartyIdentification>
            </cac:Party>
            <cac:ContractingActivity>
                <cbc:ActivityTypeCode listName="authority-activity">gen-pub</cbc:ActivityTypeCode>
            </cac:ContractingActivity>
        </cac:ContractingParty>
    </ContractAwardNotice>
    """
    xml_file = tmp_path / "test_input_cofog_activity.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)
    logger.info("Result: %s", json.dumps(result, indent=2))

    assert "parties" in result
    party = result["parties"][0]

    # Check basic party structure
    assert party["id"] == "ORG-0001"
    assert "roles" in party, "Missing roles in party"
    assert "buyer" in party["roles"], "Missing 'buyer' role"
    assert "details" in party
    assert "classifications" in party["details"]

    # Check classification
    classification = party["details"]["classifications"][0]
    assert classification["scheme"] == "COFOG"
    assert classification["id"] == "01"
    assert classification["description"] == "General public services"


def test_bt_10_missing_activity(tmp_path, setup_logging, temp_output_dir):
    """Test missing activity code"""
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
        xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
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
    logger.info("Result: %s", json.dumps(result, indent=2))

    party = next(
        (party for party in result.get("parties", []) if party["id"] == "ORG-0001"),
        None,
    )
    if party:
        assert "details" not in party or "classifications" not in party.get(
            "details", {}
        ), "Did not expect classifications when activity is missing"


def test_bt_10_invalid_activity_code(tmp_path, setup_logging, temp_output_dir):
    """Test invalid activity code"""
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
        xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
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
    logger.info("Result: %s", json.dumps(result, indent=2))

    party = next(
        (party for party in result.get("parties", []) if party["id"] == "ORG-0001"),
        None,
    )
    if party:
        assert "details" not in party or "classifications" not in party.get(
            "details", {}
        ), "Did not expect classifications when activity code is invalid"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
