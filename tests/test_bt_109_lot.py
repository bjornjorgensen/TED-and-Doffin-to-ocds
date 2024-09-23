# tests/test_bt_109_Lot.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_109_lot_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingProcess>
                <cac:FrameworkAgreement>
                    <cbc:Justification languageID="ENG">The exceptional duration of ...</cbc:Justification>
                </cac:FrameworkAgreement>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:TenderingProcess>
                <cac:FrameworkAgreement>
                    <cbc:Justification languageID="ENG">Another exceptional duration...</cbc:Justification>
                </cac:FrameworkAgreement>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_framework_duration_justification.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in result['tender']"
    assert (
        len(result["tender"]["lots"]) == 2
    ), f"Expected 2 lots, got {len(result['tender']['lots'])}"

    lot_1 = next(lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0001")
    assert "techniques" in lot_1, "Expected 'techniques' in LOT-0001"
    assert (
        "frameworkAgreement" in lot_1["techniques"]
    ), "Expected 'frameworkAgreement' in LOT-0001 techniques"
    assert (
        lot_1["techniques"]["frameworkAgreement"]["periodRationale"]
        == "The exceptional duration of ..."
    ), "Unexpected periodRationale for LOT-0001"

    lot_2 = next(lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0002")
    assert "techniques" in lot_2, "Expected 'techniques' in LOT-0002"
    assert (
        "frameworkAgreement" in lot_2["techniques"]
    ), "Expected 'frameworkAgreement' in LOT-0002 techniques"
    assert (
        lot_2["techniques"]["frameworkAgreement"]["periodRationale"]
        == "Another exceptional duration..."
    ), "Unexpected periodRationale for LOT-0002"


if __name__ == "__main__":
    pytest.main()
