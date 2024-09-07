# tests/test_BT_735_Lot.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main


def test_bt_735_lot_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
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
    </root>
    """
    xml_file = tmp_path / "test_input_cvd_contract_type.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json", "r") as f:
        result = json.load(f)

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
    pytest.main()
