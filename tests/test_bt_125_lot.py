# tests/test_bt_125_Lot.py
from pathlib import Path
import pytest
import json
import sys

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_125_lot_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingProcess>
                <cac:noticeDocumentReference>
                    <cbc:ID>9c0fd704-64d3-4294-a3b6-6df45911ab9f-01</cbc:ID>
                    <cbc:ReferencedDocumentInternalAddress>123</cbc:ReferencedDocumentInternalAddress>
                </cac:noticeDocumentReference>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_previous_planning_lot.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "relatedProcesses" in result
    assert len(result["relatedProcesses"]) == 1
    related_process = result["relatedProcesses"][0]
    assert related_process["id"] == "1"
    assert related_process["relationship"] == ["planning"]
    assert related_process["scheme"] == "eu-oj"
    assert related_process["identifier"] == "9c0fd704-64d3-4294-a3b6-6df45911ab9f-01"
    assert related_process["relatedLots"] == ["123"]


if __name__ == "__main__":
    pytest.main()