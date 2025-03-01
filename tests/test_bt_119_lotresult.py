# tests/test_bt_119_LotResult.py
import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.converters.eforms.bt_119_lotresult import parse_dps_termination, merge_dps_termination
from src.ted_and_doffin_to_ocds.main import configure_logging, main

@pytest.fixture(scope="module")
def setup_logging():
    configure_logging()
    return logging.getLogger(__name__)

@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)

def run_main_and_get_result(xml_file, output_dir):
    main(
        input_path=str(xml_file),
        output_folder=str(output_dir),
        ocid_prefix="ocds-123456"
    )
    json_files = list(Path(output_dir).glob("*.json"))
    assert len(json_files) > 0, "No JSON files were created"
    with open(json_files[0]) as f:
        return json.load(f)

def test_bt_119_dps_termination_missing_data(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID>LOT-0001</cbc:ID>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """
    xml_file = tmp_path / "test_input_bt119_dps_termination_missing.xml"
    xml_file.write_text(xml_content)
    result = run_main_and_get_result(xml_file, temp_output_dir)
    
    # When no DPS termination data is present, there should be no techniques data
    assert "tender" not in result or (
        "lots" in result["tender"]
        and all(
            "techniques" not in lot or "dynamicPurchasingSystem" not in lot["techniques"]
            for lot in result["tender"]["lots"]
        )
    ), "Did not expect DPS termination data when indicator is missing"

def test_parse_dps_termination_with_lotid():
    """Test parsing DPS termination when LotResult has explicit reference to TenderLot."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
        xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotResult>
                                <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                                <efbc:DPSTerminationIndicator>true</efbc:DPSTerminationIndicator>
                            </efac:LotResult>
                            <efac:TenderLot>
                                <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                            </efac:TenderLot>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </ContractAwardNotice>
    """
    
    result = parse_dps_termination(xml_content)
    
    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert "techniques" in result["tender"]["lots"][0]
    assert "dynamicPurchasingSystem" in result["tender"]["lots"][0]["techniques"]
    assert result["tender"]["lots"][0]["techniques"]["dynamicPurchasingSystem"]["status"] == "terminated"

def test_parse_dps_termination_multiple_lots():
    """Test parsing DPS termination with multiple lots."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
        xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotResult>
                                <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                                <efbc:DPSTerminationIndicator>true</efbc:DPSTerminationIndicator>
                            </efac:LotResult>
                            <efac:LotResult>
                                <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
                                <efbc:DPSTerminationIndicator>true</efbc:DPSTerminationIndicator>
                            </efac:LotResult>
                            <efac:TenderLot>
                                <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                            </efac:TenderLot>
                            <efac:TenderLot>
                                <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
                            </efac:TenderLot>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </ContractAwardNotice>
    """
    
    result = parse_dps_termination(xml_content)
    
    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 2
    
    lot_ids = [lot["id"] for lot in result["tender"]["lots"]]
    assert "LOT-0001" in lot_ids
    assert "LOT-0002" in lot_ids
    
    for lot in result["tender"]["lots"]:
        assert "techniques" in lot
        assert "dynamicPurchasingSystem" in lot["techniques"]
        assert lot["techniques"]["dynamicPurchasingSystem"]["status"] == "terminated"

def test_parse_dps_termination_false_indicator():
    """Test parsing DPS termination with indicator set to false."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
        xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotResult>
                                <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                                <efbc:DPSTerminationIndicator>false</efbc:DPSTerminationIndicator>
                            </efac:LotResult>
                            <efac:TenderLot>
                                <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                            </efac:TenderLot>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </ContractAwardNotice>
    """
    
    result = parse_dps_termination(xml_content)
    
    assert result is None or len(result["tender"]["lots"]) == 0

def test_merge_dps_termination():
    """Test merging DPS termination data into an existing OCDS release."""
    # Prepare test data
    dps_termination_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "techniques": {
                        "dynamicPurchasingSystem": {
                            "status": "terminated"
                        }
                    }
                }
            ]
        }
    }
    
    # Test merging into empty release
    empty_release = {}
    merge_dps_termination(empty_release, dps_termination_data)
    assert "tender" in empty_release
    assert "lots" in empty_release["tender"]
    assert len(empty_release["tender"]["lots"]) == 1
    assert empty_release["tender"]["lots"][0]["id"] == "LOT-0001"
    assert empty_release["tender"]["lots"][0]["techniques"]["dynamicPurchasingSystem"]["status"] == "terminated"
    
    # Test merging into existing release with the same lot
    existing_release = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "title": "Existing lot"
                }
            ]
        }
    }
    merge_dps_termination(existing_release, dps_termination_data)
    assert len(existing_release["tender"]["lots"]) == 1
    assert existing_release["tender"]["lots"][0]["id"] == "LOT-0001"
    assert existing_release["tender"]["lots"][0]["title"] == "Existing lot"
    assert "techniques" in existing_release["tender"]["lots"][0]
    assert "dynamicPurchasingSystem" in existing_release["tender"]["lots"][0]["techniques"]
    assert existing_release["tender"]["lots"][0]["techniques"]["dynamicPurchasingSystem"]["status"] == "terminated"
    
    # Test merging into existing release with different lots
    different_release = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0002",
                    "title": "Different lot"
                }
            ]
        }
    }
    merge_dps_termination(different_release, dps_termination_data)
    assert len(different_release["tender"]["lots"]) == 2
    lot_ids = [lot["id"] for lot in different_release["tender"]["lots"]]
    assert "LOT-0001" in lot_ids
    assert "LOT-0002" in lot_ids

def test_dps_termination_end_to_end(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    """Test the complete workflow from XML parsing to OCDS output."""
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
        xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotResult>
                                <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                                <efbc:DPSTerminationIndicator>true</efbc:DPSTerminationIndicator>
                            </efac:LotResult>
                            <efac:TenderLot>
                                <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                            </efac:TenderLot>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </ContractAwardNotice>
    """
    
    xml_file = tmp_path / "test_input_bt119_dps_termination.xml"
    xml_file.write_text(xml_content)
    
    result = run_main_and_get_result(xml_file, temp_output_dir)
    
    # Verify the final OCDS output contains the expected DPS termination data
    assert "tender" in result
    assert "lots" in result["tender"]
    assert any(
        lot["id"] == "LOT-0001" and 
        "techniques" in lot and 
        "dynamicPurchasingSystem" in lot["techniques"] and 
        lot["techniques"]["dynamicPurchasingSystem"]["status"] == "terminated"
        for lot in result["tender"]["lots"]
    ), "Expected to find a lot with terminated DPS status"

if __name__ == "__main__":
    pytest.main(["-v", "-s"])
