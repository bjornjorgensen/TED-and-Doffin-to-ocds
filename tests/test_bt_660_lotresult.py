# tests/test_bt_660_LotResult.py
from pathlib import Path
import pytest
import json
import sys

sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_660_lotresult_integration(tmp_path):
    xml_content = """
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <efac:noticeResult>
            <efac:LotResult>
                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                <efac:FrameworkAgreementValues>
                    <efbc:ReestimatedValueAmount currencyID="EUR">123</efbc:ReestimatedValueAmount>
                </efac:FrameworkAgreementValues>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                </efac:TenderLot>
            </efac:LotResult>
        </efac:noticeResult>
    </root>
    """
    xml_file = tmp_path / "test_input_framework_reestimated_value.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "awards" in result
    assert len(result["awards"]) == 1
    award = result["awards"][0]
    assert award["id"] == "RES-0001"
    assert "estimatedValue" in award
    assert award["estimatedValue"]["amount"] == 123
    assert award["estimatedValue"]["currency"] == "EUR"
    assert "relatedLots" in award
    assert award["relatedLots"] == ["LOT-0001"]


if __name__ == "__main__":
    pytest.main()