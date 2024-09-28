# tests/test_bt_537_part.py
from pathlib import Path
import pytest
import json
import sys

# Add the project root directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from src.ted_and_doffin_to_ocds.main import main


def test_bt_537_part_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="part">PART-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:PlannedPeriod>
                    <cbc:EndDate>2019-11-19+01:00</cbc:EndDate>
                </cac:PlannedPeriod>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_duration_end_date_part.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "contractPeriod" in result["tender"], "Expected 'contractPeriod' in tender"
    assert (
        "endDate" in result["tender"]["contractPeriod"]
    ), "Expected 'endDate' in tender contractPeriod"
    expected_date = "2019-11-19T23:59:59+01:00"
    assert (
        result["tender"]["contractPeriod"]["endDate"] == expected_date
    ), f"Expected end date '{expected_date}', got {result['tender']['contractPeriod']['endDate']}"


if __name__ == "__main__":
    pytest.main()
