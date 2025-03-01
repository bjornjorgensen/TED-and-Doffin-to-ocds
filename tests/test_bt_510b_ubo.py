# tests/test_bt_510b_ubo.py
import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import configure_logging, main


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
    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    output_files = list(output_dir.glob("*_release_0.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_510b_ubo_integration(tmp_path, setup_logging, temp_output_dir) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
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
                            </efac:Organization>
                            <efac:UltimateBeneficialOwner>
                                <cbc:ID schemeName="ubo">ubo-0001</cbc:ID>
                                <cac:ResidenceAddress>
                                    <cbc:StreetName>2 CheeseStreet</cbc:StreetName>
                                    <cbc:AdditionalStreetName>Nelson Building</cbc:AdditionalStreetName>
                                    <cac:AddressLine>
                                        <cbc:Line>2nd floor</cbc:Line>
                                    </cac:AddressLine>
                                </cac:ResidenceAddress>
                            </efac:UltimateBeneficialOwner>
                        </efac:Organizations>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </ContractAwardNotice>
    """
    xml_file = tmp_path / "test_input_ubo_streetline1.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

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
    assert ubo["id"] == "ubo-0001", f"Expected ubo id 'ubo-0001', got {ubo['id']}"
    assert "address" in ubo, "Expected 'address' in ubo"
    assert "streetAddress" in ubo["address"], "Expected 'streetAddress' in ubo address"
    expected_street_address = "2 CheeseStreet, Nelson Building, 2nd floor"
    assert (
        ubo["address"]["streetAddress"] == expected_street_address
    ), f"Expected street address '{expected_street_address}', got {ubo['address']['streetAddress']}"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
