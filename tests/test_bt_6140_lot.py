# tests/test_bt_6140_Lot.py
from pathlib import Path
import pytest
import json
import sys

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_6140_lot_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
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
    </root>
    """
    xml_file = tmp_path / "test_input_lot_eu_funds_details.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

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
    pytest.main()
