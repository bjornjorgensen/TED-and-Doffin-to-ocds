# tests/test_OPT_202_ubo.py

import pytest
from ted_and_doffin_to_ocds.converters.opt_202_ubo import (
    parse_ubo_identifier,
    merge_ubo_identifier,
)
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_parse_ubo_identifier():
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
                            </efac:UltimateBeneficialOwner>
                            <efac:UltimateBeneficialOwner>
                                <cbc:ID schemeName="ubo">ubo-0002</cbc:ID>
                            </efac:UltimateBeneficialOwner>
                        </efac:organizations>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """

    result = parse_ubo_identifier(xml_content)

    assert result is not None
    assert "parties" in result
    assert len(result["parties"]) == 1
    assert result["parties"][0]["id"] == "ORG-0001"
    assert "beneficialOwners" in result["parties"][0]
    assert len(result["parties"][0]["beneficialOwners"]) == 2
    assert result["parties"][0]["beneficialOwners"][0]["id"] == "ubo-0001"
    assert result["parties"][0]["beneficialOwners"][1]["id"] == "ubo-0002"


def test_merge_ubo_identifier():
    release_json = {"parties": [{"id": "ORG-0001", "name": "Existing organization"}]}

    ubo_data = {
        "parties": [
            {
                "id": "ORG-0001",
                "beneficialOwners": [{"id": "ubo-0001"}, {"id": "ubo-0002"}],
            },
        ],
    }

    merge_ubo_identifier(release_json, ubo_data)

    assert "beneficialOwners" in release_json["parties"][0]
    assert len(release_json["parties"][0]["beneficialOwners"]) == 2
    assert release_json["parties"][0]["beneficialOwners"][0]["id"] == "ubo-0001"
    assert release_json["parties"][0]["beneficialOwners"][1]["id"] == "ubo-0002"


def test_parse_ubo_identifier_no_data():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:party>
            <cac:partyName>
                <cbc:Name>Test organization</cbc:Name>
            </cac:partyName>
        </cac:party>
    </root>
    """

    result = parse_ubo_identifier(xml_content)

    assert result is None


def test_merge_ubo_identifier_no_data():
    release_json = {"parties": [{"id": "ORG-0001", "name": "Existing organization"}]}

    ubo_data = None

    merge_ubo_identifier(release_json, ubo_data)

    assert "beneficialOwners" not in release_json["parties"][0]


def test_opt_202_ubo_integration(tmp_path):
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
                            </efac:UltimateBeneficialOwner>
                            <efac:UltimateBeneficialOwner>
                                <cbc:ID schemeName="ubo">ubo-0002</cbc:ID>
                            </efac:UltimateBeneficialOwner>
                        </efac:organizations>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_ubo.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "parties" in result
    assert len(result["parties"]) == 1
    assert result["parties"][0]["id"] == "ORG-0001"
    assert "beneficialOwners" in result["parties"][0]
    assert len(result["parties"][0]["beneficialOwners"]) == 2
    assert result["parties"][0]["beneficialOwners"][0]["id"] == "ubo-0001"
    assert result["parties"][0]["beneficialOwners"][1]["id"] == "ubo-0002"


if __name__ == "__main__":
    pytest.main()
