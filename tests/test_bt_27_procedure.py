# tests/test_bt_27_procedure.py
from pathlib import Path
import pytest
import sys

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_27_procedure_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProject>
            <cac:RequestedTenderTotal>
                <cbc:EstimatedOverallContractAmount currencyID="EUR">250000</cbc:EstimatedOverallContractAmount>
            </cac:RequestedTenderTotal>
        </cac:ProcurementProject>
    </root>
    """
    xml_file = tmp_path / "test_input_bt_27_procedure.xml"
    xml_file.write_text(xml_content)

    result = main(str(xml_file), "ocds-test-prefix")

    assert "tender" in result, "tender not found in result"
    assert "value" in result["tender"], "value not found in tender"
    assert (
        result["tender"]["value"]["amount"] == 250000
    ), f"Expected amount 250000, got {result['tender']['value']['amount']}"
    assert (
        result["tender"]["value"]["currency"] == "EUR"
    ), f"Expected currency 'EUR', got {result['tender']['value']['currency']}"


if __name__ == "__main__":
    pytest.main()