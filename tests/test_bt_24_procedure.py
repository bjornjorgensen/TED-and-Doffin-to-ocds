# tests/test_bt_24_procedure.py
from pathlib import Path
import pytest
import json
import sys

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_24_procedure_description_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProject>
            <cbc:Description languageID="ENG">procedure for the procurement of office furniture</cbc:Description>
        </cac:ProcurementProject>
    </root>
    """
    xml_file = tmp_path / "test_input_procedure_description.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "description" in result["tender"], "Expected 'description' in tender"
    expected_description = "procedure for the procurement of office furniture"
    assert (
        result["tender"]["description"] == expected_description
    ), f"Expected description '{expected_description}', got {result['tender']['description']}"


if __name__ == "__main__":
    pytest.main()
