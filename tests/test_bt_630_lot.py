# tests/test_bt_630_Lot.py
from pathlib import Path
import pytest
from ted_and_doffin_to_ocds.converters.bt_630_lot import (
    parse_deadline_receipt_expressions,
    merge_deadline_receipt_expressions,
)
import json
import sys

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_parse_deadline_receipt_expressions():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingProcess>
                <ext:UBLExtensions>
                    <ext:UBLExtension>
                        <ext:ExtensionContent>
                            <efext:EformsExtension>
                                <efac:InterestExpressionReceptionPeriod>
                                    <cbc:EndDate>2019-10-28+01:00</cbc:EndDate>
                                    <cbc:EndTime>18:00:00+01:00</cbc:EndTime>
                                </efac:InterestExpressionReceptionPeriod>
                            </efext:EformsExtension>
                        </ext:ExtensionContent>
                    </ext:UBLExtension>
                </ext:UBLExtensions>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_deadline_receipt_expressions(xml_content)

    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert (
        result["tender"]["lots"][0]["tenderPeriod"]["endDate"]
        == "2019-10-28T18:00:00+01:00"
    )


def test_merge_deadline_receipt_expressions():
    release_json = {"tender": {"lots": [{"id": "LOT-0001", "title": "Existing Lot"}]}}

    deadline_receipt_expressions_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "tenderPeriod": {"endDate": "2019-10-28T18:00:00+01:00"},
                },
            ],
        },
    }

    merge_deadline_receipt_expressions(release_json, deadline_receipt_expressions_data)

    assert "tenderPeriod" in release_json["tender"]["lots"][0]
    assert (
        release_json["tender"]["lots"][0]["tenderPeriod"]["endDate"]
        == "2019-10-28T18:00:00+01:00"
    )


def test_bt_630_lot_deadline_receipt_expressions_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingProcess>
                <ext:UBLExtensions>
                    <ext:UBLExtension>
                        <ext:ExtensionContent>
                            <efext:EformsExtension>
                                <efac:InterestExpressionReceptionPeriod>
                                    <cbc:EndDate>2019-10-28+01:00</cbc:EndDate>
                                    <cbc:EndTime>18:00:00+01:00</cbc:EndTime>
                                </efac:InterestExpressionReceptionPeriod>
                            </efext:EformsExtension>
                        </ext:ExtensionContent>
                    </ext:UBLExtension>
                </ext:UBLExtensions>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_deadline_receipt_expressions.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert "tenderPeriod" in result["tender"]["lots"][0]
    assert (
        result["tender"]["lots"][0]["tenderPeriod"]["endDate"]
        == "2019-10-28T18:00:00+01:00"
    )


if __name__ == "__main__":
    pytest.main()