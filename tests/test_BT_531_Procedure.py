# tests/test_BT_531_Procedure.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main


def test_bt_531_procedure_additional_nature_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProject>
            <cac:ProcurementAdditionalType>
                <cbc:ProcurementTypeCode listName="contract-nature">works</cbc:ProcurementTypeCode>
            </cac:ProcurementAdditionalType>
        </cac:ProcurementProject>
        <cac:ProcurementProject>
            <cac:ProcurementAdditionalType>
                <cbc:ProcurementTypeCode listName="contract-nature">services</cbc:ProcurementTypeCode>
            </cac:ProcurementAdditionalType>
        </cac:ProcurementProject>
    </root>
    """
    xml_file = tmp_path / "test_input_procedure_additional_nature.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert (
        "additionalProcurementCategories" in result["tender"]
    ), "Expected 'additionalProcurementCategories' in tender"

    expected_categories = ["works", "services"]
    assert (
        set(result["tender"]["additionalProcurementCategories"])
        == set(expected_categories)
    ), f"Expected additionalProcurementCategories {expected_categories}, got {result['tender']['additionalProcurementCategories']}"


if __name__ == "__main__":
    pytest.main()
