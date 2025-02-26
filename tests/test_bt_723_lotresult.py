# tests/test_bt_723_LotResult.py
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


def test_bt_723_lot_result_integration(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
          xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:noticeResult>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                                </efac:TenderLot>
                                <efac:StrategicProcurement>
                                    <efac:StrategicProcurementInformation>
                                        <efac:ProcurementDetails>
                                            <efbc:AssetCategoryCode listName="vehicle-category">n2-n3</efbc:AssetCategoryCode>
                                        </efac:ProcurementDetails>
                                    </efac:StrategicProcurementInformation>
                                </efac:StrategicProcurement>
                            </efac:LotResult>
                        </efac:noticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </ContractAwardNotice>
    """
    xml_file = tmp_path / "test_input_vehicle_category.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)
    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    assert "awards" in result, "Expected 'awards' in result"
    assert len(result["awards"]) == 1, f"Expected 1 award, got {len(result['awards'])}"

    award = result["awards"][0]
    assert award["id"] == "RES-0001", f"Expected award id 'RES-0001', got {award['id']}"
    assert award["relatedLots"] == [
        "LOT-0001"
    ], f"Expected related lot 'LOT-0001', got {award['relatedLots']}"

    assert "items" in award, "Expected 'items' in award"
    assert len(award["items"]) == 1, f"Expected 1 item, got {len(award['items'])}"

    item = award["items"][0]
    assert item["id"] == "1", f"Expected item id '1', got {item['id']}"
    assert (
        "additionalClassifications" in item
    ), "Expected 'additionalClassifications' in item"
    assert (
        len(item["additionalClassifications"]) == 1
    ), f"Expected 1 additional classification, got {len(item['additionalClassifications'])}"

    classification = item["additionalClassifications"][0]
    assert (
        classification["scheme"] == "eu-vehicle-category"
    ), f"Expected scheme 'eu-vehicle-category', got {classification['scheme']}"
    assert (
        classification["id"] == "n2-n3"
    ), f"Expected id 'n2-n3', got {classification['id']}"
    assert (
        classification["description"] == "Truck (N2-N3)"
    ), f"Expected description 'Truck (N2-N3)', got {classification['description']}"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
