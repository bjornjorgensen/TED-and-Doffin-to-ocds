# tests/test_OPT_155_156_LotResult.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_opt_155_156_lotresult_vehicle_type_and_numeric_integration(tmp_path):
    xml_content = """
    <root xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
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
                                                <efbc:StatisticsCode listName="vehicles">vehicles-zero-emission</efbc:StatisticsCode>
                                                <efbc:StatisticsNumeric>5</efbc:StatisticsNumeric>
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
    assert len(award["items"]) == 1

    item = award["items"][0]
    assert item["id"] == "1"
    assert "additionalClassifications" in item
    assert len(item["additionalClassifications"]) == 1

    classification = item["additionalClassifications"][0]
    assert classification["scheme"] == "vehicles"
    assert classification["id"] == "vehicles-zero-emission"
    assert classification["description"] == "vehicles zero emission"

    assert award["relatedLots"] == ["LOT-0001"]

if __name__ == "__main__":
    pytest.main()