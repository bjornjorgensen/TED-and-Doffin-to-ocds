# tests/test_bt_6140_lot.py
import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


def run_main_and_get_result(xml_file, output_dir):
    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    output_files = list(output_dir.glob("*_release_0.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_6140_lot_integration(tmp_path, temp_output_dir) -> None:
    xml_content = """
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
          xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <ext:UBLExtensions>
                    <ext:UBLExtension>
                        <ext:ExtensionContent>
                            <efext:EformsExtension>
                                <efac:Funding>
                                    <cbc:Description languageID="ENG">This project will be financed ...</cbc:Description>
                                </efac:Funding>
                            </efext:EformsExtension>
                        </ext:ExtensionContent>
                    </ext:UBLExtension>
                </ext:UBLExtensions>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """
    xml_file = tmp_path / "test_input_lot_eu_funds_details.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    assert "planning" in result, "Expected 'planning' in result"
    assert "budget" in result["planning"], "Expected 'budget' in planning"
    assert "finance" in result["planning"]["budget"], "Expected 'finance' in budget"
    assert (
        len(result["planning"]["budget"]["finance"]) == 1
    ), f"Expected 1 finance entry, got {len(result['planning']['budget']['finance'])}"

    finance = result["planning"]["budget"]["finance"][0]
    assert finance["id"] == "1", f"Expected finance id '1', got {finance['id']}"
    assert (
        finance["description"] == "This project will be financed ..."
    ), f"Expected description 'This project will be financed ...', got {finance['description']}"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
