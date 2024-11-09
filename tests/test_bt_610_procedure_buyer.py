# tests/test_bt_610_procedure_buyer.py
from pathlib import Path
import pytest
import json
import sys
import tempfile
import logging

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
    output_files = list(output_dir.glob("*_release_0.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_610_procedure_buyer_integration(tmp_path, setup_logging, temp_output_dir):
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
    xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cac:ContractingParty>
        <cac:ContractingActivity>
            <cbc:ActivityTypeCode listName="entity-activity">gas-oil</cbc:ActivityTypeCode>
        </cac:ContractingActivity>
        <cac:Party>
            <cac:PartyIdentification>
                <cbc:ID>ORG-0001</cbc:ID>
            </cac:PartyIdentification>
        </cac:Party>
    </cac:ContractingParty>
</ContractNotice>
"""
    xml_file = tmp_path / "test_input_activity_entity.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)
    logger.info("Result: %s", json.dumps(result, indent=2))

    assert "parties" in result, "Expected 'parties' in result"
    assert (
        len(result["parties"]) == 1
    ), f"Expected 1 party, got {len(result['parties'])}"

    party = result["parties"][0]
    assert party["id"] == "ORG-0001", f"Expected party id 'ORG-0001', got {party['id']}"
    assert "buyer" in party["roles"], "Expected 'buyer' in party roles"
    assert "details" in party, "Expected 'details' in party"
    assert (
        "classifications" in party["details"]
    ), "Expected 'classifications' in party details"
    assert (
        len(party["details"]["classifications"]) == 1
    ), f"Expected 1 classification, got {len(party['details']['classifications'])}"

    classification = party["details"]["classifications"][0]
    assert (
        classification["scheme"] == "eu-main-activity"
    ), f"Expected scheme 'eu-main-activity', got {classification['scheme']}"
    assert (
        classification["id"] == "gas-oil"
    ), f"Expected id 'gas-oil', got {classification['id']}"
    assert (
        classification["description"] == "Extraction of gas or oil"
    ), f"Expected description 'Extraction of gas or oil', got {classification['description']}"

    logger.info("Test bt_610_procedure_buyer_integration passed successfully.")


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
