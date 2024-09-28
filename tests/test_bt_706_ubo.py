from ted_and_doffin_to_ocds.converters.bt_706_ubo import (
    parse_ubo_nationality,
    merge_ubo_nationality,
)
from pathlib import Path
import json
import sys

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_parse_ubo_nationality():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1">
        <efext:UBLExtensions>
            <efext:UBLExtension>
                <efext:ExtensionContent>
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
                            <efac:Nationality>
                                <cbc:NationalityID>DEU</cbc:NationalityID>
                            </efac:Nationality>
                        </efac:UltimateBeneficialOwner>
                    </efac:organizations>
                </efext:ExtensionContent>
            </efext:UBLExtension>
        </efext:UBLExtensions>
    </root>
    """

    result = parse_ubo_nationality(xml_content)

    assert result is not None
    assert "parties" in result
    assert len(result["parties"]) == 1
    assert result["parties"][0]["id"] == "ORG-0001"
    assert len(result["parties"][0]["beneficialOwners"]) == 1
    assert result["parties"][0]["beneficialOwners"][0]["id"] == "ubo-0001"
    assert result["parties"][0]["beneficialOwners"][0]["nationalities"] == ["DE"]


def test_merge_ubo_nationality():
    release_json = {"parties": [{"id": "ORG-0001", "name": "Existing organization"}]}

    ubo_nationality_data = {
        "parties": [
            {
                "id": "ORG-0001",
                "beneficialOwners": [{"id": "ubo-0001", "nationalities": ["DE"]}],
            },
        ],
    }

    merge_ubo_nationality(release_json, ubo_nationality_data)

    assert "beneficialOwners" in release_json["parties"][0]
    assert len(release_json["parties"][0]["beneficialOwners"]) == 1
    assert release_json["parties"][0]["beneficialOwners"][0]["id"] == "ubo-0001"
    assert release_json["parties"][0]["beneficialOwners"][0]["nationalities"] == ["DE"]


def test_bt_706_ubo_nationality_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1">
        <efext:UBLExtensions>
            <efext:UBLExtension>
                <efext:ExtensionContent>
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
                            <efac:Nationality>
                                <cbc:NationalityID>DEU</cbc:NationalityID>
                            </efac:Nationality>
                        </efac:UltimateBeneficialOwner>
                        <efac:UltimateBeneficialOwner>
                            <cbc:ID schemeName="ubo">ubo-0002</cbc:ID>
                            <efac:Nationality>
                                <cbc:NationalityID>FRA</cbc:NationalityID>
                            </efac:Nationality>
                        </efac:UltimateBeneficialOwner>
                    </efac:organizations>
                </efext:ExtensionContent>
            </efext:UBLExtension>
        </efext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_ubo_nationality.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "parties" in result
    assert len(result["parties"]) == 1

    beneficial_owners = result["parties"][0].get("beneficialOwners", [])
    assert len(beneficial_owners) == 2

    ubo_1 = next((ubo for ubo in beneficial_owners if ubo["id"] == "ubo-0001"), None)
    assert ubo_1 is not None
    assert ubo_1["nationalities"] == ["DE"]

    ubo_2 = next((ubo for ubo in beneficial_owners if ubo["id"] == "ubo-0002"), None)
    assert ubo_2 is not None
    assert ubo_2["nationalities"] == ["FR"]
