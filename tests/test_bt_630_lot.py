# tests/test_bt_630_lot.py
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
    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    output_files = list(output_dir.glob("*_release_0.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_630_lot_deadline_receipt_expressions_integration(
    tmp_path, setup_logging, temp_output_dir
):
    xml_content = """
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
          xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingProcess>
                <ext:UBLExtensions>
                    <ext:UBLExtension>
                        <ext:ExtensionContent>
                            <efext:EformsExtension>
                                <efac:InterestExpressionReceptionPeriod>
                                    <cbc:EndDate>2019-10-28+01:00</cbc:EndDate>
                                    <cbc:EndTime>18:00:00+01:00</cbc:EndTime>
                                </efac:InterestExpressionReceptionPeriod>
                            </efext:EformsExtension>
                        </ext:ExtensionContent>
                    </ext:UBLExtension>
                </ext:UBLExtensions>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """
    xml_file = tmp_path / "test_input_deadline_receipt_expressions.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    logger = setup_logging
    logger.info("Result: %s", json.dumps(result, indent=2))

    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"
    assert (
        len(result["tender"]["lots"]) == 1
    ), f"Expected 1 lot, got {len(result['tender']['lots'])}"
    assert (
        result["tender"]["lots"][0]["id"] == "LOT-0001"
    ), f"Expected lot id 'LOT-0001', got {result['tender']['lots'][0]['id']}"
    assert (
        "tenderPeriod" in result["tender"]["lots"][0]
    ), "Expected 'tenderPeriod' in lot"
    assert (
        result["tender"]["lots"][0]["tenderPeriod"]["endDate"]
        == "2019-10-28T18:00:00+01:00"
    ), f"Expected endDate '2019-10-28T18:00:00+01:00', got {result['tender']['lots'][0]['tenderPeriod']['endDate']}"

    logger.info(
        "Test bt_630_lot_deadline_receipt_expressions_integration passed successfully."
    )


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
