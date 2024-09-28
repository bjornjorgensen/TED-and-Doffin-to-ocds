# tests/test_bt_5101b_procedure.py
from pathlib import Path
import pytest
import json
import sys

sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_5101b_procedure_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProject>
            <cac:RealizedLocation>
                <cac:Address>
                    <cbc:StreetName>Main Street</cbc:StreetName>
                    <cbc:AdditionalStreetName>Building B1</cbc:AdditionalStreetName>
                    <cac:AddressLine>
                        <cbc:Line>3rd floor</cbc:Line>
                    </cac:AddressLine>
                </cac:Address>
            </cac:RealizedLocation>
        </cac:ProcurementProject>
    </root>
    """
    xml_file = tmp_path / "test_input_procedure_place_performance_streetline1.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "tender" in result
    assert "deliveryAddresses" in result["tender"]
    assert len(result["tender"]["deliveryAddresses"]) == 1
    address = result["tender"]["deliveryAddresses"][0]
    assert "streetAddress" in address
    assert address["streetAddress"] == "Main Street, Building B1, 3rd floor"


if __name__ == "__main__":
    pytest.main()
