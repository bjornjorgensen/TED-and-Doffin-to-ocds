# tests/test_bt_765_FrameworkAgreement.py
from pathlib import Path
import pytest
import json
import sys
import tempfile
import logging

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
    logging.info(
        "Running main with xml_file: %s and output_dir: %s", xml_file, output_dir
    )
    try:
        main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
        logging.info("main() executed successfully.")
    except Exception:
        logging.exception("Exception occurred while running main():")
        raise

    output_files = list(output_dir.glob("*.json"))
    logging.info("Output files found: %s", output_files)
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_765_framework_agreement_integration(
    tmp_path, setup_logging, temp_output_dir
):
    logger = setup_logging
    xml_content = """
    <ContractNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingProcess>
                <cac:ContractingSystem>
                    <cbc:ContractingSystemTypeCode listName="framework-agreement">fa-wo-rc</cbc:ContractingSystemTypeCode>
                </cac:ContractingSystem>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:TenderingProcess>
                <cac:ContractingSystem>
                    <cbc:ContractingSystemTypeCode listName="framework-agreement">fa-w-rc</cbc:ContractingSystemTypeCode>
                </cac:ContractingSystem>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0003</cbc:ID>
            <cac:TenderingProcess>
                <cac:ContractingSystem>
                    <cbc:ContractingSystemTypeCode listName="framework-agreement">fa-mix</cbc:ContractingSystemTypeCode>
                </cac:ContractingSystem>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0004</cbc:ID>
            <cac:TenderingProcess>
                <cac:ContractingSystem>
                    <cbc:ContractingSystemTypeCode listName="framework-agreement">none</cbc:ContractingSystemTypeCode>
                </cac:ContractingSystem>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </ContractNotice>
    """
    xml_file = tmp_path / "test_input_framework_agreement.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)
    logger.info("Result: %s", json.dumps(result, indent=2))

    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"
    assert (
        len(result["tender"]["lots"]) == 3
    ), f"Expected 3 lots with framework agreements, got {len(result['tender']['lots'])}"

    expected_methods = {
        "LOT-0001": "withoutReopeningCompetition",
        "LOT-0002": "withReopeningCompetition",
        "LOT-0003": "withAndWithoutReopeningCompetition",
    }

    for lot in result["tender"]["lots"]:
        assert lot["id"] in expected_methods, f"Unexpected lot {lot['id']} in result"
        assert "techniques" in lot, f"Expected 'techniques' in lot {lot['id']}"
        assert (
            "hasFrameworkAgreement" in lot["techniques"]
        ), f"Expected 'hasFrameworkAgreement' in lot {lot['id']} techniques"
        assert (
            lot["techniques"]["hasFrameworkAgreement"] is True
        ), f"Expected 'hasFrameworkAgreement' to be True for lot {lot['id']}"
        assert (
            "frameworkAgreement" in lot["techniques"]
        ), f"Expected 'frameworkAgreement' in lot {lot['id']} techniques"
        assert (
            "method" in lot["techniques"]["frameworkAgreement"]
        ), f"Expected 'method' in lot {lot['id']} frameworkAgreement"
        assert (
            lot["techniques"]["frameworkAgreement"]["method"]
            == expected_methods[lot["id"]]
        ), f"Expected method {expected_methods[lot['id']]} for lot {lot['id']}, got {lot['techniques']['frameworkAgreement']['method']}"

    assert "LOT-0004" not in [
        lot["id"] for lot in result["tender"]["lots"]
    ], "LOT-0004 should not be included in the result"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
