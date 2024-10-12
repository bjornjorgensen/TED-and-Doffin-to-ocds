# tests/test_opt_170_tenderer_leader.py

from ted_and_doffin_to_ocds.converters.opt_170_tenderer_leader import (
    parse_tendering_party_leader,
    merge_tendering_party_leader,
)


def test_parse_tendering_party_leader():
    xml_content = """
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:TenderingParty>
                                <efac:Tenderer>
                                    <cbc:ID schemeName="organization">ORG-0001</cbc:ID>
                                    <efbc:GroupLeadIndicator>true</efbc:GroupLeadIndicator>
                                </efac:Tenderer>
                            </efac:TenderingParty>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """

    result = parse_tendering_party_leader(xml_content)

    assert result is not None
    assert "parties" in result
    assert len(result["parties"]) == 1

    party = result["parties"][0]
    assert party["id"] == "ORG-0001"
    assert "roles" in party
    assert set(party["roles"]) == {"tenderer", "leadTenderer"}


def test_merge_tendering_party_leader():
    release_json = {"parties": []}
    leader_data = {
        "parties": [{"id": "ORG-0001", "roles": ["tenderer", "leadTenderer"]}]
    }

    merge_tendering_party_leader(release_json, leader_data)

    assert "parties" in release_json
    assert len(release_json["parties"]) == 1

    party = release_json["parties"][0]
    assert party["id"] == "ORG-0001"
    assert "roles" in party
    assert set(party["roles"]) == {"tenderer", "leadTenderer"}


def test_merge_tendering_party_leader_existing_party():
    release_json = {"parties": [{"id": "ORG-0001", "roles": ["supplier"]}]}
    leader_data = {
        "parties": [{"id": "ORG-0001", "roles": ["tenderer", "leadTenderer"]}]
    }

    merge_tendering_party_leader(release_json, leader_data)

    assert len(release_json["parties"]) == 1

    party = release_json["parties"][0]
    assert party["id"] == "ORG-0001"
    assert "roles" in party
    assert set(party["roles"]) == {"supplier", "tenderer", "leadTenderer"}
