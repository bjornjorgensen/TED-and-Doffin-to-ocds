# tests/test_bt_735_Lot.py
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


def test_bt_735_lot_integration(tmp_path, setup_logging, temp_output_dir) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
          xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <ext:UBLExtensions>
                    <ext:UBLExtension>
                        <ext:ExtensionContent>
                            <efext:EformsExtension>
                                <efac:StrategicProcurement>
                                    <efac:StrategicProcurementInformation>
                                        <efbc:ProcurementCategoryCode listName="cvd-contract-type">oth-serv-contr</efbc:ProcurementCategoryCode>
                                    </efac:StrategicProcurementInformation>
                                </efac:StrategicProcurement>
                            </efext:EformsExtension>
                        </ext:ExtensionContent>
                    </ext:UBLExtension>
                </ext:UBLExtensions>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </ContractNotice>
    """
    xml_file = tmp_path / "test_input_cvd_contract_type.xml"
    xml_file.write_text(xml_content)
    # logger.info("Created XML file at %s", xml_file) # Logging disabled
    # logger.info("Output directory: %s", temp_output_dir) # Logging disabled

    result = run_main_and_get_result(xml_file, temp_output_dir)
    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"
    assert (
        len(result["tender"]["lots"]) == 1
    ), f"Expected 1 lot, got {len(result['tender']['lots'])}"

    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001", f"Expected lot id 'LOT-0001', got {lot['id']}"
    assert (
        "additionalClassifications" in lot
    ), "Expected 'additionalClassifications' in lot"
    assert (
        len(lot["additionalClassifications"]) == 1
    ), f"Expected 1 additional classification, got {len(lot['additionalClassifications'])}"

    classification = lot["additionalClassifications"][0]
    assert (
        classification["id"] == "oth-serv-contr"
    ), f"Expected classification id 'oth-serv-contr', got {classification['id']}"
    assert (
        classification["scheme"] == "eu-cvd-contract-type"
    ), f"Expected scheme 'eu-cvd-contract-type', got {classification['scheme']}"
    assert (
        classification["description"] == "Other service contract"
    ), f"Expected description 'Other service contract', got {classification['description']}"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
