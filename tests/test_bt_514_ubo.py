# tests/test_bt_514_ubo.py
from pathlib import Path
import pytest
import json
import sys

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_514_ubo_integration(tmp_path):
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
                                </efac:company>
                            </efac:organization>
                            <efac:UltimateBeneficialOwner>
                                <cbc:ID schemeName="ubo">ubo-0001</cbc:ID>
                                <cac:ResidenceAddress>
                                    <cac:Country>
                                        <cbc:IdentificationCode listName="country">GBR</cbc:IdentificationCode>
                                    </cac:Country>
                                </cac:ResidenceAddress>
                            </efac:UltimateBeneficialOwner>
                        </efac:organizations>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_ubo_country.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "parties" in result, "Expected 'parties' in result"
    assert (
        len(result["parties"]) == 1
    ), f"Expected 1 party, got {len(result['parties'])}"

    party = result["parties"][0]
    assert party["id"] == "ORG-0001", f"Expected party id 'ORG-0001', got {party['id']}"
    assert "beneficialOwners" in party, "Expected 'beneficialOwners' in party"
    assert (
        len(party["beneficialOwners"]) == 1
    ), f"Expected 1 beneficial owner, got {len(party['beneficialOwners'])}"

    ubo = party["beneficialOwners"][0]
    assert ubo["id"] == "ubo-0001", f"Expected ubo id 'ubo-0001', got {ubo['id']}"
    assert "address" in ubo, "Expected 'address' in ubo"
    assert "country" in ubo["address"], "Expected 'country' in ubo address"
    assert (
        ubo["address"]["country"] == "GB"
    ), f"Expected country 'GB', got {ubo['address']['country']}"


if __name__ == "__main__":
    pytest.main()