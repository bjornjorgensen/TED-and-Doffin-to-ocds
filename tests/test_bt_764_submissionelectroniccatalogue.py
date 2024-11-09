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


def test_bt_764_submission_electronic_catalogue_integration(
    tmp_path, setup_logging, temp_output_dir
):
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
    xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cac:ProcurementProjectLot>
        <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
        <cac:TenderingTerms>
            <cac:ContractExecutionRequirement>
                <cbc:ExecutionRequirementCode listName="ecatalog-submission">allowed</cbc:ExecutionRequirementCode>
            </cac:ContractExecutionRequirement>
        </cac:TenderingTerms>
    </cac:ProcurementProjectLot>
    <cac:ProcurementProjectLot>
        <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
        <cac:TenderingTerms>
            <cac:ContractExecutionRequirement>
                <cbc:ExecutionRequirementCode listName="ecatalog-submission">required</cbc:ExecutionRequirementCode>
            </cac:ContractExecutionRequirement>
        </cac:TenderingTerms>
    </cac:ProcurementProjectLot>
    <cac:ProcurementProjectLot>
        <cbc:ID schemeName="Lot">LOT-0003</cbc:ID>
        <cac:TenderingTerms>
            <cac:ContractExecutionRequirement>
                <cbc:ExecutionRequirementCode listName="ecatalog-submission">not-allowed</cbc:ExecutionRequirementCode>
            </cac:ContractExecutionRequirement>
        </cac:TenderingTerms>
    </cac:ProcurementProjectLot>
</ContractNotice>
"""
    xml_file = tmp_path / "test_input_submission_electronic_catalogue.xml"
    xml_file.write_text(xml_content)
    logger.info("Created XML file at %s", xml_file)
    logger.info("Output directory: %s", temp_output_dir)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)
    logger.info("Result: %s", json.dumps(result, indent=2))

    # Verify results
    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"
    assert (
        len(result["tender"]["lots"]) == 3
    ), f"Expected 3 lots, got {len(result['tender']['lots'])}"

    lot_policies = {
        lot["id"]: lot["submissionTerms"]["electronicCatalogPolicy"]
        for lot in result["tender"]["lots"]
    }
    expected_policies = {
        "LOT-0001": "allowed",
        "LOT-0002": "required",
        "LOT-0003": "notAllowed",
    }
    assert (
        lot_policies == expected_policies
    ), f"Expected policies {expected_policies}, got {lot_policies}"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
