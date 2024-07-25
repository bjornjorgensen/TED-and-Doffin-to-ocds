# tests/test_BT_5071_Part.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_5071_part_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:RealizedLocation>
                    <cac:Address>
                        <cbc:CountrySubentityCode listName="nuts=lvl3">UKG23</cbc:CountrySubentityCode>
                    </cac:Address>
                </cac:RealizedLocation>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_part_place_performance.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "deliveryAddresses" in result["tender"], "Expected 'deliveryAddresses' in tender"
    assert len(result["tender"]["deliveryAddresses"]) >= 1, f"Expected at least 1 delivery address, got {len(result['tender']['deliveryAddresses'])}"

    address = next((addr for addr in result["tender"]["deliveryAddresses"] if addr.get("region") == "UKG23"), None)
    assert address is not None, "Expected to find an address with region 'UKG23'"
    assert address["region"] == "UKG23", f"Expected region 'UKG23', got {address['region']}"

if __name__ == "__main__":
    pytest.main()