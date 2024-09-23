# tests/test_bt_09_procedure.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_09_procedure_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingTerms>
            <cac:ProcurementLegislationDocumentReference>
                <cbc:ID>CrossBorderLaw</cbc:ID>
                <cbc:DocumentDescription languageID="ENG">Directive XYZ on Cross Border ...</cbc:DocumentDescription>
            </cac:ProcurementLegislationDocumentReference>
        </cac:TenderingTerms>
    </root>
    """
    xml_file = tmp_path / "test_input_cross_border_law.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "crossBorderLaw" in result["tender"], "Expected 'crossBorderLaw' in tender"
    assert (
        result["tender"]["crossBorderLaw"] == "Directive XYZ on Cross Border ..."
    ), "Unexpected crossBorderLaw value"


def test_bt_09_procedure_integration_missing(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingTerms>
        </cac:TenderingTerms>
    </root>
    """
    xml_file = tmp_path / "test_input_cross_border_law_missing.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" not in result or "crossBorderLaw" not in result.get(
        "tender",
        {},
    ), "Unexpected 'crossBorderLaw' in result when missing in input"


if __name__ == "__main__":
    pytest.main()
