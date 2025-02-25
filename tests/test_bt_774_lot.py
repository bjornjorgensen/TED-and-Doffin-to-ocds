# tests/test_bt_774_Lot.py
import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

from src.ted_and_doffin_to_ocds.converters.eforms.bt_774_lot import (
    ENVIRONMENTAL_IMPACT_MAPPING,
    merge_green_procurement,
    parse_green_procurement,
)

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
    try:
        main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    except Exception as e:
        pytest.fail(f"main() raised an exception: {e}")

    output_files = list(output_dir.glob("*.json"))
    logging.info("Output files found: %s", [file.name for file in output_files])
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_parse_green_procurement() -> None:
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
    xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cac:ProcurementProjectLot>
        <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
        <cac:ProcurementProject>
            <cac:ProcurementAdditionalType>
                <cbc:ProcurementTypeCode listName="environmental-impact">circ-econ</cbc:ProcurementTypeCode>
            </cac:ProcurementAdditionalType>
        </cac:ProcurementProject>
    </cac:ProcurementProjectLot>
</ContractNotice>
    """

    result = parse_green_procurement(xml_content)

    assert result is not None
    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"
    assert len(result["tender"]["lots"]) == 1, "Expected one lot in tender"
    assert result["tender"]["lots"][0]["id"] == "LOT-0001", "Lot ID mismatch"
    assert (
        result["tender"]["lots"][0]["hasSustainability"] is True
    ), "Expected 'hasSustainability' to be True"
    assert (
        len(result["tender"]["lots"][0]["sustainability"]) == 1
    ), "Expected one sustainability entry"
    assert (
        result["tender"]["lots"][0]["sustainability"][0]["goal"]
        == ENVIRONMENTAL_IMPACT_MAPPING["circ-econ"]
    ), "Sustainability goal mismatch"


def test_merge_green_procurement() -> None:
    release_json = {"tender": {"lots": [{"id": "LOT-0001", "title": "Existing Lot"}]}}

    green_procurement_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "hasSustainability": True,
                    "sustainability": [{"goal": "environmental.circularEconomy"}],
                },
            ],
        },
    }

    merge_green_procurement(release_json, green_procurement_data)

    assert (
        "hasSustainability" in release_json["tender"]["lots"][0]
    ), "Missing 'hasSustainability'"
    assert (
        release_json["tender"]["lots"][0]["hasSustainability"] is True
    ), "Expected 'hasSustainability' to be True"
    assert (
        "sustainability" in release_json["tender"]["lots"][0]
    ), "Missing 'sustainability'"
    assert (
        len(release_json["tender"]["lots"][0]["sustainability"]) == 1
    ), "Expected one sustainability entry"
    assert (
        release_json["tender"]["lots"][0]["sustainability"][0]["goal"]
        == "environmental.circularEconomy"
    ), "Sustainability goal mismatch"


def test_bt_774_lot_green_procurement_integration(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
    xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cac:ProcurementProjectLot>
        <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
        <cac:ProcurementProject>
            <cac:ProcurementAdditionalType>
                <cbc:ProcurementTypeCode listName="environmental-impact">circ-econ</cbc:ProcurementTypeCode>
            </cac:ProcurementAdditionalType>
        </cac:ProcurementProject>
    </cac:ProcurementProjectLot>
    <cac:ProcurementProjectLot>
        <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
        <cac:ProcurementProject>
            <cac:ProcurementAdditionalType>
                <cbc:ProcurementTypeCode listName="environmental-impact">biodiv-eco</cbc:ProcurementTypeCode>
            </cac:ProcurementAdditionalType>
        </cac:ProcurementProject>
    </cac:ProcurementProjectLot>
    <cac:ProcurementProjectLot>
        <cbc:ID schemeName="Lot">LOT-0003</cbc:ID>
        <cac:ProcurementProject>
            <cac:ProcurementAdditionalType>
                <cbc:ProcurementTypeCode listName="other-type">not-environmental</cbc:ProcurementTypeCode>
            </cac:ProcurementAdditionalType>
        </cac:ProcurementProject>
    </cac:ProcurementProjectLot>
</ContractNotice>
    """
    xml_file = tmp_path / "test_input_green_procurement.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    logger.info("Result: %s", json.dumps(result, indent=2))

    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"

    green_lots = [lot for lot in result["tender"]["lots"] if "sustainability" in lot]
    assert len(green_lots) == 2, "Expected two lots with sustainability information"

    lot_1 = next((lot for lot in green_lots if lot["id"] == "LOT-0001"), None)
    assert lot_1 is not None, "LOT-0001 should be included with sustainability"
    assert (
        lot_1["hasSustainability"] is True
    ), "Expected 'hasSustainability' to be True for LOT-0001"
    assert (
        len(lot_1["sustainability"]) == 1
    ), "Expected one sustainability entry for LOT-0001"
    assert (
        lot_1["sustainability"][0]["goal"] == ENVIRONMENTAL_IMPACT_MAPPING["circ-econ"]
    ), "Sustainability goal mismatch for LOT-0001"

    lot_2 = next((lot for lot in green_lots if lot["id"] == "LOT-0002"), None)
    assert lot_2 is not None, "LOT-0002 should be included with sustainability"
    assert (
        lot_2["hasSustainability"] is True
    ), "Expected 'hasSustainability' to be True for LOT-0002"
    assert (
        len(lot_2["sustainability"]) == 1
    ), "Expected one sustainability entry for LOT-0002"
    assert (
        lot_2["sustainability"][0]["goal"] == ENVIRONMENTAL_IMPACT_MAPPING["biodiv-eco"]
    ), "Sustainability goal mismatch for LOT-0002"

    lot_3 = next(
        (lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0003"), None
    )
    assert lot_3 is not None, "LOT-0003 should be present"
    assert "sustainability" not in lot_3, "Did not expect 'sustainability' in LOT-0003"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
