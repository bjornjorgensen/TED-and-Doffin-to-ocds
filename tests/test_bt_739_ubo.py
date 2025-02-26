import json
import logging
import sys
import tempfile
from pathlib import Path
from typing import Any

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.converters.eforms.bt_739_ubo import (
    merge_ubo_contact_fax,
    parse_ubo_contact_fax,
)
from src.ted_and_doffin_to_ocds.main import configure_logging, main

# Test constants
TEST_UBO_XML = """<?xml version="1.0" encoding="UTF-8"?>
<ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
      xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
      xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
      xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
      xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
      xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
    <ext:UBLExtensions>
        <ext:UBLExtension>
            <ext:ExtensionContent>
                <efext:EformsExtension>
                    <efac:Organizations>
                        <efac:Organization>
                            <efac:Company>
                                <cac:PartyIdentification>
                                    <cbc:ID schemeName="organization">ORG-0001</cbc:ID>
                                </cac:PartyIdentification>
                            </efac:Company>
                            <efac:UltimateBeneficialOwner>
                                <cbc:ID schemeName="ubo">UBO-0001</cbc:ID>
                                <cac:Contact>
                                    <cbc:Telefax>+123 4567891</cbc:Telefax>
                                </cac:Contact>
                            </efac:UltimateBeneficialOwner>
                        </efac:Organization>
                    </efac:Organizations>
                </efext:EformsExtension>
            </ext:ExtensionContent>
        </ext:UBLExtension>
    </ext:UBLExtensions>
</ContractAwardNotice>
"""


# Fixtures
@pytest.fixture(scope="module")
def setup_logging():
    configure_logging()
    return logging.getLogger(__name__)


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


@pytest.fixture
def sample_xml_file(tmp_path) -> Path:
    xml_file = tmp_path / "test_input_ubo_fax.xml"
    xml_file.write_text(TEST_UBO_XML)
    return xml_file


@pytest.fixture
def sample_release_json() -> dict[str, Any]:
    return {"parties": [{"id": "ORG-0001", "beneficialOwners": [{"id": "UBO-0001"}]}]}


# Helper functions
def run_main_and_get_result(xml_file: Path, output_dir: Path) -> dict[str, Any]:
    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    output_files = list(output_dir.glob("*_release_0.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def validate_ubo_data(result: dict[str, Any], expected_fax: str) -> None:
    """Validate UBO data in the result"""
    assert "parties" in result, "Expected 'parties' in result"
    assert (
        len(result["parties"]) == 1
    ), f"Expected 1 party, got {len(result['parties'])}"

    party = result["parties"][0]
    assert party["id"] == "ORG-0001", f"Expected party id 'ORG-0001', got {party['id']}"
    assert "beneficialOwners" in party, "Expected 'beneficialOwners' in party"
    assert (
        len(party["beneficialOwners"]) == 1
    ), f"Expected 1 beneficial owner, got {len(party['beneficialOwners'])}"

    ubo = party["beneficialOwners"][0]
    assert ubo["id"] == "UBO-0001", f"Expected ubo id 'UBO-0001', got {ubo['id']}"
    assert "faxNumber" in ubo, "Expected 'faxNumber' in ubo"
    assert (
        ubo["faxNumber"] == expected_fax
    ), f"Expected faxNumber '{expected_fax}', got {ubo['faxNumber']}"


# Tests
def test_bt_739_ubo_integration(
    sample_xml_file: Path, setup_logging, temp_output_dir: Path
) -> None:
    """Test complete integration of UBO fax processing"""
    logger = setup_logging

    result = run_main_and_get_result(sample_xml_file, temp_output_dir)
    logger.info("Result: %s", json.dumps(result, indent=2))

    validate_ubo_data(result, "+123 4567891")
    logger.info("Test bt_739_ubo_integration passed successfully.")


def test_parse_ubo_fax() -> None:
    """Test parsing UBO fax data directly"""
    result = parse_ubo_fax(TEST_UBO_XML)

    assert result is not None, "Expected parse result not to be None"
    assert "parties" in result, "Expected 'parties' in parse result"
    assert len(result["parties"]) == 1, "Expected 1 party in parse result"

    party = result["parties"][0]
    assert "beneficialOwners" in party, "Expected beneficialOwners in party"
    assert len(party["beneficialOwners"]) == 1, "Expected 1 beneficial owner"

    ubo = party["beneficialOwners"][0]
    assert ubo["faxNumber"] == "+123 4567891", "Wrong fax number parsed"


def test_merge_ubo_fax(sample_release_json) -> None:
    """Test merging UBO fax data into existing release"""
    ubo_data = {
        "parties": [
            {
                "id": "ORG-0001",
                "beneficialOwners": [{"id": "UBO-0001", "faxNumber": "+123 4567891"}],
            }
        ]
    }

    merge_ubo_fax(sample_release_json, ubo_data)
    validate_ubo_data(sample_release_json, "+123 4567891")


def test_parse_invalid_xml() -> None:
    """Test parsing invalid XML content"""
    result = parse_ubo_fax("Invalid XML content")
    assert result is None, "Expected None result for invalid XML"


def test_merge_empty_data(sample_release_json) -> None:
    """Test merging empty UBO data"""
    original_json = json.dumps(sample_release_json)
    merge_ubo_fax(sample_release_json, None)
    assert (
        json.dumps(sample_release_json) == original_json
    ), "Release should not change when merging None"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
