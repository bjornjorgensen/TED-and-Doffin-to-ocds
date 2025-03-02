import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main
from src.ted_and_doffin_to_ocds.converters.eforms.bt_26a_procedure import (
    merge_classification_type_procedure,
    parse_classification_type_procedure,
)


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


@pytest.fixture
def sample_xml():
    return """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProject>
            <cac:AdditionalCommodityClassification>
                <cbc:ItemClassificationCode listName="cpv">15311200</cbc:ItemClassificationCode>
            </cac:AdditionalCommodityClassification>
            <cac:AdditionalCommodityClassification>
                <cbc:ItemClassificationCode listName="cpv">15311300</cbc:ItemClassificationCode>
            </cac:AdditionalCommodityClassification>
        </cac:ProcurementProject>
    </ContractAwardNotice>
    """


def run_main_and_get_result(xml_file, output_dir):
    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    output_files = list(output_dir.glob("*.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_parse_classification_type_procedure(sample_xml):
    result = parse_classification_type_procedure(sample_xml)

    assert result is not None
    assert len(result["tender"]["items"]) == 1
    item = result["tender"]["items"][0]
    assert item["id"] == "1"
    assert len(item["additionalClassifications"]) == 2
    assert all("scheme" in c and "id" in c for c in item["additionalClassifications"])
    assert all(c["scheme"] == "CPV" for c in item["additionalClassifications"])
    
    # Verify the actual classification code values
    codes = {c["id"] for c in item["additionalClassifications"]}
    assert codes == {"15311200", "15311300"}, f"Expected codes 15311200 and 15311300, got {codes}"


def test_parse_classification_type_procedure_no_scheme():
    xml_no_scheme = """
    <ContractAwardNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProject>
            <cac:AdditionalCommodityClassification>
                <cbc:ItemClassificationCode>15311200</cbc:ItemClassificationCode>
            </cac:AdditionalCommodityClassification>
        </cac:ProcurementProject>
    </ContractAwardNotice>
    """
    result = parse_classification_type_procedure(xml_no_scheme)
    assert result is None


def test_merge_classification_type_procedure():
    release_json = {
        "tender": {
            "items": [
                {
                    "id": "1",
                    "additionalClassifications": [{"scheme": "EXISTING", "id": "123"}],
                }
            ]
        }
    }

    classification_data = {
        "tender": {
            "items": [
                {
                    "id": "1",
                    "additionalClassifications": [{"scheme": "CPV", "id": "15311200"}],
                }
            ]
        }
    }

    merge_classification_type_procedure(release_json, classification_data)

    item = release_json["tender"]["items"][0]
    assert len(item["additionalClassifications"]) == 2
    schemes = {c["scheme"] for c in item["additionalClassifications"]}
    ids = {c["id"] for c in item["additionalClassifications"]}
    assert "EXISTING" in schemes
    assert "CPV" in schemes
    assert ids == {"123", "15311200"}, f"Unexpected ids: {ids}"


def test_bt_26a_procedure_integration(tmp_path) -> None:
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProject>
            <cac:AdditionalCommodityClassification>
                <cbc:ItemClassificationCode listName="cpv">15311200</cbc:ItemClassificationCode>
            </cac:AdditionalCommodityClassification>
        </cac:ProcurementProject>
    </ContractAwardNotice>
    """
    xml_file = tmp_path / "test_input_classification_type_procedure.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), str(tmp_path), "ocds-test-prefix", "test-scheme")
    output_files = list(tmp_path.glob("*.json"))
    assert len(output_files) == 1

    with output_files[0].open() as f:
        result = json.load(f)

    assert "tender" in result
    assert "items" in result["tender"]
    assert len(result["tender"]["items"]) == 1

    item = result["tender"]["items"][0]
    assert item["id"] == "1"

    classifications = item["additionalClassifications"]
    assert any(c["scheme"] == "CPV" for c in classifications)
    assert all("scheme" in c and "id" in c for c in classifications)
    
    # Verify that the correct code value is present
    codes = [c["id"] for c in classifications if c["scheme"] == "CPV"]
    assert "15311200" in codes, f"Expected code 15311200 in {codes}"


if __name__ == "__main__":
    pytest.main(["-v"])
