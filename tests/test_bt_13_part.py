# tests/test_bt_13_part.py

from pathlib import Path
import pytest
import json
import sys

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_13_part_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="part">PART-0001</cbc:ID>
            <cac:TenderingProcess>
                <cac:AdditionalInformationRequestPeriod>
                    <cbc:EndDate>2019-11-08+01:00</cbc:EndDate>
                    <cbc:EndTime>18:00:00+01:00</cbc:EndTime>
                </cac:AdditionalInformationRequestPeriod>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_additional_information_deadline_part.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "tender" in result
    assert "enquiryPeriod" in result["tender"]
    assert "endDate" in result["tender"]["enquiryPeriod"]
    assert result["tender"]["enquiryPeriod"]["endDate"] == "2019-11-08T18:00:00+01:00"


if __name__ == "__main__":
    pytest.main()