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
    # Logging disabled for tests
    logger = logging.getLogger(__name__)
    logger.disabled = True
    return logger


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


def test_bt_776_lot_procurement_innovation_integration(
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
                <cbc:ProcurementTypeCode listName="innovative-acquisition">proc-innov</cbc:ProcurementTypeCode>
            </cac:ProcurementAdditionalType>
        </cac:ProcurementProject>
    </cac:ProcurementProjectLot>
    <cac:ProcurementProjectLot>
        <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
        <cac:ProcurementProject>
            <cac:ProcurementAdditionalType>
                <cbc:ProcurementTypeCode listName="innovative-acquisition">mar-nov</cbc:ProcurementTypeCode>
            </cac:ProcurementAdditionalType>
        </cac:ProcurementProject>
    </cac:ProcurementProjectLot>
    <cac:ProcurementProjectLot>
        <cbc:ID schemeName="Lot">LOT-0003</cbc:ID>
        <cac:ProcurementProject>
            <cac:ProcurementAdditionalType>
                <cbc:ProcurementTypeCode listName="other-type">not-innovation</cbc:ProcurementTypeCode>
            </cac:ProcurementAdditionalType>
        </cac:ProcurementProject>
    </cac:ProcurementProjectLot>
</ContractNotice>
"""
    xml_file = tmp_path / "test_input_procurement_innovation.xml"
    xml_file.write_text(xml_content)
    # logger.info("Created XML file at %s", xml_file) # Logging disabled
    # logger.info("Output directory: %s", temp_output_dir) # Logging disabled

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)
    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    assert "tender" in result
    assert "lots" in result["tender"]

    innovation_lots = [
        lot for lot in result["tender"]["lots"] if "sustainability" in lot
    ]
    assert len(innovation_lots) == 2

    lot_1 = next((lot for lot in innovation_lots if lot["id"] == "LOT-0001"), None)
    assert lot_1 is not None
    assert lot_1["hasSustainability"] is True
    assert len(lot_1["sustainability"]) == 1
    assert lot_1["sustainability"][0]["goal"] == "economic.processInnovation"

    lot_2 = next((lot for lot in innovation_lots if lot["id"] == "LOT-0002"), None)
    assert lot_2 is not None
    assert lot_2["hasSustainability"] is True
    assert len(lot_2["sustainability"]) == 1
    assert lot_2["sustainability"][0]["goal"] == "economic.marketInnovationPromotion"

    lot_3 = next(
        (lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0003"),
        None,
    )
    assert lot_3 is not None
    assert "sustainability" not in lot_3


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
