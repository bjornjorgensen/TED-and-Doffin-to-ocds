# tests/test_BT_706_UBO.py

import pytest
from lxml import etree
from converters.BT_706_UBO import parse_ubo_nationality, merge_ubo_nationality
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_parse_ubo_nationality():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <efac:Organizations>
            <efac:Organization>
                <efac:Company>
                    <cac:PartyIdentification>
                        <cbc:ID schemeName="organization">ORG-0001</cbc:ID>
                    </cac:PartyIdentification>
                </efac:Company>
            </efac:Organization>
            <efac:UltimateBeneficialOwner>
                <cbc:ID schemeName="ubo">UBO-0001</cbc:ID>
                <efac:Nationality>
                    <cbc:NationalityID>DEU</cbc:NationalityID>
                </efac:Nationality>
            </efac:UltimateBeneficialOwner>
        </efac:Organizations>
    </root>
    """
    
    result = parse_ubo_nationality(xml_content)
    
    assert result is not None
    assert "parties" in result
    assert len(result["parties"]) == 1
    assert result["parties"][0]["id"] == "ORG-0001"
    assert len(result["parties"][0]["beneficialOwners"]) == 1
    assert result["parties"][0]["beneficialOwners"][0]["id"] == "UBO-0001"
    assert result["parties"][0]["beneficialOwners"][0]["nationalities"] == ["DE"]

def test_merge_ubo_nationality():
    release_json = {
        "parties": [
            {
                "id": "ORG-0001",
                "name": "Existing Organization"
            }
        ]
    }
    
    ubo_nationality_data = {
        "parties": [
            {
                "id": "ORG-0001",
                "beneficialOwners": [
                    {
                        "id": "UBO-0001",
                        "nationalities": ["DE"]
                    }
                ]
            }
        ]
    }
    
    merge_ubo_nationality(release_json, ubo_nationality_data)
    
    assert "beneficialOwners" in release_json["parties"][0]
    assert len(release_json["parties"][0]["beneficialOwners"]) == 1
    assert release_json["parties"][0]["beneficialOwners"][0]["id"] == "UBO-0001"
    assert release_json["parties"][0]["beneficialOwners"][0]["nationalities"] == ["DE"]

def test_bt_706_ubo_nationality_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <efac:Organizations>
            <efac:Organization>
                <efac:Company>
                    <cac:PartyIdentification>
                        <cbc:ID schemeName="organization">ORG-0001</cbc:ID>
                    </cac:PartyIdentification>
                </efac:Company>
            </efac:Organization>
            <efac:UltimateBeneficialOwner>
                <cbc:ID schemeName="ubo">UBO-0001</cbc:ID>
                <efac:Nationality>
                    <cbc:NationalityID>DEU</cbc:NationalityID>
                </efac:Nationality>
            </efac:UltimateBeneficialOwner>
            <efac:UltimateBeneficialOwner>
                <cbc:ID schemeName="ubo">UBO-0002</cbc:ID>
                <efac:Nationality>
                    <cbc:NationalityID>FRA</cbc:NationalityID>
                </efac:Nationality>
            </efac:UltimateBeneficialOwner>
        </efac:Organizations>
    </root>
    """
    xml_file = tmp_path / "test_input_ubo_nationality.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "parties" in result
    assert len(result["parties"]) == 1
    assert result["parties"][0]["id"] == "ORG-0001"
    assert "beneficialOwners" in result["parties"][0]
    assert len(result["parties"][0]["beneficialOwners"]) == 2
    
    ubo_1 = next((bo for bo in result["parties"][0]["beneficialOwners"] if bo["id"] == "UBO-0001"), None)
    assert ubo_1 is not None
    assert ubo_1["nationalities"] == ["DE"]
    
    ubo_2 = next((bo for bo in result["parties"][0]["beneficialOwners"] if bo["id"] == "UBO-0002"), None)
    assert ubo_2 is not None
    assert ubo_2["nationalities"] == ["FR"]

if __name__ == "__main__":
    pytest.main()