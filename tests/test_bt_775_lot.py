# tests/test_bt_775_Lot.py
import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

from src.ted_and_doffin_to_ocds.converters.eforms.bt_775_lot import (
    SOCIAL_OBJECTIVE_MAPPING,
    SUSTAINABILITY_STRATEGIES,
    merge_social_procurement,
    parse_social_procurement,
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
    try:
        main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    except Exception as e:
        pytest.fail(f"main() raised an exception: {e}")

    output_files = list(output_dir.glob("*.json"))
    logging.info("Output files found: %s", [file.name for file in output_files])
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_parse_social_procurement() -> None:
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
    xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cac:ProcurementProjectLot>
        <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
        <cac:ProcurementProject>
            <cac:ProcurementAdditionalType>
                <cbc:ProcurementTypeCode listName="social-objective">et-eq</cbc:ProcurementTypeCode>
            </cac:ProcurementAdditionalType>
        </cac:ProcurementProject>
    </cac:ProcurementProjectLot>
</ContractNotice>
    """

    result = parse_social_procurement(xml_content)

    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert result["tender"]["lots"][0]["hasSustainability"] is True
    assert len(result["tender"]["lots"][0]["sustainability"]) == 1
    assert (
        result["tender"]["lots"][0]["sustainability"][0]["goal"]
        == SOCIAL_OBJECTIVE_MAPPING["et-eq"]
    )
    assert set(result["tender"]["lots"][0]["sustainability"][0]["strategies"]) == set(
        SUSTAINABILITY_STRATEGIES,
    )


def test_merge_social_procurement() -> None:
    release_json = {"tender": {"lots": [{"id": "LOT-0001", "title": "Existing Lot"}]}}

    social_procurement_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "hasSustainability": True,
                    "sustainability": [
                        {
                            "goal": "social.ethnicEquality",
                            "strategies": SUSTAINABILITY_STRATEGIES,
                        },
                    ],
                },
            ],
        },
    }

    merge_social_procurement(release_json, social_procurement_data)

    assert "hasSustainability" in release_json["tender"]["lots"][0]
    assert release_json["tender"]["lots"][0]["hasSustainability"] is True
    assert "sustainability" in release_json["tender"]["lots"][0]
    assert len(release_json["tender"]["lots"][0]["sustainability"]) == 1
    assert (
        release_json["tender"]["lots"][0]["sustainability"][0]["goal"]
        == "social.ethnicEquality"
    )
    assert set(
        release_json["tender"]["lots"][0]["sustainability"][0]["strategies"],
    ) == set(SUSTAINABILITY_STRATEGIES)


def test_bt_775_lot_social_procurement_integration(
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
                <cbc:ProcurementTypeCode listName="social-objective">et-eq</cbc:ProcurementTypeCode>
            </cac:ProcurementAdditionalType>
        </cac:ProcurementProject>
    </cac:ProcurementProjectLot>
    <cac:ProcurementProjectLot>
        <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
        <cac:ProcurementProject>
            <cac:ProcurementAdditionalType>
                <cbc:ProcurementTypeCode listName="social-objective">gen-eq</cbc:ProcurementTypeCode>
            </cac:ProcurementAdditionalType>
        </cac:ProcurementProject>
    </cac:ProcurementProjectLot>
    <cac:ProcurementProjectLot>
        <cbc:ID schemeName="Lot">LOT-0003</cbc:ID>
        <cac:ProcurementProject>
            <cac:ProcurementAdditionalType>
                <cbc:ProcurementTypeCode listName="other-type">not-social</cbc:ProcurementTypeCode>
            </cac:ProcurementAdditionalType>
        </cac:ProcurementProject>
    </cac:ProcurementProjectLot>
</ContractNotice>
    """
    xml_file = tmp_path / "test_input_social_procurement.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"

    social_lots = [lot for lot in result["tender"]["lots"] if "sustainability" in lot]
    assert len(social_lots) == 2, "Expected two lots with sustainability information"

    lot_1 = next((lot for lot in social_lots if lot["id"] == "LOT-0001"), None)
    assert lot_1 is not None, "LOT-0001 should be included with sustainability"
    assert (
        lot_1["hasSustainability"] is True
    ), "Expected 'hasSustainability' to be True for LOT-0001"
    assert (
        len(lot_1["sustainability"]) == 1
    ), "Expected one sustainability entry for LOT-0001"
    assert (
        lot_1["sustainability"][0]["goal"] == SOCIAL_OBJECTIVE_MAPPING["et-eq"]
    ), "Sustainability goal mismatch for LOT-0001"

    lot_2 = next((lot for lot in social_lots if lot["id"] == "LOT-0002"), None)
    assert lot_2 is not None, "LOT-0002 should be included with sustainability"
    assert (
        lot_2["hasSustainability"] is True
    ), "Expected 'hasSustainability' to be True for LOT-0002"
    assert (
        len(lot_2["sustainability"]) == 1
    ), "Expected one sustainability entry for LOT-0002"
    assert (
        lot_2["sustainability"][0]["goal"] == SOCIAL_OBJECTIVE_MAPPING["gen-eq"]
    ), "Sustainability goal mismatch for LOT-0002"

    lot_3 = next(
        (lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0003"),
        None,
    )
    assert lot_3 is not None, "LOT-0003 should be present"
    assert "sustainability" not in lot_3, "Did not expect 'sustainability' in LOT-0003"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
