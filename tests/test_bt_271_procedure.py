# tests/test_bt_271_procedure.py
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


def test_bt_271_procedure_integration(tmp_path, setup_logging, temp_output_dir) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
        xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:ProcurementProject>
            <cac:RequestedTenderTotal>
                <ext:UBLExtensions>
                    <ext:UBLExtension>
                        <ext:ExtensionContent>
                            <efext:EformsExtension>
                                <efbc:FrameworkMaximumAmount currencyID="EUR">120000</efbc:FrameworkMaximumAmount>
                            </efext:EformsExtension>
                        </ext:ExtensionContent>
                    </ext:UBLExtension>
                </ext:UBLExtensions>
            </cac:RequestedTenderTotal>
        </cac:ProcurementProject>
    </ContractAwardNotice>
    """
    xml_file = tmp_path / "test_input_bt_271_procedure.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    assert "tender" in result, "tender not found in result"
    assert "techniques" in result["tender"], "techniques not found in tender"
    assert (
        "frameworkAgreement" in result["tender"]["techniques"]
    ), "frameworkAgreement not found in techniques"
    assert (
        "value" in result["tender"]["techniques"]["frameworkAgreement"]
    ), "value not found in frameworkAgreement"
    assert (
        result["tender"]["techniques"]["frameworkAgreement"]["value"]["amount"]
        == 120000
    ), f"Expected amount 120000, got {result['tender']['techniques']['frameworkAgreement']['value']['amount']}"
    assert (
        result["tender"]["techniques"]["frameworkAgreement"]["value"]["currency"]
        == "EUR"
    ), f"Expected currency 'EUR', got {result['tender']['techniques']['frameworkAgreement']['value']['currency']}"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
