# tests/test_bt_263_procedure.py

import json
import logging
import sys
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import configure_logging, main
from src.ted_and_doffin_to_ocds.converters.eforms.bt_263_procedure import (
    merge_additional_classification_code_procedure,
    parse_additional_classification_code_procedure,
)

logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def setup_logging():
    # Logging disabled for tests
    logger = logging.getLogger(__name__)
    logger.disabled = True
    return logger


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
                <cbc:ItemClassificationCode listName="CPV">15311200</cbc:ItemClassificationCode>
            </cac:AdditionalCommodityClassification>
            <cac:AdditionalCommodityClassification>
                <cbc:ItemClassificationCode>15311300</cbc:ItemClassificationCode>
            </cac:AdditionalCommodityClassification>
        </cac:ProcurementProject>
    </ContractNotice>
    """


def test_parse_additional_classification_code_procedure(sample_xml):
    result = parse_additional_classification_code_procedure(sample_xml)

    assert result is not None
    assert len(result["tender"]["items"]) == 1
    item = result["tender"]["items"][0]
    assert item["id"] == "1"
    assert len(item["additionalClassifications"]) == 2
    
    # Test both with and without scheme
    classification_with_scheme = next(
        (c for c in item["additionalClassifications"] if c.get("id") == "15311200"),
        None
    )
    classification_without_scheme = next(
        (c for c in item["additionalClassifications"] if c.get("id") == "15311300"),
        None
    )
    
    assert classification_with_scheme is not None
    assert classification_without_scheme is not None
    assert classification_with_scheme.get("scheme") == "CPV"
    assert "scheme" not in classification_without_scheme


def test_parse_additional_classification_code_procedure_no_data():
    xml_no_classifications = """
    <ContractNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProject/>
    </ContractNotice>
    """
    result = parse_additional_classification_code_procedure(xml_no_classifications)
    assert result is None


def test_merge_additional_classification_code_procedure():
    release_json = {
        "tender": {
            "items": [
                {
                    "id": "1",
                    "additionalClassifications": [{"scheme": "CPV", "id": "existing"}],
                }
            ]
        }
    }

    additional_data = {
        "tender": {"items": [{"id": "1", "additionalClassifications": [
            {"id": "new1"},
            {"id": "new2", "scheme": "UNSPSC"}
        ]}]}
    }

    merge_additional_classification_code_procedure(release_json, additional_data)

    assert len(release_json["tender"]["items"]) == 1
    item = release_json["tender"]["items"][0]
    assert len(item["additionalClassifications"]) == 3
    
    # Check that all IDs are present
    classification_ids = [c.get("id") for c in item["additionalClassifications"]]
    assert "existing" in classification_ids
    assert "new1" in classification_ids
    assert "new2" in classification_ids
    
    # Check that schemes are preserved
    cpv_classifications = [c for c in item["additionalClassifications"] 
                           if c.get("scheme") == "CPV"]
    unspsc_classifications = [c for c in item["additionalClassifications"] 
                              if c.get("scheme") == "UNSPSC"]
    
    assert len(cpv_classifications) == 1
    assert len(unspsc_classifications) == 1
    assert cpv_classifications[0]["id"] == "existing"
    assert unspsc_classifications[0]["id"] == "new2"


def test_bt_263_procedure_integration(tmp_path) -> None:
    xml_content = """
    <ContractNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProject>
            <cac:AdditionalCommodityClassification>
                <cbc:ItemClassificationCode listName="cpv">15311200</cbc:ItemClassificationCode>
            </cac:AdditionalCommodityClassification>
            <cac:AdditionalCommodityClassification>
                <cbc:ItemClassificationCode listName="cpv">15311300</cbc:ItemClassificationCode>
            </cac:AdditionalCommodityClassification>
        </cac:ProcurementProject>
    </ContractNotice>
    """
    xml_file = tmp_path / "test_input_additional_classification_code_procedure.xml"
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
    assert "additionalClassifications" in item

    classifications = item["additionalClassifications"]
    cpv_classifications = [c for c in classifications if c.get("scheme") == "CPV"]
    id_classifications = [c for c in classifications if "id" in c]

    assert len(cpv_classifications) == 2
    assert len(id_classifications) == 2

    classification_ids = {c["id"] for c in id_classifications}
    assert "15311200" in classification_ids
    assert "15311300" in classification_ids


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
