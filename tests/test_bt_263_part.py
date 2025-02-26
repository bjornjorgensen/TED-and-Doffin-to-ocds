import json
import sys
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main
from src.ted_and_doffin_to_ocds.converters.eforms.bt_263_part import (
    merge_additional_classification_code_part,
    parse_additional_classification_code_part,
)

@pytest.fixture
def temp_output_dir(tmp_path):
    return tmp_path

@pytest.fixture
def sample_xml():
    return """
    <ContractNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProject>
            <cac:AdditionalCommodityClassification>
                <cbc:ItemClassificationCode>15311200</cbc:ItemClassificationCode>
            </cac:AdditionalCommodityClassification>
            <cac:AdditionalCommodityClassification>
                <cbc:ItemClassificationCode>15311300</cbc:ItemClassificationCode>
            </cac:AdditionalCommodityClassification>
        </cac:ProcurementProject>
    </ContractNotice>
    """

def test_parse_additional_classification_code(sample_xml):
    result = parse_additional_classification_code(sample_xml)
    assert result is not None
    assert "tender" in result
    assert "items" in result["tender"]
    assert len(result["tender"]["items"]) == 1
    item = result["tender"]["items"][0]
    assert "additionalClassifications" in item
    classifications = item["additionalClassifications"]
    assert len(classifications) == 2
    for classification in classifications:
        assert "id" in classification
        assert "scheme" in classification

def test_parse_additional_classification_code_no_data():
    xml_content = """
    <ContractNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProject>
            <!-- No AdditionalCommodityClassification -->
        </cac:ProcurementProject>
    </ContractNotice>
    """
    result = parse_additional_classification_code(xml_content)
    assert result is None

def test_merge_additional_classification_code():
    release_json = {
        "tender": {
            "items": [
                {
                    "id": "1",
                    "additionalClassifications": [{"scheme": "CPV", "id": "15311200"}],
                }
            ]
        }
    }
    additional_classification_data = {
        "tender": {
            "items": [
                {
                    "id": "1",
                    "additionalClassifications": [{"scheme": "CPV", "id": "15311300"}],
                }
            ]
        }
    }
    merge_additional_classification_code(release_json, additional_classification_data)
    classifications = release_json["tender"]["items"][0]["additionalClassifications"]
    assert len(classifications) == 2
    ids = {c["id"] for c in classifications}
    assert ids == {"15311200", "15311300"}

def test_merge_additional_classification_code_none_data():
    release_json = {
        "tender": {
            "items": [
                {
                    "id": "1",
                    "additionalClassifications": [{"scheme": "CPV", "id": "15311200"}],
                }
            ]
        }
    }
    merge_additional_classification_code(release_json, None)
    assert len(release_json["tender"]["items"]) == 1
    classifications = release_json["tender"]["items"][0]["additionalClassifications"]
    assert len(classifications) == 1
    assert classifications[0]["id"] == "15311200"

def test_bt_263_part_integration(tmp_path, temp_output_dir):
    xml_content = """
    <ContractNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProject>
            <cac:AdditionalCommodityClassification>
                <cbc:ItemClassificationCode>15311200</cbc:ItemClassificationCode>
            </cac:AdditionalCommodityClassification>
            <cac:AdditionalCommodityClassification>
                <cbc:ItemClassificationCode>15311300</cbc:ItemClassificationCode>
            </cac:AdditionalCommodityClassification>
        </cac:ProcurementProject>
    </ContractNotice>
    """

    xml_file = tmp_path / "test_input.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), str(temp_output_dir), "ocds-test-prefix", "test-scheme")
    output_files = list(temp_output_dir.glob("*.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"

    with output_files[0].open() as f:
        result = json.load(f)

    assert "tender" in result
    assert "items" in result["tender"]
    assert len(result["tender"]["items"]) == 1
    item = result["tender"]["items"][0]
    assert "additionalClassifications" in item
    classifications = item["additionalClassifications"]
    assert len(classifications) == 2
    for classification in classifications:
        assert "id" in classification
        assert classification["scheme"] == "CPV"
        assert classification["id"] in {"15311200", "15311300"}

if __name__ == "__main__":
    pytest.main(["-v", "-s"])
