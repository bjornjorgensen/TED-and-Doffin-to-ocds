# tests/test_bt_44_Lot.py
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
    output_files = list(output_dir.glob("*_release_0.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_44_lot_integration(tmp_path, setup_logging, temp_output_dir) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:AwardingTerms>
                    <cac:Prize>
                        <cbc:RankCode>1</cbc:RankCode>
                    </cac:Prize>
                    <cac:Prize>
                        <cbc:RankCode>2</cbc:RankCode>
                    </cac:Prize>
                </cac:AwardingTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """
    xml_file = tmp_path / "test_input_prize_rank.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # logger.info("Test result: %s", json.dumps(result, indent=2) # Logging disabled)

    # Verify the results
    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"

    # Check the number of lots
    assert (
        len(result["tender"]["lots"]) == 1
    ), f"Expected 1 lot, got {len(result['tender']['lots'])}"

    lot = result["tender"]["lots"][0]

    # Check lot ID
    assert lot["id"] == "LOT-0001", f"Expected lot id 'LOT-0001', got {lot['id']}"

    # Check designContest structure
    assert "designContest" in lot, "Expected 'designContest' in lot"
    assert "prizes" in lot["designContest"], "Expected 'prizes' in designContest"
    assert "details" in lot["designContest"]["prizes"], "Expected 'details' in prizes"

    prizes = lot["designContest"]["prizes"]["details"]

    # Check number of prizes
    assert len(prizes) == 2, f"Expected 2 prizes, got {len(prizes)}"

    # Check first prize (highest rank - first position in array)
    assert prizes[0]["id"] == "0", f"Expected first prize id '0', got {prizes[0]['id']}"
    # The rank is represented by position in array, no explicit rank attribute
    assert "rank" not in prizes[0], "Rank should not be present in prize object"

    # Check second prize (second-highest rank - second position in array)
    assert prizes[1]["id"] == "1", f"Expected second prize id '1', got {prizes[1]['id']}"
    # The rank is represented by position in array, no explicit rank attribute
    assert "rank" not in prizes[1], "Rank should not be present in prize object"


if __name__ == "__main__":
    pytest.main(["-v"])
