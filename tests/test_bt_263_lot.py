# tests/test_bt_263_lot.py

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


def test_bt_263_lot_integration(tmp_path, setup_logging, temp_output_dir):
    logger = setup_logging
    xml_content = """
    <ContractNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:AdditionalCommodityClassification>
                    <cbc:ItemClassificationCode listName="cpv">15311200</cbc:ItemClassificationCode>
                </cac:AdditionalCommodityClassification>
                <cac:AdditionalCommodityClassification>
                    <cbc:ItemClassificationCode listName="cpv">15311300</cbc:ItemClassificationCode>
                </cac:AdditionalCommodityClassification>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </ContractNotice>
    """
    xml_file = tmp_path / "test_input_additional_classification_code.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    logger.info("Result: %s", json.dumps(result, indent=2))

    assert "tender" in result, "Expected 'tender' in result"
    assert "items" in result["tender"], "Expected 'items' in tender"
    assert (
        len(result["tender"]["items"]) == 1
    ), f"Expected 1 item, got {len(result['tender']['items'])}"

    item = result["tender"]["items"][0]
    assert item["id"] == "1", f"Expected item id '1', got {item['id']}"
    assert (
        item["relatedLot"] == "LOT-0001"
    ), f"Expected relatedLot 'LOT-0001', got {item['relatedLot']}"
    assert (
        "additionalClassifications" in item
    ), "Expected 'additionalClassifications' in item"
    assert (
        len(item["additionalClassifications"]) == 2
    ), f"Expected 2 additional classifications, got {len(item['additionalClassifications'])}"

    classification_ids = [c["id"] for c in item["additionalClassifications"]]
    assert "15311200" in classification_ids, "Expected classification id '15311200'"
    assert "15311300" in classification_ids, "Expected classification id '15311300'"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
