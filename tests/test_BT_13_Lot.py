# tests/test_BT_13_Lot.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_13_lot_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingProcess>
                <cac:AdditionalInformationRequestPeriod>
                    <cbc:EndDate>2019-11-08+01:00</cbc:EndDate>
                    <cbc:EndTime>18:00:00+01:00</cbc:EndTime>
                </cac:AdditionalInformationRequestPeriod>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_additional_information_deadline.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001"
    assert "enquiryPeriod" in lot
    assert "endDate" in lot["enquiryPeriod"]
    assert lot["enquiryPeriod"]["endDate"] == "2019-11-08T18:00:00+01:00"


if __name__ == "__main__":
    pytest.main()
