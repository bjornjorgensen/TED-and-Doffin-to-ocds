# tests/test_bt_109_lot.py

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
    # Clear the output directory before each run
    for file in output_dir.glob("*.json"):
        file.unlink()
    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    output_files = list(output_dir.glob("*.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_109_framework_duration_missing_justification(
    tmp_path, setup_logging, temp_output_dir
):
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-001</cbc:ID>
            <cac:TenderingProcess>
                <cac:FrameworkAgreement>
                    <!-- Justification is missing -->
                </cac:FrameworkAgreement>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """

    xml_file = tmp_path / "test_input_framework_missing_justification.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    logger.info("Result: %s", json.dumps(result, indent=2))

    # Check that there is no framework agreement data
    assert "tender" in result
    assert "lots" in result["tender"]
    lots = result["tender"]["lots"]
    assert len(lots) == 1
    lot = lots[0]
    assert lot["id"] == "LOT-001"
    assert (
        "techniques" not in lot
        or "frameworkAgreement" not in lot.get("techniques", {})
        or "periodRationale"
        not in lot.get("techniques", {}).get("frameworkAgreement", {})
    ), "Framework agreement data should not be present when justification is missing"


def test_bt_109_framework_duration_empty_justification(
    tmp_path, setup_logging, temp_output_dir
):
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-001</cbc:ID>
            <cac:TenderingProcess>
                <cac:FrameworkAgreement>
                    <cbc:Justification></cbc:Justification>
                </cac:FrameworkAgreement>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """

    xml_file = tmp_path / "test_input_framework_empty_justification.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    logger.info("Result: %s", json.dumps(result, indent=2))

    # Check that there is no framework agreement data for empty justification
    assert "tender" in result
    assert "lots" in result["tender"]
    lots = result["tender"]["lots"]
    assert len(lots) == 1
    lot = lots[0]
    assert lot["id"] == "LOT-001"
    assert (
        "techniques" not in lot
        or "frameworkAgreement" not in lot.get("techniques", {})
        or "periodRationale"
        not in lot.get("techniques", {}).get("frameworkAgreement", {})
    ), "Framework agreement data should not be present when justification is empty"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
