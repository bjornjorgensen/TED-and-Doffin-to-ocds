# tests/test_bt_133_Lot.py
import json
import sys
import tempfile
from pathlib import Path
import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main

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

def test_bt_133_lot_integration(tmp_path, temp_output_dir) -> None:
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingProcess>
                <cac:OpenTenderEvent>
                    <cac:OccurenceLocation>
                        <cbc:Description>online at URL https://event-on-line.org/d22f65 ...</cbc:Description>
                    </cac:OccurenceLocation>
                </cac:OpenTenderEvent>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """
    # Create input XML file
    xml_file = tmp_path / "test_input_lot_bid_opening.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Verify the results
    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"
    assert (
        len(result["tender"]["lots"]) == 1
    ), f"Expected 1 lot, got {len(result['tender']['lots'])}"

    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001", f"Expected lot id 'LOT-0001', got {lot['id']}"
    assert "bidOpening" in lot, "Expected 'bidOpening' in lot"
    assert "location" in lot["bidOpening"], "Expected 'location' in bidOpening"
    assert (
        "description" in lot["bidOpening"]["location"]
    ), "Expected 'description' in location"

    expected_description = "online at URL https://event-on-line.org/d22f65 ..."
    assert (
        lot["bidOpening"]["location"]["description"] == expected_description
    ), f"Expected description '{expected_description}', got {lot['bidOpening']['location']['description']}"

if __name__ == "__main__":
    pytest.main(["-v", "-s"])
