# tests/test_OPT_155_156_LotResult.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_vehicle_type_and_numeric_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                                <efac:StrategicProcurement>
                                    <efac:StrategicProcurementInformation>
                                        <efac:ProcurementDetails>
                                            <efac:StrategicProcurementStatistics>
                                                <efbc:StatisticsCode listName="vehicles">vehicles</efbc:StatisticsCode>
                                                <efbc:StatisticsNumeric>10</efbc:StatisticsNumeric>
                                            </efac:StrategicProcurementStatistics>
                                            <efac:StrategicProcurementStatistics>
                                                <efbc:StatisticsCode listName="vehicles">vehicles-zero-emission</efbc:StatisticsCode>
                                                <efbc:StatisticsNumeric>3</efbc:StatisticsNumeric>
                                            </efac:StrategicProcurementStatistics>
                                            <efac:StrategicProcurementStatistics>
                                                <efbc:StatisticsCode listName="vehicles">vehicles-clean</efbc:StatisticsCode>
                                                <efbc:StatisticsNumeric>2</efbc:StatisticsNumeric>
                                            </efac:StrategicProcurementStatistics>
                                        </efac:ProcurementDetails>
                                    </efac:StrategicProcurementInformation>
                                </efac:StrategicProcurement>
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                                </efac:TenderLot>
                            </efac:LotResult>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_vehicle_type_and_numeric.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "awards" in result
    assert len(result["awards"]) == 1
    award = result["awards"][0]
    assert award["id"] == "RES-0001"
    assert "items" in award
    assert len(award["items"]) == 3

    vehicle_types = {item["id"]: item for item in award["items"]}

    assert "vehicles-zero-emission" in vehicle_types
    assert vehicle_types["vehicles-zero-emission"]["quantity"] == 3
    assert vehicle_types["vehicles-zero-emission"]["additionalClassifications"][0]["scheme"] == "vehicles"
    assert vehicle_types["vehicles-zero-emission"]["additionalClassifications"][0]["id"] == "vehicles-zero-emission"
    assert vehicle_types["vehicles-zero-emission"]["additionalClassifications"][0]["description"] == "vehicles zero emission"

    assert "vehicles-clean" in vehicle_types
    assert vehicle_types["vehicles-clean"]["quantity"] == 2
    assert vehicle_types["vehicles-clean"]["additionalClassifications"][0]["scheme"] == "vehicles"
    assert vehicle_types["vehicles-clean"]["additionalClassifications"][0]["id"] == "vehicles-clean"
    assert vehicle_types["vehicles-clean"]["additionalClassifications"][0]["description"] == "vehicles clean"

    assert "vehicles-other" in vehicle_types
    assert vehicle_types["vehicles-other"]["quantity"] == 5
    assert vehicle_types["vehicles-other"]["additionalClassifications"][0]["scheme"] == "vehicles"
    assert vehicle_types["vehicles-other"]["additionalClassifications"][0]["id"] == "vehicles-other"
    assert vehicle_types["vehicles-other"]["additionalClassifications"][0]["description"] == "vehicles other"

    assert award["relatedLots"] == ["LOT-0001"]

def test_vehicle_type_and_numeric_no_other_vehicles(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0002</cbc:ID>
                                <efac:StrategicProcurement>
                                    <efac:StrategicProcurementInformation>
                                        <efac:ProcurementDetails>
                                            <efac:StrategicProcurementStatistics>
                                                <efbc:StatisticsCode listName="vehicles">vehicles</efbc:StatisticsCode>
                                                <efbc:StatisticsNumeric>5</efbc:StatisticsNumeric>
                                            </efac:StrategicProcurementStatistics>
                                            <efac:StrategicProcurementStatistics>
                                                <efbc:StatisticsCode listName="vehicles">vehicles-zero-emission</efbc:StatisticsCode>
                                                <efbc:StatisticsNumeric>3</efbc:StatisticsNumeric>
                                            </efac:StrategicProcurementStatistics>
                                            <efac:StrategicProcurementStatistics>
                                                <efbc:StatisticsCode listName="vehicles">vehicles-clean</efbc:StatisticsCode>
                                                <efbc:StatisticsNumeric>2</efbc:StatisticsNumeric>
                                            </efac:StrategicProcurementStatistics>
                                        </efac:ProcurementDetails>
                                    </efac:StrategicProcurementInformation>
                                </efac:StrategicProcurement>
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
                                </efac:TenderLot>
                            </efac:LotResult>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_vehicle_type_and_numeric_no_other.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "awards" in result
    assert len(result["awards"]) == 1
    award = result["awards"][0]
    assert award["id"] == "RES-0002"
    assert "items" in award
    assert len(award["items"]) == 2

    vehicle_types = {item["id"]: item for item in award["items"]}

    assert "vehicles-zero-emission" in vehicle_types
    assert vehicle_types["vehicles-zero-emission"]["quantity"] == 3

    assert "vehicles-clean" in vehicle_types
    assert vehicle_types["vehicles-clean"]["quantity"] == 2

    assert "vehicles-other" not in vehicle_types

    assert award["relatedLots"] == ["LOT-0002"]

def test_vehicle_type_and_numeric_no_data(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0003</cbc:ID>
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0003</cbc:ID>
                                </efac:TenderLot>
                            </efac:LotResult>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_vehicle_type_and_numeric_no_data.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "awards" not in result or len(result["awards"]) == 0

if __name__ == "__main__":
    pytest.main()