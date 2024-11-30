# tests/test_bt_23_procedure.py
import sys
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import the converter
sys.path.append(str(Path(__file__).parent.parent))
from ted_and_doffin_to_ocds.converters.bt_23_procedure import (
    merge_main_nature_procedure,
    parse_main_nature_procedure,
)


def test_parse_main_nature_procedure_works() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProject>
            <cbc:ProcurementTypeCode listName="contract-nature">works</cbc:ProcurementTypeCode>
        </cac:ProcurementProject>
    </root>
    """
    result = parse_main_nature_procedure(xml_content)
    assert result == {"tender": {"mainProcurementCategory": "works"}}


def test_parse_main_nature_procedure_services() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProject>
            <cbc:ProcurementTypeCode listName="contract-nature">services</cbc:ProcurementTypeCode>
        </cac:ProcurementProject>
    </root>
    """
    result = parse_main_nature_procedure(xml_content)
    assert result == {"tender": {"mainProcurementCategory": "services"}}


def test_parse_main_nature_procedure_supplies() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProject>
            <cbc:ProcurementTypeCode listName="contract-nature">supplies</cbc:ProcurementTypeCode>
        </cac:ProcurementProject>
    </root>
    """
    result = parse_main_nature_procedure(xml_content)
    assert result == {"tender": {"mainProcurementCategory": "goods"}}


def test_parse_main_nature_procedure_unexpected() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProject>
            <cbc:ProcurementTypeCode listName="contract-nature">unexpected</cbc:ProcurementTypeCode>
        </cac:ProcurementProject>
    </root>
    """
    result = parse_main_nature_procedure(xml_content)
    assert result is None


def test_parse_main_nature_procedure_no_data() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    </root>
    """
    result = parse_main_nature_procedure(xml_content)
    assert result is None


def test_merge_main_nature_procedure() -> None:
    release_json = {"tender": {"id": "tender-001"}}
    main_nature_data = {"tender": {"mainProcurementCategory": "works"}}
    merge_main_nature_procedure(release_json, main_nature_data)
    assert release_json == {
        "tender": {"id": "tender-001", "mainProcurementCategory": "works"},
    }


def test_merge_main_nature_procedure_no_data() -> None:
    release_json = {"tender": {"id": "tender-001"}}
    merge_main_nature_procedure(release_json, None)
    assert release_json == {"tender": {"id": "tender-001"}}


if __name__ == "__main__":
    pytest.main()
