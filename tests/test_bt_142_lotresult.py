# tests/test_bt_142_LotResult.py
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


def test_bt_142_lotresult_integration(tmp_path, setup_logging, temp_output_dir) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                                <cbc:TenderResultCode listName="winner-selection-status">selec-w</cbc:TenderResultCode>
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                                </efac:TenderLot>
                            </efac:LotResult>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0002</cbc:ID>
                                <cbc:TenderResultCode listName="winner-selection-status">open-nw</cbc:TenderResultCode>
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
                                </efac:TenderLot>
                            </efac:LotResult>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0003</cbc:ID>
                                <cbc:TenderResultCode listName="winner-selection-status">clos-nw</cbc:TenderResultCode>
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0003</cbc:ID>
                                </efac:TenderLot>
                            </efac:LotResult>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_winner_chosen.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)
    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    # Verify the results
    assert "awards" in result, "Expected 'awards' in result"
    # Update expected number of awards to 3
    assert len(result["awards"]) == 3, f"Expected 3 awards, got {len(result['awards'])}"

    # Test for selec-w (winner chosen)
    selec_w_award = next((a for a in result["awards"] if a["id"] == "RES-0001"), None)
    assert selec_w_award is not None, "Missing award with ID RES-0001"
    assert selec_w_award["status"] == "active", f"Expected status 'active', got {selec_w_award['status']}"
    assert selec_w_award["statusDetails"] == "At least one winner was chosen.", "Unexpected statusDetails"
    assert selec_w_award["relatedLots"] == ["LOT-0001"], f"Expected relatedLots ['LOT-0001'], got {selec_w_award['relatedLots']}"

    # Test for clos-nw (no winner, closed)
    clos_nw_award = next((a for a in result["awards"] if a["id"] == "RES-0003"), None)
    assert clos_nw_award is not None, "Missing award with ID RES-0003"
    assert clos_nw_award["status"] == "unsuccessful", f"Expected status 'unsuccessful', got {clos_nw_award['status']}"
    assert clos_nw_award["statusDetails"] == "No winner was chosen and the competition is closed.", "Unexpected statusDetails"
    assert clos_nw_award["relatedLots"] == ["LOT-0003"], f"Expected relatedLots ['LOT-0003'], got {clos_nw_award['relatedLots']}"

    # Test for open-nw (ongoing)
    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"
    assert len(result["tender"]["lots"]) == 1, f"Expected 1 lot, got {len(result['tender']['lots'])}"

    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0002", f"Expected lot id 'LOT-0002', got {lot['id']}"
    assert lot["status"] == "active", f"Expected status 'active', got {lot['status']}"


def test_bt_142_parse_winner_chosen():
    """Unit test for parse_winner_chosen function."""
    from src.ted_and_doffin_to_ocds.converters.eforms.bt_142_lotresult import parse_winner_chosen

    # Add all required namespaces to fix parsing error
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <efac:NoticeResult>
            <efac:LotResult>
                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                <cbc:TenderResultCode listName="winner-selection-status">selec-w</cbc:TenderResultCode>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                </efac:TenderLot>
            </efac:LotResult>
        </efac:NoticeResult>
    </root>
    """
    
    result = parse_winner_chosen(xml_content)
    
    assert result is not None
    assert len(result["awards"]) == 1
    assert result["awards"][0]["status"] == "active"
    assert result["awards"][0]["id"] == "RES-0001"
    
    # Test with clos-nw status
    xml_content = xml_content.replace("selec-w", "clos-nw")
    result = parse_winner_chosen(xml_content)
    
    assert result is not None
    assert len(result["awards"]) == 1
    assert result["awards"][0]["status"] == "unsuccessful"
    
    # Test with open-nw status
    xml_content = xml_content.replace("clos-nw", "open-nw")
    result = parse_winner_chosen(xml_content)
    
    assert result is not None
    assert len(result["tender"]["lots"]) == 1
    assert result["tender"]["lots"][0]["status"] == "active"
    
    # Test with empty XML
    result = parse_winner_chosen("<root></root>")
    assert result is None


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
