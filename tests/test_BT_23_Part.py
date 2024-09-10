# tests/test_BT_23_Part.py

import pytest
import sys
import os

# Add the parent directory to sys.path to import the converter
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ted_and_doffin_to_ocds.converters.BT_23_Part import (
    parse_main_nature_part,
    merge_main_nature_part,
)


def test_parse_main_nature_part_works():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:ProcurementProject>
                <cbc:ProcurementTypeCode listName="contract-nature">works</cbc:ProcurementTypeCode>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    result = parse_main_nature_part(xml_content)
    assert result == {"tender": {"mainProcurementCategory": "works"}}


def test_parse_main_nature_part_services():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:ProcurementProject>
                <cbc:ProcurementTypeCode listName="contract-nature">services</cbc:ProcurementTypeCode>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    result = parse_main_nature_part(xml_content)
    assert result == {"tender": {"mainProcurementCategory": "services"}}


def test_parse_main_nature_part_supplies():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:ProcurementProject>
                <cbc:ProcurementTypeCode listName="contract-nature">supplies</cbc:ProcurementTypeCode>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    result = parse_main_nature_part(xml_content)
    assert result == {"tender": {"mainProcurementCategory": "goods"}}


def test_parse_main_nature_part_no_data():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    </root>
    """
    result = parse_main_nature_part(xml_content)
    assert result is None


def test_merge_main_nature_part():
    release_json = {"tender": {"id": "tender-001"}}
    main_nature_data = {"tender": {"mainProcurementCategory": "works"}}
    merge_main_nature_part(release_json, main_nature_data)
    assert release_json == {
        "tender": {"id": "tender-001", "mainProcurementCategory": "works"}
    }


def test_merge_main_nature_part_no_data():
    release_json = {"tender": {"id": "tender-001"}}
    merge_main_nature_part(release_json, None)
    assert release_json == {"tender": {"id": "tender-001"}}


if __name__ == "__main__":
    pytest.main()
