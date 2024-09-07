# tests/test_BT_514_Organization_TouchPoint.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main


def test_bt_514_organization_touchpoint_integration(tmp_path):
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
                                    <cac:PartyLegalEntity>
                                        <cbc:CompanyID>998298</cbc:CompanyID>
                                    </cac:PartyLegalEntity>
                                </efac:Company>
                                <efac:TouchPoint>
                                    <cac:PartyIdentification>
                                        <cbc:ID schemeName="touchpoint">TPO-0001</cbc:ID>
                                    </cac:PartyIdentification>
                                    <cac:PostalAddress>
                                        <cac:Country>
                                            <cbc:IdentificationCode listName="country">GBR</cbc:IdentificationCode>
                                        </cac:Country>
                                    </cac:PostalAddress>
                                </efac:TouchPoint>
                            </efac:Organization>
                        </efac:Organizations>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_touchpoint_country.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json", "r") as f:
        result = json.load(f)

    assert "parties" in result, "Expected 'parties' in result"
    assert (
        len(result["parties"]) == 1
    ), f"Expected 1 party, got {len(result['parties'])}"

    party = result["parties"][0]
    assert party["id"] == "TPO-0001", f"Expected party id 'TPO-0001', got {party['id']}"
    assert "address" in party, "Expected 'address' in party"
    assert "country" in party["address"], "Expected 'country' in party address"
    assert (
        party["address"]["country"] == "GB"
    ), f"Expected country 'GB', got {party['address']['country']}"
    assert "identifier" in party, "Expected 'identifier' in party"
    assert (
        party["identifier"]["id"] == "998298"
    ), f"Expected identifier id '998298', got {party['identifier']['id']}"
    assert (
        party["identifier"]["scheme"] == "internal"
    ), f"Expected identifier scheme 'internal', got {party['identifier']['scheme']}"


if __name__ == "__main__":
    pytest.main()
