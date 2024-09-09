# tests/test_BT_115_GPA_Coverage.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main


def test_bt_115_gpa_coverage_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingProcess>
                <cbc:GovernmentAgreementConstraintIndicator>true</cbc:GovernmentAgreementConstraintIndicator>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:TenderingProcess>
                <cbc:GovernmentAgreementConstraintIndicator>false</cbc:GovernmentAgreementConstraintIndicator>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:TenderingProcess>
                <cbc:GovernmentAgreementConstraintIndicator>true</cbc:GovernmentAgreementConstraintIndicator>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_gpa_coverage.xml"
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
    assert "coveredBy" in lot_1, "Expected 'coveredBy' in LOT-0001"
    assert "GPA" in lot_1["coveredBy"], "Expected 'GPA' in LOT-0001 coveredBy"

    lot_2 = next(lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0002")
    assert "coveredBy" not in lot_2, "Unexpected 'coveredBy' in LOT-0002"

    assert "coveredBy" in result["tender"], "Expected 'coveredBy' in tender"
    assert "GPA" in result["tender"]["coveredBy"], "Expected 'GPA' in tender coveredBy"


if __name__ == "__main__":
    pytest.main()
