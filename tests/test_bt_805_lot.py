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
    output_files = list(output_dir.glob("*.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_805_lot_integration(tmp_path, setup_logging, temp_output_dir) -> None:
    logger = setup_logging

    xml_content = """
    <ContractAwardNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
                         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:ProcurementAdditionalType>
                    <cbc:ProcurementTypeCode listName="gpp-criteria">eu</cbc:ProcurementTypeCode>
                </cac:ProcurementAdditionalType>
                <cac:ProcurementAdditionalType>
                    <cbc:ProcurementTypeCode listName="gpp-criteria">national</cbc:ProcurementTypeCode>
                </cac:ProcurementAdditionalType>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:ProcurementProject>
                <cac:ProcurementAdditionalType>
                    <cbc:ProcurementTypeCode listName="gpp-criteria">none</cbc:ProcurementTypeCode>
                </cac:ProcurementAdditionalType>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_green_procurement_criteria.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)
    logger.info("Result: %s", json.dumps(result, indent=2))

    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"
    assert (
        len(result["tender"]["lots"]) == 1
    ), f"Expected 1 lot, got {len(result['tender']['lots'])}"

    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001", f"Expected lot id 'LOT-0001', got {lot['id']}"
    assert lot["hasSustainability"] is True, "Expected hasSustainability to be True"
    assert "sustainability" in lot, "Expected 'sustainability' in lot"
    assert (
        len(lot["sustainability"]) == 2
    ), f"Expected 2 sustainability entries, got {len(lot['sustainability'])}"

    strategies = [
        item
        for sustainability in lot["sustainability"]
        for item in sustainability["strategies"]
    ]
    assert "euGPPCriteria" in strategies, "Expected 'euGPPCriteria' in strategies"
    assert (
        "nationalGPPCriteria" in strategies
    ), "Expected 'nationalGPPCriteria' in strategies"

    # Check that LOT-0002 is not included
    assert all(
        lot["id"] != "LOT-0002" for lot in result["tender"]["lots"]
    ), "LOT-0002 should not be included"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
