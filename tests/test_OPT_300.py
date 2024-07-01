# tests/test_OPT_300.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_opt_300_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:Organizations>
                            <efac:Organization>
                                <efac:Company>
                                    <cac:PartyIdentification>
                                        <cbc:ID schemeName="organization">ORG-0001</cbc:ID>
                                    </cac:PartyIdentification>
                                    <cac:PartyName>
                                        <cbc:Name languageID="ENG">Financial Administration for ...</cbc:Name>
                                    </cac:PartyName>
                                </efac:Company>
                            </efac:Organization>
                            <efac:Organization>
                                <efac:Company>
                                    <cac:PartyIdentification>
                                        <cbc:ID schemeName="organization">ORG-0002</cbc:ID>
                                    </cac:PartyIdentification>
                                    <cac:PartyName>
                                        <cbc:Name languageID="ENG">Service Provider Ltd</cbc:Name>
                                    </cac:PartyName>
                                </efac:Company>
                            </efac:Organization>
                        </efac:Organizations>
                        <efac:NoticeResult>
                            <efac:SettledContract>
                                <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                                <cac:SignatoryParty>
                                    <cac:PartyIdentification>
                                        <cbc:ID schemeName="organization">ORG-0001</cbc:ID>
                                    </cac:PartyIdentification>
                                </cac:SignatoryParty>
                            </efac:SettledContract>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">AWD-0001</cbc:ID>
                                <efac:SettledContract>
                                    <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                                </efac:SettledContract>
                            </efac:LotResult>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
        <cac:ContractingParty>
            <cac:Party>
                <cac:PartyIdentification>
                    <cbc:ID>ORG-0001</cbc:ID>
                </cac:PartyIdentification>
            </cac:Party>
            <cac:ServiceProviderParty>
                <cac:Party>
                    <cac:PartyIdentification>
                        <cbc:ID>ORG-0002</cbc:ID>
                    </cac:PartyIdentification>
                </cac:Party>
            </cac:ServiceProviderParty>
        </cac:ContractingParty>
    </root>
    """
    xml_file = tmp_path / "test_input_opt_300.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    # Test OPT-300-Contract-Signatory
    assert "parties" in result
    assert len(result["parties"]) == 2
    buyer_party = next(party for party in result["parties"] if party["id"] == "ORG-0001")
    assert buyer_party["name"] == "Financial Administration for ..."
    assert "buyer" in buyer_party["roles"]

    assert "awards" in result
    assert len(result["awards"]) == 1
    award = result["awards"][0]
    assert award["id"] == "AWD-0001"
    assert "buyers" in award
    assert len(award["buyers"]) == 1
    assert award["buyers"][0]["id"] == "ORG-0001"

    # Test OPT-300-Procedure-Buyer
    assert "buyer" in result
    assert result["buyer"]["id"] == "ORG-0001"

    # Test OPT-300-Procedure-SProvider
    service_provider = next(party for party in result["parties"] if party["id"] == "ORG-0002")
    assert service_provider["name"] == "Service Provider Ltd"

if __name__ == "__main__":
    pytest.main()