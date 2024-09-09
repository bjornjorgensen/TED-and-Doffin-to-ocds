# tests/test_OPP_090_Procedure.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main


def test_opp_090_procedure_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingProcess>
            <cac:NoticeDocumentReference>
                <cbc:ID schemeName="notice-id-ref">123e4567-e89b-12d3-a456-426614174000-06</cbc:ID>
            </cac:NoticeDocumentReference>
        </cac:TenderingProcess>
        <cac:TenderingProcess>
            <cac:NoticeDocumentReference>
                <cbc:ID schemeName="notice-id-ref">987e6543-e21b-12d3-a456-426614174000-07</cbc:ID>
            </cac:NoticeDocumentReference>
        </cac:TenderingProcess>
    </root>
    """
    xml_file = tmp_path / "test_input_previous_notice_identifier.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "relatedProcesses" in result
    assert len(result["relatedProcesses"]) == 2

    related_process_1 = result["relatedProcesses"][0]
    assert related_process_1["id"] == "1"
    assert related_process_1["relationship"] == ["planning"]
    assert related_process_1["scheme"] == "eu-oj"
    assert related_process_1["identifier"] == "123e4567-e89b-12d3-a456-426614174000-06"

    related_process_2 = result["relatedProcesses"][1]
    assert related_process_2["id"] == "2"
    assert related_process_2["relationship"] == ["planning"]
    assert related_process_2["scheme"] == "eu-oj"
    assert related_process_2["identifier"] == "987e6543-e21b-12d3-a456-426614174000-07"


if __name__ == "__main__":
    pytest.main()
