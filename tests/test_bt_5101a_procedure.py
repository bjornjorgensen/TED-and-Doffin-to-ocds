# tests/test_bt_5101a_procedure.py
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


def test_bt_5101a_procedure_integration(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:ProcurementProject>
            <cac:RealizedLocation>
                <cac:Address>
                    <cbc:StreetName>Main Street</cbc:StreetName>
                    <cbc:AdditionalStreetName>Building B1</cbc:AdditionalStreetName>
                    <cac:AddressLine>
                        <cbc:Line>3rd floor</cbc:Line>
                    </cac:AddressLine>
                </cac:Address>
            </cac:RealizedLocation>
        </cac:ProcurementProject>
    </ContractAwardNotice>
    """
    xml_file = tmp_path / "test_input_procedure_place_performance_street.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    logger.info("Test result: %s", json.dumps(result, indent=2))

    # Verify the results
    assert "tender" in result
    assert "deliveryAddresses" in result["tender"]
    assert len(result["tender"]["deliveryAddresses"]) == 1
    address = result["tender"]["deliveryAddresses"][0]
    assert "streetAddress" in address
    assert address["streetAddress"] == "Main Street, Building B1, 3rd floor"


if __name__ == "__main__":
    pytest.main(["-v"])
