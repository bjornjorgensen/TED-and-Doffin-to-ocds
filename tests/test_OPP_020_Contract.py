# tests/test_OPP_020_Contract.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_opp_020_contract_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <efac:NoticeResult>
            <efac:LotResult>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                </efac:TenderLot>
                <efac:SettledContract>
                    <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                </efac:SettledContract>
            </efac:LotResult>
            <efac:SettledContract>
                <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                <efac:DurationJustification>
                    <efbc:ExtendedDurationIndicator>true</efbc:ExtendedDurationIndicator>
                </efac:DurationJustification>
            </efac:SettledContract>
        </efac:NoticeResult>
    </root>
    """
    xml_file = tmp_path / "test_input.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001"
    assert "hasEssentialAssets" in lot
    assert lot["hasEssentialAssets"] == True

def test_opp_020_contract_integration_false(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <efac:NoticeResult>
            <efac:LotResult>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
                </efac:TenderLot>
                <efac:SettledContract>
                    <cbc:ID schemeName="contract">CON-0002</cbc:ID>
                </efac:SettledContract>
            </efac:LotResult>
            <efac:SettledContract>
                <cbc:ID schemeName="contract">CON-0002</cbc:ID>
                <efac:DurationJustification>
                    <efbc:ExtendedDurationIndicator>false</efbc:ExtendedDurationIndicator>
                </efac:DurationJustification>
            </efac:SettledContract>
        </efac:NoticeResult>
    </root>
    """
    xml_file = tmp_path / "test_input_false.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    assert result["tender"]["lots"][0]["id"] == "LOT-0002"  # Check for the correct lot ID

    lot = result["tender"]["lots"][0]
    assert "hasEssentialAssets" not in lot

def test_opp_020_021_022_023_contract_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <efac:NoticeResult>
            <efac:SettledContract>
                <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                <efac:DurationJustification>
                    <efbc:ExtendedDurationIndicator>true</efbc:ExtendedDurationIndicator>
                    <efac:AssetsList>
                        <efac:Asset>
                            <efbc:AssetDescription>Asset 1 blabla</efbc:AssetDescription>
                            <efbc:AssetSignificance>30</efbc:AssetSignificance>
                            <efbc:AssetPredominance>40</efbc:AssetPredominance>
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
    </root>
    """
    xml_file = tmp_path / "test_input_essential_assets.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001"
    assert lot["hasEssentialAssets"] == True
    assert "essentialAssets" in lot
    assert len(lot["essentialAssets"]) == 1
    asset = lot["essentialAssets"][0]
    assert asset["description"] == "Asset 1 blabla"
    assert asset["significance"] == "30"
    assert asset["predominance"] == "40"

if __name__ == "__main__":
    pytest.main()