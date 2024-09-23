# tests/test_OPT_300_Contract_Signatory.py

import pytest
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_opt_300_contract_signatory_integration(tmp_path):
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
                        <efac:organizations>
                            <efac:organization>
                                <efac:company>
                                    <cac:partyIdentification>
                                        <cbc:ID schemeName="organization">ORG-0001</cbc:ID>
                                    </cac:partyIdentification>
                                    <cac:partyName>
                                        <cbc:Name languageID="ENG">Financial Administration for ...</cbc:Name>
                                    </cac:partyName>
                                </efac:company>
                            </efac:organization>
                        </efac:organizations>
                        <efac:noticeResult>
                            <efac:SettledContract>
                                <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                                <cac:Signatoryparty>
                                    <cac:partyIdentification>
                                        <cbc:ID schemeName="organization">ORG-0001</cbc:ID>
                                    </cac:partyIdentification>
                                </cac:Signatoryparty>
                            </efac:SettledContract>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                                <efac:SettledContract>
                                    <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                                </efac:SettledContract>
                            </efac:LotResult>
                        </efac:noticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_contract_signatory.xml"
    xml_file.write_text(xml_content)

    result = main(str(xml_file), "ocds-test-prefix")

    assert result is not None
    assert "initiationType" in result
    assert result["initiationType"] == "tender"

    assert "parties" in result
    assert len(result["parties"]) == 1
    party = result["parties"][0]
    assert party["id"] == "ORG-0001"
    assert party["name"] == "Financial Administration for ..."
    assert "buyer" in party["roles"]

    assert "awards" in result
    assert len(result["awards"]) == 1
    award = result["awards"][0]
    assert award["id"] == "RES-0001"
    assert "buyers" in award
    assert len(award["buyers"]) == 1
    assert award["buyers"][0]["id"] == "ORG-0001"

    assert "contracts" in result
    assert len(result["contracts"]) == 1
    contract = result["contracts"][0]
    assert contract["id"] == "CON-0001"
    assert contract["awardID"] == "RES-0001"


if __name__ == "__main__":
    pytest.main()
