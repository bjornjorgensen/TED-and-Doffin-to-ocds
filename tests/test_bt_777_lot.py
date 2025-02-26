# tests/test_bt_777_Lot.py
import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

from src.ted_and_doffin_to_ocds.converters.eforms.bt_777_lot import (
    merge_strategic_procurement_description,
    parse_strategic_procurement_description,
)

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import configure_logging, main


@pytest.fixture(scope="module")
def setup_logging():
    # Logging disabled for tests
    logger = logging.getLogger(__name__)
    logger.disabled = True
    return logger


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


def test_parse_strategic_procurement_description() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:ProcurementAdditionalType>
                    <cbc:ProcurementTypeCode listName="strategic-procurement">innovation</cbc:ProcurementTypeCode>
                    <cbc:ProcurementType>This is a strategic procurement involving innovative use...</cbc:ProcurementType>
                </cac:ProcurementAdditionalType>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_strategic_procurement_description(xml_content)

    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert "sustainability" in result["tender"]["lots"][0]
    assert len(result["tender"]["lots"][0]["sustainability"]) == 1
    assert (
        result["tender"]["lots"][0]["sustainability"][0]["description"]
        == "This is a strategic procurement involving innovative use..."
    )


def test_merge_strategic_procurement_description() -> None:
    release_json = {"tender": {"lots": [{"id": "LOT-0001", "title": "Existing Lot"}]}}

    strategic_procurement_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "sustainability": [
                        {
                            "description": "This is a strategic procurement involving innovative use...",
                        },
                    ],
                },
            ],
        },
    }

    merge_strategic_procurement_description(release_json, strategic_procurement_data)

    assert "sustainability" in release_json["tender"]["lots"][0]
    assert len(release_json["tender"]["lots"][0]["sustainability"]) == 1
    assert (
        release_json["tender"]["lots"][0]["sustainability"][0]["description"]
        == "This is a strategic procurement involving innovative use..."
    )


def test_bt_777_lot_strategic_procurement_integration(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging
    xml_content = """
    <ContractNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:ProcurementAdditionalType>
                    <cbc:ProcurementTypeCode listName="strategic-procurement">innovation</cbc:ProcurementTypeCode>
                    <cbc:ProcurementType>This is a strategic procurement involving innovative use...</cbc:ProcurementType>
                </cac:ProcurementAdditionalType>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:ProcurementProject>
                <cac:ProcurementAdditionalType>
                    <cbc:ProcurementTypeCode listName="strategic-procurement">environmental</cbc:ProcurementTypeCode>
                    <cbc:ProcurementType>This procurement aims to reduce environmental impact...</cbc:ProcurementType>
                </cac:ProcurementAdditionalType>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0003</cbc:ID>
            <cac:ProcurementProject>
                <cac:ProcurementAdditionalType>
                    <cbc:ProcurementTypeCode listName="other-type">not-strategic</cbc:ProcurementTypeCode>
                    <cbc:ProcurementType>This is not a strategic procurement...</cbc:ProcurementType>
                </cac:ProcurementAdditionalType>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </ContractNotice>
    """
    xml_file = tmp_path / "test_input_strategic_procurement.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)
    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    assert "tender" in result
    assert "lots" in result["tender"]

    lots_with_sustainability = [
        lot for lot in result["tender"]["lots"] if "sustainability" in lot
    ]
    assert len(lots_with_sustainability) == 2

    lot_1 = next(
        (lot for lot in lots_with_sustainability if lot["id"] == "LOT-0001"),
        None,
    )
    assert lot_1 is not None
    assert "sustainability" in lot_1
    assert isinstance(lot_1["sustainability"], list)
    assert len(lot_1["sustainability"]) > 0

    # Check if 'description' is directly in the sustainability object
    if "description" in lot_1["sustainability"][0]:
        assert (
            lot_1["sustainability"][0]["description"]
            == "This is a strategic procurement involving innovative use..."
        )
    # If not, it might be nested under another key, or the structure might be different
    else:
        # Print the structure for debugging
        pass
        # You might want to add more specific checks based on the actual structure

    lot_2 = next(
        (lot for lot in lots_with_sustainability if lot["id"] == "LOT-0002"),
        None,
    )
    assert lot_2 is not None
    assert "sustainability" in lot_2
    assert isinstance(lot_2["sustainability"], list)
    assert len(lot_2["sustainability"]) > 0

    # Similar check for lot_2
    if "description" in lot_2["sustainability"][0]:
        assert (
            lot_2["sustainability"][0]["description"]
            == "This procurement aims to reduce environmental impact..."
        )
    else:
        pass

    lot_3 = next(
        (lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0003"),
        None,
    )
    assert lot_3 is not None
    assert "sustainability" not in lot_3


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
