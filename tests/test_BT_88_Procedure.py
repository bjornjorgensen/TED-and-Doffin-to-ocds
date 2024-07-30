# tests/test_BT_88_Procedure.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_88_procedure_features_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingProcess>
            <cbc:Description languageID="ENG">A two stage procedure with initial evaluation followed by negotiation.</cbc:Description>
        </cac:TenderingProcess>
    </root>
    """
    xml_file = tmp_path / "test_input_procedure_features.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "tender" in result
    assert "procurementMethodDetails" in result["tender"]
    assert result["tender"]["procurementMethodDetails"] == "A two stage procedure with initial evaluation followed by negotiation."

def test_bt_88_procedure_features_missing(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingProcess>
            <!-- No Description element -->
        </cac:TenderingProcess>
    </root>
    """
    xml_file = tmp_path / "test_input_procedure_features_missing.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "tender" not in result

if __name__ == "__main__":
    pytest.main()