# tests/test_OPP_040_Procedure.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_opp_040_procedure_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProject>
            <cac:ProcurementAdditionalType>
                <cbc:ProcurementTypeCode listName="transport-service">bus-s</cbc:ProcurementTypeCode>
            </cac:ProcurementAdditionalType>
        </cac:ProcurementProject>
    </root>
    """
    xml_file = tmp_path / "test_input_main_nature_sub_type.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" in result
    assert "additionalProcurementCategories" in result["tender"]
    assert "bus-s" in result["tender"]["additionalProcurementCategories"]


def test_opp_040_procedure_integration_multiple(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProject>
            <cac:ProcurementAdditionalType>
                <cbc:ProcurementTypeCode listName="transport-service">bus-s</cbc:ProcurementTypeCode>
            </cac:ProcurementAdditionalType>
            <cac:ProcurementAdditionalType>
                <cbc:ProcurementTypeCode listName="transport-service">tram-s</cbc:ProcurementTypeCode>
            </cac:ProcurementAdditionalType>
        </cac:ProcurementProject>
    </root>
    """
    xml_file = tmp_path / "test_input_main_nature_sub_type_multiple.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" in result
    assert "additionalProcurementCategories" in result["tender"]
    assert "bus-s" in result["tender"]["additionalProcurementCategories"]
    assert "tram-s" in result["tender"]["additionalProcurementCategories"]


if __name__ == "__main__":
    pytest.main()
