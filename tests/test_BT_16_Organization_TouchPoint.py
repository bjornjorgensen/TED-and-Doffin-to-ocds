# tests/test_BT_16_Organization_TouchPoint.py

import pytest
from lxml import etree
from converters.BT_16_Organization_TouchPoint import parse_organization_touchpoint_part_name, merge_organization_touchpoint_part_name
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_parse_organization_touchpoint_part_name():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <efac:Organizations>
            <efac:Organization>
                <efac:Company>
                    <cac:PartyLegalEntity>
                        <cbc:CompanyID>998298</cbc:CompanyID>
                    </cac:PartyLegalEntity>
                </efac:Company>
                <efac:TouchPoint>
                    <cac:PartyIdentification>
                        <cbc:ID schemeName="touchpoint">TPO-0001</cbc:ID>
                    </cac:PartyIdentification>
                    <cac:PartyName>
                        <cbc:Name>Ministry of Education</cbc:Name>
                    </cac:PartyName>
                    <cac:PostalAddress>
                        <cbc:Department>Legal Department</cbc:Department>
                    </cac:PostalAddress>
                </efac:TouchPoint>
            </efac:Organization>
        </efac:Organizations>
    </root>
    """
    
    result = parse_organization_touchpoint_part_name(xml_content)
    
    assert result is not None
    assert "parties" in result
    assert len(result["parties"]) == 1
    assert result["parties"][0]["id"] == "TPO-0001"
    assert result["parties"][0]["name"] == "Ministry of Education - Legal Department"
    assert result["parties"][0]["identifier"]["id"] == "998298"
    assert result["parties"][0]["identifier"]["scheme"] == "internal"

def test_merge_organization_touchpoint_part_name():
    release_json = {
        "parties": [
            {
                "id": "TPO-0001",
                "name": "Ministry of Education"
            }
        ]
    }
    
    organization_touchpoint_part_name_data = {
        "parties": [
            {
                "id": "TPO-0001",
                "name": "Ministry of Education - Legal Department",
                "identifier": {
                    "id": "998298",
                    "scheme": "internal"
                }
            }
        ]
    }
    
    merge_organization_touchpoint_part_name(release_json, organization_touchpoint_part_name_data)
    
    assert len(release_json["parties"]) == 1
    assert release_json["parties"][0]["name"] == "Ministry of Education - Legal Department"
    assert release_json["parties"][0]["identifier"]["id"] == "998298"
    assert release_json["parties"][0]["identifier"]["scheme"] == "internal"

def test_bt_16_organization_touchpoint_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <efac:Organizations>
            <efac:Organization>
                <efac:Company>
                    <cac:PartyLegalEntity>
                        <cbc:CompanyID>998298</cbc:CompanyID>
                    </cac:PartyLegalEntity>
                </efac:Company>
                <efac:TouchPoint>
                    <cac:PartyIdentification>
                        <cbc:ID schemeName="touchpoint">TPO-0001</cbc:ID>
                    </cac:PartyIdentification>
                    <cac:PartyName>
                        <cbc:Name>Ministry of Education</cbc:Name>
                    </cac:PartyName>
                    <cac:PostalAddress>
                        <cbc:Department>Legal Department</cbc:Department>
                    </cac:PostalAddress>
                </efac:TouchPoint>
            </efac:Organization>
        </efac:Organizations>
    </root>
    """
    xml_file = tmp_path / "test_input_organization_touchpoint_part_name.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "parties" in result
    assert len(result["parties"]) == 1
    assert result["parties"][0]["id"] == "TPO-0001"
    assert result["parties"][0]["name"] == "Ministry of Education - Legal Department"
    assert result["parties"][0]["identifier"]["id"] == "998298"
    assert result["parties"][0]["identifier"]["scheme"] == "internal"

if __name__ == "__main__":
    pytest.main()