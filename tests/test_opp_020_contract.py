# tests/test_OPP_020_Contract.py
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
    output_files = list(output_dir.glob("*_release_0.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_opp_020_contract_integration(tmp_path, setup_logging, temp_output_dir):
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
        <efac:noticeResult>
            <efac:LotResult>
                <efac:TenderLot>
                    <cbc:ID schemeName="lot">LOT-0001</cbc:ID>
                </efac:TenderLot>
                <efac:SettledContract>
                    <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                </efac:SettledContract>
            </efac:LotResult>
            <efac:SettledContract>
                <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                <efac:DurationJustification>
                    <efbc:ExtendedDurationIndicator>true</efbc:ExtendedDurationIndicator>
                </efac:DurationJustification>
            </efac:SettledContract>
        </efac:noticeResult>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_extended_duration_indicator.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    logger.info("Test result: %s", json.dumps(result, indent=2))

    # Verify the results
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001"
    assert "hasEssentialAssets" in lot
    assert lot["hasEssentialAssets"] is True


def test_opp_020_contract_integration_false(tmp_path, setup_logging, temp_output_dir):
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
        <efac:noticeResult>
            <efac:LotResult>
                <efac:TenderLot>
                    <cbc:ID schemeName="lot">LOT-0002</cbc:ID>
                </efac:TenderLot>
                <efac:SettledContract>
                    <cbc:ID schemeName="contract">CON-0002</cbc:ID>
                </efac:SettledContract>
            </efac:LotResult>
            <efac:SettledContract>
                <cbc:ID schemeName="contract">CON-0002</cbc:ID>
                <efac:DurationJustification>
                    <efbc:ExtendedDurationIndicator>false</efbc:ExtendedDurationIndicator>
                </efac:DurationJustification>
            </efac:SettledContract>
        </efac:noticeResult>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_extended_duration_indicator_false.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    logger.info("Test result: %s", json.dumps(result, indent=2))

    # Verify the results
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0002"
    assert "hasEssentialAssets" in lot
    assert lot["hasEssentialAssets"] is False


if __name__ == "__main__":
    pytest.main(["-v"])
