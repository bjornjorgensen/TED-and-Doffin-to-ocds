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
    output_files = list(output_dir.glob("*.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_766_part_dynamic_purchasing_system_integration(
    tmp_path, setup_logging, temp_output_dir
):
    configure_logging()
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="part">PART-0001</cbc:ID>
            <cac:TenderingProcess>
                <cac:ContractingSystem>
                    <cbc:ContractingSystemTypeCode listName="dps-usage">dps-nlist</cbc:ContractingSystemTypeCode>
                </cac:ContractingSystem>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </ContractNotice>
    """
    xml_file = tmp_path / "test_input_part_dynamic_purchasing_system.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    logger.info("Result: %s", json.dumps(result, indent=2))

    assert "tender" in result, "Expected 'tender' in result"
    assert "techniques" in result["tender"], "Expected 'techniques' in tender"
    assert (
        "hasDynamicPurchasingSystem" in result["tender"]["techniques"]
    ), "Expected 'hasDynamicPurchasingSystem' in techniques"
    assert (
        result["tender"]["techniques"]["hasDynamicPurchasingSystem"] is True
    ), "Expected 'hasDynamicPurchasingSystem' to be True"
    assert (
        "dynamicPurchasingSystem" in result["tender"]["techniques"]
    ), "Expected 'dynamicPurchasingSystem' in techniques"
    assert (
        "type" in result["tender"]["techniques"]["dynamicPurchasingSystem"]
    ), "Expected 'type' in dynamicPurchasingSystem"
    assert (
        result["tender"]["techniques"]["dynamicPurchasingSystem"]["type"] == "open"
    ), "Expected type to be 'open'"


def test_bt_766_part_dynamic_purchasing_system_none(
    tmp_path, setup_logging, temp_output_dir
):
    configure_logging()
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="part">PART-0001</cbc:ID>
            <cac:TenderingProcess>
                <cac:ContractingSystem>
                    <cbc:ContractingSystemTypeCode listName="dps-usage">none</cbc:ContractingSystemTypeCode>
                </cac:ContractingSystem>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </ContractNotice>
    """
    xml_file = tmp_path / "test_input_part_dynamic_purchasing_system_none.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    logger.info("Result: %s", json.dumps(result, indent=2))

    assert "tender" in result, "Expected 'tender' in result"
    assert (
        "techniques" not in result["tender"]
    ), "Did not expect 'techniques' in tender when DPS usage is 'none'"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
