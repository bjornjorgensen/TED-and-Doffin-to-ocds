# tests/test_BT_5071_Lot.py

import pytest
from lxml import etree
import json
import sys
import os

# Add the parent directory to sys.path to import the converter
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from converters.BT_5071_Lot import parse_place_performance_country_subdivision, merge_place_performance_country_subdivision

def test_parse_place_performance_country_subdivision():
    xml_content = '''
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:RealizedLocation>
                    <cac:Address>
                        <cbc:CountrySubentityCode listName="nuts=lvl3">UKG23</cbc:CountrySubentityCode>
                    </cac:Address>
                </cac:RealizedLocation>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:ProcurementProject>
                <cac:RealizedLocation>
                    <cac:Address>
                        <cbc:CountrySubentityCode listName="nuts=lvl3">UKG24</cbc:CountrySubentityCode>
                    </cac:Address>
                </cac:RealizedLocation>
                <cac:RealizedLocation>
                    <cac:Address>
                        <cbc:CountrySubentityCode listName="nuts=lvl3">UKG25</cbc:CountrySubentityCode>
                    </cac:Address>
                </cac:RealizedLocation>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    '''

    result = parse_place_performance_country_subdivision(xml_content)

    assert result is not None
    assert "tender" in result
    assert "items" in result["tender"]
    assert len(result["tender"]["items"]) == 3

    assert result["tender"]["items"][0]["relatedLot"] == "LOT-0001"
    assert result["tender"]["items"][0]["deliveryAddresses"][0]["region"] == "UKG23"

    assert result["tender"]["items"][1]["relatedLot"] == "LOT-0002"
    assert result["tender"]["items"][1]["deliveryAddresses"][0]["region"] == "UKG24"

    assert result["tender"]["items"][2]["relatedLot"] == "LOT-0002"
    assert result["tender"]["items"][2]["deliveryAddresses"][0]["region"] == "UKG25"

def test_merge_place_performance_country_subdivision():
    existing_release = {
        "tender": {
            "items": [
                {
                    "id": "1",
                    "relatedLot": "LOT-0001",
                    "deliveryAddresses": [
                        {"streetAddress": "123 Main St"}
                    ]
                }
            ]
        }
    }

    new_data = {
        "tender": {
            "items": [
                {
                    "id": "1",
                    "relatedLot": "LOT-0001",
                    "deliveryAddresses": [
                        {"region": "UKG23"}
                    ]
                },
                {
                    "id": "2",
                    "relatedLot": "LOT-0002",
                    "deliveryAddresses": [
                        {"region": "UKG24"}
                    ]
                }
            ]
        }
    }

    merge_place_performance_country_subdivision(existing_release, new_data)

    assert len(existing_release["tender"]["items"]) == 2

    lot_0001 = next(item for item in existing_release["tender"]["items"] if item["relatedLot"] == "LOT-0001")
    assert len(lot_0001["deliveryAddresses"]) == 1
    assert lot_0001["deliveryAddresses"][0]["streetAddress"] == "123 Main St"
    assert lot_0001["deliveryAddresses"][0]["region"] == "UKG23"

    lot_0002 = next(item for item in existing_release["tender"]["items"] if item["relatedLot"] == "LOT-0002")
    assert len(lot_0002["deliveryAddresses"]) == 1
    assert lot_0002["deliveryAddresses"][0]["region"] == "UKG24"

def test_parse_empty_xml():
    xml_content = '''
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    </root>
    '''

    result = parse_place_performance_country_subdivision(xml_content)

    assert result is None

def test_merge_empty_data():
    existing_release = {
        "tender": {
            "items": [
                {
                    "id": "1",
                    "relatedLot": "LOT-0001",
                    "deliveryAddresses": [
                        {"streetAddress": "123 Main St"}
                    ]
                }
            ]
        }
    }

    new_data = None

    merge_place_performance_country_subdivision(existing_release, new_data)

    assert len(existing_release["tender"]["items"]) == 1
    assert existing_release["tender"]["items"][0]["deliveryAddresses"][0]["streetAddress"] == "123 Main St"

if __name__ == "__main__":
    pytest.main()