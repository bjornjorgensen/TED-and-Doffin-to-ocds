# tests/test_bt_125_part.py
from pathlib import Path
import pytest
import json
import sys
import logging

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


@pytest.mark.parametrize("caplog", [True], indirect=True)
def test_bt_125_part_integration(tmp_path, caplog):
    caplog.set_level(logging.INFO)

    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="part">PART-0001</cbc:ID>
            <cac:TenderingProcess>
                <cac:noticeDocumentReference>
                    <cbc:ID schemeName="notice-id-ref">123e4567-e89b-12d3-a456-426614174000-06</cbc:ID>
                    <cbc:ReferencedDocumentInternalAddress>PAR-0001</cbc:ReferencedDocumentInternalAddress>
                </cac:noticeDocumentReference>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_previous_planning_part.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    for _record in caplog.records:
        pass

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "relatedProcesses" in result
    assert len(result["relatedProcesses"]) == 1
    related_process = result["relatedProcesses"][0]
    assert related_process["id"] == "1"
    assert related_process["relationship"] == ["planning"]
    assert related_process["scheme"] == "eu-oj"
    assert (
        related_process["identifier"]
        == "123e4567-e89b-12d3-a456-426614174000-06-PAR-0001"
    )


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
