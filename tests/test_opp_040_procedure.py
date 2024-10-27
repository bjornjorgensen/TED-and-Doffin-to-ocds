# tests/test_OPP_040_procedure.py
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


def test_opp_040_procedure_integration(tmp_path, setup_logging, temp_output_dir):
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:ProcurementProject>
            <cac:ProcurementAdditionalType>
                <cbc:ProcurementTypeCode listName="transport-service">bus-s</cbc:ProcurementTypeCode>
            </cac:ProcurementAdditionalType>
        </cac:ProcurementProject>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_main_nature_sub_type.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    logger.info("Test result: %s", json.dumps(result, indent=2))

    # Verify the results
    assert "tender" in result
    assert "additionalProcurementCategories" in result["tender"]
    assert "bus-s" in result["tender"]["additionalProcurementCategories"]


def test_opp_040_procedure_integration_multiple(
    tmp_path, setup_logging, temp_output_dir
):
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:ProcurementProject>
            <cac:ProcurementAdditionalType>
                <cbc:ProcurementTypeCode listName="transport-service">bus-s</cbc:ProcurementTypeCode>
            </cac:ProcurementAdditionalType>
            <cac:ProcurementAdditionalType>
                <cbc:ProcurementTypeCode listName="transport-service">tram-s</cbc:ProcurementTypeCode>
            </cac:ProcurementAdditionalType>
        </cac:ProcurementProject>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_main_nature_sub_type_multiple.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    logger.info("Test result: %s", json.dumps(result, indent=2))

    # Verify the results
    assert "tender" in result
    assert "additionalProcurementCategories" in result["tender"]
    assert "bus-s" in result["tender"]["additionalProcurementCategories"]
    assert "tram-s" in result["tender"]["additionalProcurementCategories"]


if __name__ == "__main__":
    pytest.main(["-v"])
