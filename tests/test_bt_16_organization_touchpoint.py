# tests/test_bt_16_organization_touchpoint.py

import pytest
from ted_and_doffin_to_ocds.converters.bt_16_organization_touchpoint import (
    parse_organization_touchpoint_part_name,
    merge_organization_touchpoint_part_name,
)
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_parse_organization_touchpoint_part_name():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <efac:organizations>
            <efac:organization>
                <efac:company>
                    <cac:partyLegalEntity>
                        <cbc:companyID>998298</cbc:companyID>
                    </cac:partyLegalEntity>
                </efac:company>
                <efac:touchpoint>
                    <cac:partyIdentification>
                        <cbc:ID schemeName="touchpoint">TPO-0001</cbc:ID>
                    </cac:partyIdentification>
                    <cac:partyName>
                        <cbc:Name>Ministry of Education</cbc:Name>
                    </cac:partyName>
                    <cac:PostalAddress>
                        <cbc:Department>Legal Department</cbc:Department>
                    </cac:PostalAddress>
                </efac:touchpoint>
            </efac:organization>
        </efac:organizations>
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
    release_json = {"parties": [{"id": "TPO-0001", "name": "Ministry of Education"}]}

    organization_touchpoint_part_name_data = {
        "parties": [
            {
                "id": "TPO-0001",
                "name": "Ministry of Education - Legal Department",
                "identifier": {"id": "998298", "scheme": "internal"},
            },
        ],
    }

    merge_organization_touchpoint_part_name(
        release_json,
        organization_touchpoint_part_name_data,
    )

    assert len(release_json["parties"]) == 1
    assert (
        release_json["parties"][0]["name"] == "Ministry of Education - Legal Department"
    )
    assert release_json["parties"][0]["identifier"]["id"] == "998298"
    assert release_json["parties"][0]["identifier"]["scheme"] == "internal"


def test_bt_16_organization_touchpoint_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <efac:organizations>
            <efac:organization>
                <efac:company>
                    <cac:partyLegalEntity>
                        <cbc:companyID>998298</cbc:companyID>
                    </cac:partyLegalEntity>
                </efac:company>
                <efac:touchpoint>
                    <cac:partyIdentification>
                        <cbc:ID schemeName="touchpoint">TPO-0001</cbc:ID>
                    </cac:partyIdentification>
                    <cac:partyName>
                        <cbc:Name>Ministry of Education</cbc:Name>
                    </cac:partyName>
                    <cac:PostalAddress>
                        <cbc:Department>Legal Department</cbc:Department>
                    </cac:PostalAddress>
                </efac:touchpoint>
            </efac:organization>
        </efac:organizations>
    </root>
    """
    xml_file = tmp_path / "test_input_organization_touchpoint_part_name.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "parties" in result
    assert len(result["parties"]) == 1
    assert result["parties"][0]["id"] == "TPO-0001"
    assert result["parties"][0]["name"] == "Ministry of Education - Legal Department"
    assert result["parties"][0]["identifier"]["id"] == "998298"
    assert result["parties"][0]["identifier"]["scheme"] == "internal"


if __name__ == "__main__":
    pytest.main()
