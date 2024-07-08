# tests/test_BT_271_LotsGroup.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_271_lots_group_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="LotsGroup">GLO-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:RequestedTenderTotal>
                    <ext:UBLExtensions>
                        <ext:UBLExtension>
                            <ext:ExtensionContent>
                                <efext:EformsExtension>
                                    <efbc:FrameworkMaximumAmount currencyID="EUR">120000</efbc:FrameworkMaximumAmount>
                                </efext:EformsExtension>
                            </ext:ExtensionContent>
                        </ext:UBLExtension>
                    </ext:UBLExtensions>
                </cac:RequestedTenderTotal>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_bt_271_lots_group.xml"
    xml_file.write_text(xml_content)

    result = main(str(xml_file), "ocds-test-prefix")

    assert "tender" in result, "tender not found in result"
    assert "lotGroups" in result["tender"], "lotGroups not found in tender"
    assert len(result["tender"]["lotGroups"]) == 1, f"Expected 1 lot group, got {len(result['tender']['lotGroups'])}"
    
    lot_group = result["tender"]["lotGroups"][0]
    assert lot_group["id"] == "GLO-0001", f"Expected lot group id 'GLO-0001', got {lot_group['id']}"
    assert "techniques" in lot_group, "techniques not found in lot group"
    assert "frameworkAgreement" in lot_group["techniques"], "frameworkAgreement not found in techniques"
    assert "value" in lot_group["techniques"]["frameworkAgreement"], "value not found in frameworkAgreement"
    assert lot_group["techniques"]["frameworkAgreement"]["value"]["amount"] == 120000, f"Expected amount 120000, got {lot_group['techniques']['frameworkAgreement']['value']['amount']}"
    assert lot_group["techniques"]["frameworkAgreement"]["value"]["currency"] == "EUR", f"Expected currency 'EUR', got {lot_group['techniques']['frameworkAgreement']['value']['currency']}"

if __name__ == "__main__":
    pytest.main()