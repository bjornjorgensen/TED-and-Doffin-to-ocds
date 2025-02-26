# tests/test_bt_610_procedure_buyer.py
import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.converters.eforms.bt_610_procedure_buyer import parse_activity_entity, merge_activity_entity
from src.ted_and_doffin_to_ocds.main import configure_logging, main

# Test constants
TEST_OCID_PREFIX = "ocds-test-prefix"
TEST_SCHEME = "test-scheme"
TEST_XML_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
    xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cac:ContractingParty>
        <cac:ContractingActivity>
            <cbc:ActivityTypeCode listName="entity-activity">{activity_code}</cbc:ActivityTypeCode>
        </cac:ContractingActivity>
        <cac:Party>
            <cac:PartyIdentification>
                <cbc:ID>{org_id}</cbc:ID>
            </cac:PartyIdentification>
        </cac:Party>
    </cac:ContractingParty>
</ContractNotice>
"""


@pytest.fixture(scope="module")
def setup_logging():
    configure_logging()
    return logging.getLogger(__name__)


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


def run_main_and_get_result(xml_file, output_dir):
    main(str(xml_file), str(output_dir), TEST_OCID_PREFIX, TEST_SCHEME)
    output_files = list(output_dir.glob("*_release_0.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


@pytest.mark.parametrize(
    ("activity_code", "org_id"),
    [
        ("gas-oil", "ORG-0001"),
        ("education", "ORG-0002"),  # COFOG activity
    ],
)
def test_bt_610_procedure_buyer_integration(
    activity_code, org_id, tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging

    # Generate test XML content
    xml_content = TEST_XML_TEMPLATE.format(activity_code=activity_code, org_id=org_id)
    xml_file = tmp_path / "test_input_activity_entity.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)
    logger.info("Result: %s", json.dumps(result, indent=2))

    # Verify base structure
    assert "parties" in result, "Expected 'parties' in result"
    assert (
        len(result["parties"]) == 1
    ), f"Expected 1 party, got {len(result['parties'])}"

    # Verify party details
    party = result["parties"][0]
    assert party["id"] == org_id, f"Expected party id '{org_id}', got {party['id']}"
    assert "buyer" in party["roles"], "Expected 'buyer' in party roles"
    assert "details" in party, "Expected 'details' in party"
    assert (
        "classifications" in party["details"]
    ), "Expected 'classifications' in party details"
    assert (
        len(party["details"]["classifications"]) == 1
    ), f"Expected 1 classification, got {len(party['details']['classifications'])}"

    # Verify classification
    classification = party["details"]["classifications"][0]
    if activity_code in AUTHORITY_TABLE:
        assert (
            classification["scheme"] == "eu-main-activity"
        ), f"Expected scheme 'eu-main-activity', got {classification['scheme']}"
        assert (
            classification["id"] == activity_code
        ), f"Expected id '{activity_code}', got {classification['id']}"
        assert (
            classification["description"] == AUTHORITY_TABLE[activity_code]
        ), "Expected description from AUTHORITY_TABLE"
    else:
        assert (
            classification["scheme"] == "COFOG"
        ), f"Expected scheme 'COFOG', got {classification['scheme']}"

    logger.info("Test bt_610_procedure_buyer_integration passed successfully.")


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
