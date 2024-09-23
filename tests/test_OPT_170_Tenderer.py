# tests/test_OPT_170_Tenderer.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_tendering_party_leader_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
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
                            <efac:TenderingParty>
                                <efac:Tenderer>
                                    <cbc:ID schemeName="organization">ORG-0002</cbc:ID>
                                    <efbc:GroupLeadIndicator>false</efbc:GroupLeadIndicator>
                                </efac:Tenderer>
                            </efac:TenderingParty>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_tendering_party_leader.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "parties" in result
    assert len(result["parties"]) == 2

    leader_party = next(
        (party for party in result["parties"] if party["id"] == "ORG-0001"), None,
    )
    assert leader_party is not None
    assert set(leader_party["roles"]) == {"tenderer", "leadTenderer"}

    non_leader_party = next(
        (party for party in result["parties"] if party["id"] == "ORG-0002"), None,
    )
    assert non_leader_party is not None
    assert set(non_leader_party["roles"]) == {"tenderer"}


def test_tendering_party_leader_no_data(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_tendering_party_leader_no_data.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "parties" not in result or not any(
        "tenderer" in party.get("roles", []) for party in result.get("parties", [])
    )


if __name__ == "__main__":
    pytest.main()
