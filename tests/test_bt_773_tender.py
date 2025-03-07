# tests/test_bt_773_Tender.py
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


def test_bt_773_tender_subcontracting_integration(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    
    logger = setup_logging

    xml_content = """
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotTender>
                                <cbc:ID schemeName="tender">TEN-0001</cbc:ID>
                                <efac:SubcontractingTerm>
                                    <efbc:TermCode listName="applicability">yes</efbc:TermCode>
                                </efac:SubcontractingTerm>
                            </efac:LotTender>
                            <efac:LotTender>
                                <cbc:ID schemeName="tender">TEN-0002</cbc:ID>
                                <efac:SubcontractingTerm>
                                    <efbc:TermCode listName="applicability">no</efbc:TermCode>
                                </efac:SubcontractingTerm>
                            </efac:LotTender>
                            <efac:LotTender>
                                <cbc:ID schemeName="tender">TEN-0003</cbc:ID>
                            </efac:LotTender>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_subcontracting.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    assert "bids" in result, "Expected 'bids' in result"
    assert "details" in result["bids"], "Expected 'details' in bids"
    
    bids = result["bids"]["details"]
    
    assert len(bids) == 3, "All bids should be included regardless of subcontracting information"
    
    bid_1 = next((bid for bid in bids if bid["id"] == "TEN-0001"), None)
    assert bid_1 is not None, "Bid TEN-0001 should be included"
    assert bid_1["hasSubcontracting"] is True, "Expected 'hasSubcontracting' to be True for 'yes' value"
    
    bid_2 = next((bid for bid in bids if bid["id"] == "TEN-0002"), None)
    assert bid_2 is not None, "Bid TEN-0002 should be included"
    assert bid_2["hasSubcontracting"] is False, "Expected 'hasSubcontracting' to be False for 'no' value"

    bid_3 = next((bid for bid in bids if bid["id"] == "TEN-0003"), None)
    assert bid_3 is not None, "Bid TEN-0003 should be included even without subcontracting information"
    assert "hasSubcontracting" not in bid_3, "No hasSubcontracting field should be present when info is missing"


def test_bt_773_tender_subcontracting_missing_subcontracting_term(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    
    logger = setup_logging

    xml_content = """
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotTender>
                                <cbc:ID schemeName="tender">TEN-0004</cbc:ID>
                                <!-- SubcontractingTerm is missing -->
                            </efac:LotTender>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_subcontracting_missing_term.xml"
    xml_file.write_text(xml_content)

    
    result = run_main_and_get_result(xml_file, temp_output_dir)

    assert "bids" in result, "Expected 'bids' section in result"
    assert "details" in result["bids"], "Expected 'details' array in bids section"
    
    assert len(result["bids"]["details"]) == 1, "All bids should be included regardless of subcontracting information"

    bid_4 = next((bid for bid in result["bids"]["details"] if bid["id"] == "TEN-0004"), None)
    assert bid_4 is not None, "Bid TEN-0004 should be included even without subcontracting information"
    assert "hasSubcontracting" not in bid_4, "No hasSubcontracting field should be present when info is missing"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
