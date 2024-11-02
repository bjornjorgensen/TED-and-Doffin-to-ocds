# tests/test_bt_765_PartFrameworkAgreement.py
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


def test_bt_765_part_framework_agreement_integration(
    tmp_path, setup_logging, temp_output_dir
):
    logger = setup_logging

    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="part">PART-0001</cbc:ID>
            <cac:TenderingProcess>
                <cac:ContractingSystem>
                    <cbc:ContractingSystemTypeCode listName="framework-agreement">fa-wo-rc</cbc:ContractingSystemTypeCode>
                </cac:ContractingSystem>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_part_framework_agreement.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    logger.info("Result: %s", json.dumps(result, indent=2))

    assert "tender" in result, "Expected 'tender' in result"
    assert "techniques" in result["tender"], "Expected 'techniques' in tender"
    assert (
        "hasFrameworkAgreement" in result["tender"]["techniques"]
    ), "Expected 'hasFrameworkAgreement' in techniques"
    assert (
        result["tender"]["techniques"]["hasFrameworkAgreement"] is True
    ), "Expected 'hasFrameworkAgreement' to be True"
    assert (
        "frameworkAgreement" in result["tender"]["techniques"]
    ), "Expected 'frameworkAgreement' in techniques"
    assert (
        "method" in result["tender"]["techniques"]["frameworkAgreement"]
    ), "Expected 'method' in frameworkAgreement"
    assert (
        result["tender"]["techniques"]["frameworkAgreement"]["method"]
        == "withoutReopeningCompetition"
    ), "Expected method to be 'withoutReopeningCompetition'"


def test_bt_765_part_framework_agreement_none(tmp_path, setup_logging, temp_output_dir):
    logger = setup_logging

    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="part">PART-0001</cbc:ID>
            <cac:TenderingProcess>
                <cac:ContractingSystem>
                    <cbc:ContractingSystemTypeCode listName="framework-agreement">none</cbc:ContractingSystemTypeCode>
                </cac:ContractingSystem>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_part_framework_agreement_none.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    logger.info("Result: %s", json.dumps(result, indent=2))

    assert "tender" in result, "Expected 'tender' in result"
    assert "techniques" in result["tender"], "Expected 'techniques' in tender"
    assert (
        "hasFrameworkAgreement" in result["tender"]["techniques"]
    ), "Expected 'hasFrameworkAgreement' in techniques"
    assert (
        result["tender"]["techniques"]["hasFrameworkAgreement"] is False
    ), "Expected 'hasFrameworkAgreement' to be False"
    assert (
        "frameworkAgreement" not in result["tender"]["techniques"]
    ), "Did not expect 'frameworkAgreement' in techniques when agreement is 'none'"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
