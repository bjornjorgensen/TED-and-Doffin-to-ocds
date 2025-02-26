# tests/test_bt_553_Tender.py
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


def test_bt_553_tender_integration(tmp_path, setup_logging, temp_output_dir) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
        xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <efac:noticeResult>
            <efac:LotTender>
                <cbc:ID schemeName="tender">TEN-0001</cbc:ID>
                <efac:SubcontractingTerm>
                    <efbc:TermCode listName="applicability">applicable</efbc:TermCode>
                    <efbc:TermAmount currencyID="EUR">9999999.99</efbc:TermAmount>
                </efac:SubcontractingTerm>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                </efac:TenderLot>
            </efac:LotTender>
        </efac:noticeResult>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_subcontracting_value.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)
    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    # Verify the results
    assert "bids" in result, "Expected 'bids' in result"
    assert "details" in result["bids"], "Expected 'details' in bids"
    assert (
        len(result["bids"]["details"]) == 1
    ), f"Expected 1 bid, got {len(result['bids']['details'])}"

    bid = result["bids"]["details"][0]
    assert bid["id"] == "TEN-0001", f"Expected bid id 'TEN-0001', got {bid['id']}"
    assert "subcontracting" in bid, "Expected 'subcontracting' in bid"
    assert "value" in bid["subcontracting"], "Expected 'value' in bid subcontracting"
    assert (
        bid["subcontracting"]["value"]["amount"] == 9999999.99
    ), f"Expected amount 9999999.99, got {bid['subcontracting']['value']['amount']}"
    assert (
        bid["subcontracting"]["value"]["currency"] == "EUR"
    ), f"Expected currency 'EUR', got {bid['subcontracting']['value']['currency']}"
    assert bid["relatedLots"] == [
        "LOT-0001"
    ], f"Expected relatedLots ['LOT-0001'], got {bid['relatedLots']}"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
