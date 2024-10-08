# tests/test_opt_310_tender.py

from pathlib import Path
import pytest
import json
import sys
import tempfile

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


def test_opt_310_tender_integration(tmp_path, temp_output_dir):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1">
        <efac:NoticeResult>
            <efac:LotTender>
                <cbc:ID schemeName="tender">TEN-0001</cbc:ID>
                <efac:TenderingParty>
                    <cbc:ID schemeName="tendering-party">TPA-0001</cbc:ID>
                </efac:TenderingParty>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                </efac:TenderLot>
            </efac:LotTender>
            <efac:TenderingParty>
                <cbc:ID schemeName="tendering-party">TPA-0001</cbc:ID>
                <efac:Tenderer>
                    <cbc:ID schemeName="organization">ORG-0001</cbc:ID>
                </efac:Tenderer>
            </efac:TenderingParty>
        </efac:NoticeResult>
    </root>
    """
    xml_file = tmp_path / "test_input_tendering_party_id_reference.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    assert "parties" in result
    assert len(result["parties"]) == 1
    assert result["parties"][0] == {"id": "ORG-0001", "roles": ["tenderer"]}

    assert "bids" in result
    assert "details" in result["bids"]
    assert len(result["bids"]["details"]) == 1
    assert result["bids"]["details"][0] == {
        "id": "TEN-0001",
        "tenderers": [{"id": "ORG-0001"}],
        "relatedLots": ["LOT-0001"],
    }


if __name__ == "__main__":
    pytest.main()
