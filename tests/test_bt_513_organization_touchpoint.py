# tests/test_bt_513_organization_touchpoint.py
from pathlib import Path
import pytest
import json
import sys

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_513_organization_touchpoint_integration(tmp_path):
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
                                    <cac:partyLegalEntity>
                                        <cbc:companyID>998298</cbc:companyID>
                                    </cac:partyLegalEntity>
                                </efac:company>
                                <efac:touchpoint>
                                    <cac:partyIdentification>
                                        <cbc:ID schemeName="touchpoint">TPO-0001</cbc:ID>
                                    </cac:partyIdentification>
                                    <cac:PostalAddress>
                                        <cbc:CityName>SmallCity</cbc:CityName>
                                    </cac:PostalAddress>
                                </efac:touchpoint>
                            </efac:organization>
                        </efac:organizations>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_bt_513_organization_touchpoint.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "parties" in result, "Expected 'parties' in result"
    assert (
        len(result["parties"]) == 1
    ), f"Expected 1 party, got {len(result['parties'])}"

    party = result["parties"][0]
    assert party["id"] == "TPO-0001", f"Expected party id 'TPO-0001', got {party['id']}"
    assert "address" in party, "Expected 'address' in party"
    assert "locality" in party["address"], "Expected 'locality' in party address"
    expected_locality = "SmallCity"
    assert (
        party["address"]["locality"] == expected_locality
    ), f"Expected locality '{expected_locality}', got {party['address']['locality']}"
    assert "identifier" in party, "Expected 'identifier' in party"
    assert (
        party["identifier"]["id"] == "998298"
    ), f"Expected identifier id '998298', got {party['identifier']['id']}"
    assert (
        party["identifier"]["scheme"] == "internal"
    ), f"Expected identifier scheme 'internal', got {party['identifier']['scheme']}"


if __name__ == "__main__":
    pytest.main()
