# tests/test_OPP_022_Contract.py
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


def test_opp_022_contract_significance_integration(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging

    # Test XML with AssetSignificance (OPP-022-Contract) field with correct XML path structure
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
        xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:SettledContract>
                                <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                                <efac:DurationJustification>
                                    <efac:AssetsList>
                                        <efac:Asset>
                                            <efbc:AssetSignificance>30</efbc:AssetSignificance>
                                        </efac:Asset>
                                    </efac:AssetsList>
                                </efac:DurationJustification>
                            </efac:SettledContract>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                                <efac:SettledContract>
                                    <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                                </efac:SettledContract>
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
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
    xml_file = tmp_path / "test_input_asset_significance.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Verify the results
    # Check overall structure
    assert "tender" in result, "Result should contain tender object"
    assert "lots" in result["tender"], "Tender should contain lots array"
    assert len(result["tender"]["lots"]) == 1, f"Expected 1 lot, got {len(result['tender']['lots'])}"
    
    # Check lot-specific structure
    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001", f"Expected lot ID LOT-0001, got {lot['id']}"
    assert "essentialAssets" in lot, "Lot should contain essentialAssets array"
    assert len(lot["essentialAssets"]) == 1, f"Expected 1 essential asset, got {len(lot['essentialAssets'])}"
    
    # Check significance value (OPP-022-Contract mapping)
    asset = lot["essentialAssets"][0]
    assert "significance" in asset, "Essential asset should contain significance field"
    assert asset["significance"] == "30", f"Expected significance value 30, got {asset['significance']}"


if __name__ == "__main__":
    pytest.main(["-v"])
