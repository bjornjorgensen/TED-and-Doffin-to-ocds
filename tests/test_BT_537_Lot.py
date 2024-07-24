# tests/test_BT_537_Lot.py

import pytest
from lxml import etree
from converters.BT_537_Lot import parse_lot_duration_end_date, merge_lot_duration_end_date

def test_parse_lot_duration_end_date():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:PlannedPeriod>
                    <cbc:EndDate>2019-11-19+01:00</cbc:EndDate>
                </cac:PlannedPeriod>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    
    result = parse_lot_duration_end_date(xml_content)
    
    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert result["tender"]["lots"][0]["contractPeriod"]["endDate"] == "2019-11-19T23:59:59+01:00"

def test_merge_lot_duration_end_date():
    release_json = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "title": "Existing Lot"
                }
            ]
        }
    }
    
    lot_duration_end_date_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "contractPeriod": {
                        "endDate": "2019-11-19T23:59:59+01:00"
                    }
                }
            ]
        }
    }
    
    merge_lot_duration_end_date(release_json, lot_duration_end_date_data)
    
    assert "contractPeriod" in release_json["tender"]["lots"][0]
    assert release_json["tender"]["lots"][0]["contractPeriod"]["endDate"] == "2019-11-19T23:59:59+01:00"

if __name__ == "__main__":
    pytest.main()