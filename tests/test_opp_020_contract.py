# tests/test_OPP_020_Contract.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_opp_020_contract_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <efac:noticeResult>
            <efac:LotResult>
                <efac:TenderLot>
                    <cbc:ID schemeName="lot">LOT-0001</cbc:ID>
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
        </efac:noticeResult>
    </root>
    """
    xml_file = tmp_path / "test_input_extended_duration_indicator.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001"
    assert "hasEssentialAssets" in lot
    assert lot["hasEssentialAssets"] is True


def test_opp_020_contract_integration_false(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <efac:noticeResult>
            <efac:LotResult>
                <efac:TenderLot>
                    <cbc:ID schemeName="lot">LOT-0002</cbc:ID>
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
        </efac:noticeResult>
    </root>
    """
    xml_file = tmp_path / "test_input_extended_duration_indicator_false.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0002"
    assert "hasEssentialAssets" in lot
    assert lot["hasEssentialAssets"] is False


if __name__ == "__main__":
    pytest.main()
