# tests/test_BT_23_Lot.py

import pytest
from lxml import etree
import json
import sys
import os

# Add the parent directory to sys.path to import the converter
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from converters.BT_23_Lot import parse_main_nature, merge_main_nature


def test_parse_main_nature_works():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cbc:ProcurementTypeCode listName="contract-nature">works</cbc:ProcurementTypeCode>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    result = parse_main_nature(xml_content)
    assert result == {
        "tender": {"lots": [{"id": "LOT-0001", "mainProcurementCategory": "works"}]}
    }


def test_parse_main_nature_services():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:ProcurementProject>
                <cbc:ProcurementTypeCode listName="contract-nature">services</cbc:ProcurementTypeCode>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    result = parse_main_nature(xml_content)
    assert result == {
        "tender": {"lots": [{"id": "LOT-0002", "mainProcurementCategory": "services"}]}
    }


def test_parse_main_nature_supplies():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0003</cbc:ID>
            <cac:ProcurementProject>
                <cbc:ProcurementTypeCode listName="contract-nature">supplies</cbc:ProcurementTypeCode>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    result = parse_main_nature(xml_content)
    assert result == {
        "tender": {"lots": [{"id": "LOT-0003", "mainProcurementCategory": "goods"}]}
    }


def test_parse_main_nature_multiple_lots():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cbc:ProcurementTypeCode listName="contract-nature">works</cbc:ProcurementTypeCode>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:ProcurementProject>
                <cbc:ProcurementTypeCode listName="contract-nature">services</cbc:ProcurementTypeCode>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    result = parse_main_nature(xml_content)
    assert result == {
        "tender": {
            "lots": [
                {"id": "LOT-0001", "mainProcurementCategory": "works"},
                {"id": "LOT-0002", "mainProcurementCategory": "services"},
            ]
        }
    }


def test_parse_main_nature_no_lots():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    </root>
    """
    result = parse_main_nature(xml_content)
    assert result is None


def test_merge_main_nature():
    release_json = {"tender": {"lots": [{"id": "LOT-0001", "title": "Existing Lot"}]}}
    main_nature_data = {
        "tender": {
            "lots": [
                {"id": "LOT-0001", "mainProcurementCategory": "works"},
                {"id": "LOT-0002", "mainProcurementCategory": "services"},
            ]
        }
    }
    merge_main_nature(release_json, main_nature_data)
    assert release_json == {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "title": "Existing Lot",
                    "mainProcurementCategory": "works",
                },
                {"id": "LOT-0002", "mainProcurementCategory": "services"},
            ]
        }
    }


def test_merge_main_nature_no_data():
    release_json = {"tender": {"lots": []}}
    merge_main_nature(release_json, None)
    assert release_json == {"tender": {"lots": []}}


if __name__ == "__main__":
    pytest.main()
