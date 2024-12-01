# tests/test_bt_263_lot.py

import json
import logging
import sys
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
    configure_logging(logging.DEBUG)
    return logger


@pytest.fixture
def temp_output_dir(tmp_path):
    return tmp_path / "output"


@pytest.fixture
def sample_xml():
    return """
    <ContractNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:AdditionalCommodityClassification>
                    <cbc:ItemClassificationCode listName="CPV">15311200</cbc:ItemClassificationCode>
                </cac:AdditionalCommodityClassification>
                <cac:AdditionalCommodityClassification>
                    <cbc:ItemClassificationCode listName="CPV">15311300</cbc:ItemClassificationCode>
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
                    <cbc:ItemClassificationCode listName="CPV">15311200</cbc:ItemClassificationCode>
                </cac:AdditionalCommodityClassification>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:ProcurementProject>
                <cac:AdditionalCommodityClassification>
                    <cbc:ItemClassificationCode listName="CPV">15311300</cbc:ItemClassificationCode>
                </cac:AdditionalCommodityClassification>
                <cac:AdditionalCommodityClassification>
                    <cbc:ItemClassificationCode listName="CPV">15311400</cbc:ItemClassificationCode>
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
        main([str(xml_file), str(output_dir)])
    except Exception as e:
        logging.exception("Error running main: %s")
        pytest.fail(f"main() raised an exception: {e}")

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
                    <cbc:ItemClassificationCode listName="CPV">15311200</cbc:ItemClassificationCode>
                </cac:AdditionalCommodityClassification>
                <cac:AdditionalCommodityClassification>
                    <cbc:ItemClassificationCode listName="CPV">15311300</cbc:ItemClassificationCode>
                </cac:AdditionalCommodityClassification>
                <cac:AdditionalCommodityClassification>
                    <cbc:ItemClassificationCode listName="CPV">15311200</cbc:ItemClassificationCode>
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

    # Ensure 'id' is present to prevent AttributeError
    assert "id" in item, "Missing 'id' in item"

    assert (
        "additionalClassifications" in item
    ), "Expected 'additionalClassifications' in item"
    classifications = item["additionalClassifications"]
    assert (
        len(classifications) == 2
    ), f"Expected 2 unique classifications, got {len(classifications)}"

    schemes = set()
    ids = set()
    for classification in classifications:
        assert (
            "scheme" in classification
        ), "Missing 'scheme' in additionalClassification"
        assert "id" in classification, "Missing 'id' in additionalClassification"
        schemes.add(classification["scheme"])
        ids.add(classification["id"])

    assert schemes == {"CPV"}, f"Unexpected schemes: {schemes}"
    assert ids == {"15311200", "15311300"}, f"Unexpected ids: {ids}"


def test_parse_additional_classification_code_single_lot(sample_xml):
    result = parse_additional_classification_code(sample_xml)
    assert (
        result is not None
    ), "Expected result from parse_additional_classification_code"
    assert "tender" in result
    assert "items" in result["tender"]
    assert len(result["tender"]["items"]) == 1
    item = result["tender"]["items"][0]
    assert "additionalClassifications" in item
    classifications = item["additionalClassifications"]
    assert len(classifications) == 2
    for classification in classifications:
        assert "scheme" in classification
        assert "id" in classification


def test_parse_additional_classification_code_multiple_lots(sample_xml_multiple_lots):
    result = parse_additional_classification_code(sample_xml_multiple_lots)
    assert (
        result is not None
    ), "Expected result from parse_additional_classification_code with multiple lots"
    assert "tender" in result
    assert "items" in result["tender"]
    assert len(result["tender"]["items"]) == 2
    for item in result["tender"]["items"]:
        assert "additionalClassifications" in item
        for classification in item["additionalClassifications"]:
            assert "scheme" in classification
            assert "id" in classification


def test_parse_additional_classification_code_no_data():
    xml_content = """
    <ContractNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <!-- No AdditionalCommodityClassification -->
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </ContractNotice>
    """
    result = parse_additional_classification_code(xml_content)
    assert (
        result is None
    ), "Expected None when there is no additional classification code"


def test_merge_additional_classification_code():
    release_json = {
        "tender": {
            "items": [
                {
                    "id": "1",
                    "additionalClassifications": [{"scheme": "CPV", "id": "15311200"}],
                    "relatedLot": "LOT-0001",
                }
            ]
        }
    }
    additional_classification_data = {
        "tender": {
            "items": [
                {
                    "id": "1",
                    "additionalClassifications": [
                        {"scheme": "CPV", "id": "15311300"},
                        {"scheme": "CPV", "id": "15311200"},  # Duplicate
                    ],
                    "relatedLot": "LOT-0001",
                }
            ]
        }
    }
    merge_additional_classification_code(release_json, additional_classification_data)
    classifications = release_json["tender"]["items"][0]["additionalClassifications"]
    assert (
        len(classifications) == 2
    ), f"Expected 2 unique classifications, got {len(classifications)}"
    ids = {c["id"] for c in classifications}
    assert ids == {"15311200", "15311300"}, f"Unexpected ids after merge: {ids}"


def test_merge_additional_classification_code_new_lot():
    release_json = {
        "tender": {
            "items": [
                {
                    "id": "1",
                    "additionalClassifications": [{"scheme": "CPV", "id": "15311200"}],
                    "relatedLot": "LOT-0001",
                }
            ]
        }
    }
    additional_classification_data = {
        "tender": {
            "items": [
                {
                    "id": "2",
                    "additionalClassifications": [{"scheme": "CPV", "id": "15311400"}],
                    "relatedLot": "LOT-0002",
                }
            ]
        }
    }
    merge_additional_classification_code(release_json, additional_classification_data)
    assert (
        len(release_json["tender"]["items"]) == 2
    ), "Expected 2 items after merging new lot"
    new_item = next(
        item for item in release_json["tender"]["items"] if item["id"] == "2"
    )
    assert new_item["additionalClassifications"] == [
        {"scheme": "CPV", "id": "15311400"}
    ]


def test_merge_additional_classification_code_none_data():
    release_json = {
        "tender": {
            "items": [
                {
                    "id": "1",
                    "additionalClassifications": [{"scheme": "CPV", "id": "15311200"}],
                    "relatedLot": "LOT-0001",
                }
            ]
        }
    }
    merge_additional_classification_code(release_json, None)
    assert (
        len(release_json["tender"]["items"]) == 1
    ), "No items should be added when data is None"


if __name__ == "__main__":
    pytest.main()
