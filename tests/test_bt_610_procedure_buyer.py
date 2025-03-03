# tests/test_bt_610_procedure_buyer.py
import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.converters.eforms.bt_610_procedure_buyer import (
    parse_activity_entity, 
    merge_activity_entity,
    COFOG_MAPPING,
    AUTHORITY_TABLE
)
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
    # Logging disabled for tests
    logger = logging.getLogger(__name__)
    logger.disabled = True
    return logger


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
    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

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
        expected_id = COFOG_MAPPING[activity_code][0]
        expected_description = COFOG_MAPPING[activity_code][1]
        assert classification["id"] == expected_id, f"Expected COFOG id '{expected_id}', got {classification['id']}"
        assert classification["description"] == expected_description, f"Expected COFOG description '{expected_description}', got {classification['description']}"

    # logger.info("Test bt_610_procedure_buyer_integration passed successfully.") # Logging disabled


def test_parse_activity_entity_direct():
    """Test parse_activity_entity function directly with XML content."""
    # Generate test XML with both types of activities, including namespace declarations
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
    <cac:ContractingParty>
        <cac:ContractingActivity>
            <cbc:ActivityTypeCode listName="entity-activity">education</cbc:ActivityTypeCode>
        </cac:ContractingActivity>
        <cac:Party>
            <cac:PartyIdentification>
                <cbc:ID>ORG-0002</cbc:ID>
            </cac:PartyIdentification>
        </cac:Party>
    </cac:ContractingParty>
    <cac:ContractingParty>
        <cac:ContractingActivity>
            <cbc:ActivityTypeCode listName="entity-activity">invalid-code</cbc:ActivityTypeCode>
        </cac:ContractingActivity>
        <cac:Party>
            <cac:PartyIdentification>
                <cbc:ID>ORG-0003</cbc:ID>
            </cac:PartyIdentification>
        </cac:Party>
    </cac:ContractingParty>
</ContractNotice>
    """
    
    result = parse_activity_entity(xml_content)
    
    assert result is not None
    assert "parties" in result
    assert len(result["parties"]) == 2  # Only 2 valid activities (invalid-code is skipped)
    
    # Check first party (gas-oil)
    party1 = result["parties"][0]
    assert party1["id"] == "ORG-0001"
    assert party1["details"]["classifications"][0]["scheme"] == "eu-main-activity"
    assert party1["details"]["classifications"][0]["id"] == "gas-oil"
    
    # Check second party (education - COFOG)
    party2 = result["parties"][1]
    assert party2["id"] == "ORG-0002"
    assert party2["details"]["classifications"][0]["scheme"] == "COFOG"
    assert party2["details"]["classifications"][0]["id"] == "09"
    assert party2["details"]["classifications"][0]["description"] == "Education"


def test_merge_activity_entity_duplicate_avoidance():
    """Test that merge_activity_entity avoids duplicating classifications."""
    # Setup existing release JSON with a party that already has a classification
    release_json = {
        "parties": [
            {
                "id": "ORG-0001",
                "roles": ["buyer"],
                "details": {
                    "classifications": [
                        {
                            "scheme": "eu-main-activity",
                            "id": "gas-oil",
                            "description": "Activities related to the exploitation of a geographical area for the purpose of extracting oil or gas."
                        }
                    ]
                }
            }
        ]
    }
    
    # Setup activity data with the same classification
    activity_data = {
        "parties": [
            {
                "id": "ORG-0001",
                "roles": ["buyer"],
                "details": {
                    "classifications": [
                        {
                            "scheme": "eu-main-activity",
                            "id": "gas-oil",
                            "description": "Activities related to the exploitation of a geographical area for the purpose of extracting oil or gas."
                        }
                    ]
                }
            }
        ]
    }
    
    # Merge the data
    merge_activity_entity(release_json, activity_data)
    
    # Check that no duplicate was added
    assert len(release_json["parties"]) == 1
    assert len(release_json["parties"][0]["details"]["classifications"]) == 1
    
    # Now try adding a different classification
    activity_data["parties"][0]["details"]["classifications"] = [
        {
            "scheme": "COFOG",
            "id": "09",
            "description": "Education"
        }
    ]
    
    merge_activity_entity(release_json, activity_data)
    
    # Check that the new classification was added
    assert len(release_json["parties"]) == 1
    assert len(release_json["parties"][0]["details"]["classifications"]) == 2


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
