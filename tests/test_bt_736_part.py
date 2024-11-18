# tests/test_bt_736_part.py
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


def test_bt_736_part_reserved_execution_yes(tmp_path, setup_logging, temp_output_dir):
    """Test when reserved execution is set to 'yes' for a part:
    - Should set tender.contractTerms.reservedExecution to true
    """
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
    xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cac:ProcurementProjectLot>
        <cbc:ID schemeName="part">PART-0001</cbc:ID>
        <cac:TenderingTerms>
            <cac:ContractExecutionRequirement>
                <cbc:ExecutionRequirementCode listName="reserved-execution">yes</cbc:ExecutionRequirementCode>
            </cac:ContractExecutionRequirement>
        </cac:TenderingTerms>
    </cac:ProcurementProjectLot>
</ContractNotice>
"""
    xml_file = tmp_path / "test_input_reserved_execution_part.xml"
    xml_file.write_text(xml_content)
    logger.info("Created XML file at %s", xml_file)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Verify reserved execution is set correctly
    assert "tender" in result
    assert "contractTerms" in result["tender"]
    assert "reservedExecution" in result["tender"]["contractTerms"]
    assert result["tender"]["contractTerms"]["reservedExecution"] is True


def test_bt_736_part_reserved_execution_no(tmp_path, setup_logging, temp_output_dir):
    """Test when reserved execution is set to 'no' for a part:
    - Should not include reservedExecution in contractTerms
    """
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
    xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cac:ProcurementProjectLot>
        <cbc:ID schemeName="part">PART-0001</cbc:ID>
        <cac:TenderingTerms>
            <cac:ContractExecutionRequirement>
                <cbc:ExecutionRequirementCode listName="reserved-execution">no</cbc:ExecutionRequirementCode>
            </cac:ContractExecutionRequirement>
        </cac:TenderingTerms>
    </cac:ProcurementProjectLot>
</ContractNotice>
"""
    xml_file = tmp_path / "test_input_reserved_execution_part_no.xml"
    xml_file.write_text(xml_content)
    logger.info("Created XML file at %s", xml_file)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Verify reserved execution is not present
    assert "tender" in result
    assert "contractTerms" not in result["tender"] or "reservedExecution" not in result[
        "tender"
    ].get("contractTerms", {})


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
