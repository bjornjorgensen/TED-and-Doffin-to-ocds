from pathlib import Path
import pytest
import sys
import tempfile
import json

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


def run_main_and_get_result(xml_file, output_dir):
    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    output_files = list(output_dir.glob("*.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_26m_procedure_integration(tmp_path, temp_output_dir):
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
                         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
                         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProject>
            <cac:MainCommodityClassification>
                <cbc:ItemClassificationCode listName="cpv">15311100</cbc:ItemClassificationCode>
            </cac:MainCommodityClassification>
        </cac:ProcurementProject>
    </ContractAwardNotice>
    """

    xml_file = tmp_path / "test_input_main_classification_type_procedure.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    assert "tender" in result
    assert "items" in result["tender"]
    assert len(result["tender"]["items"]) == 1

    item = result["tender"]["items"][0]
    assert item["id"] == "1"
    assert "classification" in item
    assert item["classification"]["scheme"] == "CPV"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
