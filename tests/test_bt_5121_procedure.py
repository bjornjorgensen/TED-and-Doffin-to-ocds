# tests/test_bt_5121_procedure.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_5121_procedure_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProject>
            <cac:RealizedLocation>
                <cac:Address>
                    <cbc:PostalZone>XY14 2LG</cbc:PostalZone>
                </cac:Address>
            </cac:RealizedLocation>
        </cac:ProcurementProject>
    </root>
    """
    xml_file = tmp_path / "test_input_bt_5121_procedure.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert (
        "deliveryAddresses" in result["tender"]
    ), "Expected 'deliveryAddresses' in tender"
    assert (
        len(result["tender"]["deliveryAddresses"]) == 1
    ), f"Expected 1 delivery address, got {len(result['tender']['deliveryAddresses'])}"

    address = result["tender"]["deliveryAddresses"][0]
    assert "postalCode" in address, "Expected 'postalCode' in delivery address"
    expected_postal_code = "XY14 2LG"
    assert (
        address["postalCode"] == expected_postal_code
    ), f"Expected postal code '{expected_postal_code}', got {address['postalCode']}"


if __name__ == "__main__":
    pytest.main()
