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


def test_bt_6110_contract_integration(tmp_path, setup_logging, temp_output_dir) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
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
                        <efac:NoticeResult>
                            <efac:SettledContract>
                                <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                                <efac:Funding>
                                    <cbc:Description>Program for the development ...</cbc:Description>
                                </efac:Funding>
                            </efac:SettledContract>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                                <efac:SettledContract>
                                    <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                                </efac:SettledContract>
                            </efac:LotResult>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </ContractAwardNotice>
    """

    xml_file = tmp_path / "test_input_contract_eu_funds_details.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)
    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    assert "contracts" in result, "Expected 'contracts' in result"
    assert (
        len(result["contracts"]) == 1
    ), f"Expected 1 contract, got {len(result['contracts'])}"

    contract = result["contracts"][0]
    assert (
        contract["id"] == "CON-0001"
    ), f"Expected contract id 'CON-0001', got {contract['id']}"
    assert "finance" in contract, "Expected 'finance' in contract"
    assert (
        len(contract["finance"]) == 1
    ), f"Expected 1 finance entry, got {len(contract['finance'])}"
    assert (
        contract["finance"][0]["description"] == "Program for the development ..."
    ), f"Expected description 'Program for the development ...', got {contract['finance'][0]['description']}"
    assert (
        contract["awardID"] == "RES-0001"
    ), f"Expected awardID 'RES-0001', got {contract.get('awardID')}"

    # logger.info("Test bt_6110_contract_integration passed successfully.") # Logging disabled


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
