# tests/test_bt_720_Tender.py
from pathlib import Path
import pytest
import sys

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_720_tender_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <efac:LotResult>
            <cbc:ID schemeName="result">RES-0001</cbc:ID>
            <efac:LotTender>
                <cbc:ID schemeName="tender">TEN-0001</cbc:ID>
            </efac:LotTender>
            <efac:TenderLot>
                <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            </efac:TenderLot>
        </efac:LotResult>
        <efac:LotTender>
            <cbc:ID schemeName="tender">TEN-0001</cbc:ID>
            <cac:LegalMonetaryTotal>
                <cbc:PayableAmount currencyID="EUR">500</cbc:PayableAmount>
            </cac:LegalMonetaryTotal>
            <efac:TenderLot>
                <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            </efac:TenderLot>
        </efac:LotTender>
    </root>
    """
    xml_file = tmp_path / "test_input_tender_value.xml"
    xml_file.write_text(xml_content)

    result = main(str(xml_file), "ocds-test-prefix")

    assert result is not None, "Result is None"

    assert "bids" in result, "No 'bids' in result"
    assert "details" in result["bids"], "No 'details' in result['bids']"
    assert (
        len(result["bids"]["details"]) == 1
    ), f"Expected 1 bid, got {len(result['bids']['details'])}"

    bid = result["bids"]["details"][0]

    assert bid["id"] == "TEN-0001", f"Expected bid id 'TEN-0001', got '{bid.get('id')}'"

    assert "value" in bid, f"No 'value' in bid. Bid keys: {list(bid.keys())}"
    assert (
        "amount" in bid["value"]
    ), f"No 'amount' in bid['value']. Value keys: {list(bid['value'].keys())}"
    assert (
        bid["value"]["amount"] == 500
    ), f"Expected amount 500, got {bid['value'].get('amount')}"
    assert (
        bid["value"]["currency"] == "EUR"
    ), f"Expected currency 'EUR', got '{bid['value'].get('currency')}'"

    assert "awards" in result, "No 'awards' in result"
    assert len(result["awards"]) == 1, f"Expected 1 award, got {len(result['awards'])}"

    award = result["awards"][0]

    assert (
        award["id"] == "RES-0001"
    ), f"Expected award id 'RES-0001', got '{award.get('id')}'"
    assert "value" in award, f"No 'value' in award. Award keys: {list(award.keys())}"
    assert (
        "amount" in award["value"]
    ), f"No 'amount' in award['value']. Value keys: {list(award['value'].keys())}"
    assert (
        award["value"]["amount"] == 500
    ), f"Expected amount 500, got {award['value'].get('amount')}"
    assert (
        award["value"]["currency"] == "EUR"
    ), f"Expected currency 'EUR', got '{award['value'].get('currency')}'"
    assert award["relatedLots"] == [
        "LOT-0001",
    ], f"Expected relatedLots ['LOT-0001'], got {award.get('relatedLots')}"


if __name__ == "__main__":
    pytest.main()