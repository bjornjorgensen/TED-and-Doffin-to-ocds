# tests/test_BT_723_LotResult.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main


def test_bt_723_lot_result_integration(tmp_path):
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
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_vehicle_category.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

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
    pytest.main()
