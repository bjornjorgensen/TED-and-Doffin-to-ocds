# tests/test_BT_271_Procedure.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_271_procedure_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
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
    </root>
    """
    xml_file = tmp_path / "test_input_bt_271_procedure.xml"
    xml_file.write_text(xml_content)

    result = main(str(xml_file), "ocds-test-prefix")

    assert "tender" in result, "tender not found in result"
    assert "techniques" in result["tender"], "techniques not found in tender"
    assert "frameworkAgreement" in result["tender"]["techniques"], "frameworkAgreement not found in techniques"
    assert "value" in result["tender"]["techniques"]["frameworkAgreement"], "value not found in frameworkAgreement"
    assert result["tender"]["techniques"]["frameworkAgreement"]["value"]["amount"] == 120000, f"Expected amount 120000, got {result['tender']['techniques']['frameworkAgreement']['value']['amount']}"
    assert result["tender"]["techniques"]["frameworkAgreement"]["value"]["currency"] == "EUR", f"Expected currency 'EUR', got {result['tender']['techniques']['frameworkAgreement']['value']['currency']}"

if __name__ == "__main__":
    pytest.main()