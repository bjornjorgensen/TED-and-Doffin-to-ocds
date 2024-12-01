# tests/test_bt_263_lot.py

import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import configure_logging, main
from ted_and_doffin_to_ocds.converters.bt_263_lot import (
    merge_additional_classification_code,
    parse_additional_classification_code,
)

logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def setup_logging():
    configure_logging()
    return logging.getLogger(__name__)


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


@pytest.fixture
def sample_xml():
    return """
    <ContractNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:AdditionalCommodityClassification>
                    <cbc:ItemClassificationCode>15311200</cbc:ItemClassificationCode>
                </cac:AdditionalCommodityClassification>
                <cac:AdditionalCommodityClassification>
                    <cbc:ItemClassificationCode>15311300</cbc:ItemClassificationCode>
                </cac:AdditionalCommodityClassification>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </ContractNotice>
    """


@pytest.fixture
def sample_xml_multiple_lots():
    return """
    <ContractNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:AdditionalCommodityClassification>
                    <cbc:ItemClassificationCode>15311200</cbc:ItemClassificationCode>
                </cac:AdditionalCommodityClassification>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:ProcurementProject>
                <cac:AdditionalCommodityClassification>
                    <cbc:ItemClassificationCode>15311300</cbc:ItemClassificationCode>
                </cac:AdditionalCommodityClassification>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </ContractNotice>
    """


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


def test_bt_263_lot_integration(tmp_path, setup_logging, temp_output_dir) -> None:
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

    classifications = item["additionalClassifications"]
    # Check for expected classifications
    cpv_classifications = [c for c in classifications if c.get("scheme") == "CPV"]
    id_classifications = [c for c in classifications if "id" in c]

    assert (
        len(cpv_classifications) == 2
    ), f"Expected 2 CPV classifications, got {len(cpv_classifications)}"
    assert (
        len(id_classifications) == 2
    ), f"Expected 2 ID classifications, got {len(id_classifications)}"

    # Verify specific IDs are present
    classification_ids = [c["id"] for c in id_classifications]
    assert "15311200" in classification_ids, "Expected classification id '15311200'"
    assert "15311300" in classification_ids, "Expected classification id '15311300'"


def test_parse_additional_classification_code_single_lot(sample_xml):
    result = parse_additional_classification_code(sample_xml)

    assert result is not None
    assert len(result["tender"]["items"]) == 1
    item = result["tender"]["items"][0]
    assert item["id"] == "1"
    assert item["relatedLot"] == "LOT-0001"
    assert len(item["additionalClassifications"]) == 2
    assert {"id": "15311200"} in item["additionalClassifications"]
    assert {"id": "15311300"} in item["additionalClassifications"]


def test_parse_additional_classification_code_multiple_lots(sample_xml_multiple_lots):
    result = parse_additional_classification_code(sample_xml_multiple_lots)

    assert result is not None
    assert len(result["tender"]["items"]) == 2
    assert result["tender"]["items"][0]["relatedLot"] == "LOT-0001"
    assert result["tender"]["items"][1]["relatedLot"] == "LOT-0002"


def test_parse_additional_classification_code_no_data():
    xml_no_classifications = """
    <ContractNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject/>
        </cac:ProcurementProjectLot>
    </ContractNotice>
    """
    result = parse_additional_classification_code(xml_no_classifications)
    assert result is None


def test_merge_additional_classification_code():
    release_json = {
        "tender": {
            "items": [
                {
                    "id": "1",
                    "relatedLot": "LOT-0001",
                    "additionalClassifications": [{"scheme": "CPV", "id": "existing"}],
                }
            ]
        }
    }

    additional_data = {
        "tender": {
            "items": [
                {
                    "id": "1",
                    "relatedLot": "LOT-0001",
                    "additionalClassifications": [{"id": "new"}],
                }
            ]
        }
    }

    merge_additional_classification_code(release_json, additional_data)

    assert len(release_json["tender"]["items"]) == 1
    item = release_json["tender"]["items"][0]
    assert len(item["additionalClassifications"]) == 2
    classification_ids = [c.get("id") for c in item["additionalClassifications"]]
    assert "existing" in classification_ids
    assert "new" in classification_ids


def test_merge_additional_classification_code_new_lot():
    release_json = {"tender": {"items": []}}

    additional_data = {
        "tender": {
            "items": [
                {
                    "id": "1",
                    "relatedLot": "LOT-0001",
                    "additionalClassifications": [{"id": "new"}],
                }
            ]
        }
    }

    merge_additional_classification_code(release_json, additional_data)

    assert len(release_json["tender"]["items"]) == 1
    assert release_json["tender"]["items"][0]["relatedLot"] == "LOT-0001"


def test_merge_additional_classification_code_none_data():
    release_json = {"tender": {"items": []}}
    merge_additional_classification_code(release_json, None)
    assert len(release_json["tender"]["items"]) == 0


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
