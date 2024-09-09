# tests/test_BT_197_BT_142_LotResult.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main


def test_bt_197_bt_142_lotresult_integration(tmp_path):
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
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                                <efac:FieldsPrivacy>
                                    <efbc:FieldIdentifierCode>win-cho</efbc:FieldIdentifierCode>
                                    <cbc:ReasonCode listName="non-publication-justification">oth-int</cbc:ReasonCode>
                                </efac:FieldsPrivacy>
                            </efac:LotResult>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_bt197_bt142.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert (
        len(result["withheldInformation"]) == 1
    ), f"Expected 1 withheld information item, got {len(result['withheldInformation'])}"

    withheld_info = result["withheldInformation"][0]
    assert (
        withheld_info["id"] == "win-cho-RES-0001"
    ), f"Expected id 'win-cho-RES-0001', got {withheld_info['id']}"
    assert (
        "rationaleClassifications" in withheld_info
    ), "Expected 'rationaleClassifications' in withheld_info"
    assert (
        len(withheld_info["rationaleClassifications"]) == 1
    ), f"Expected 1 rationale classification, got {len(withheld_info['rationaleClassifications'])}"

    classification = withheld_info["rationaleClassifications"][0]
    assert (
        classification["scheme"] == "eu-non-publication-justification"
    ), f"Expected scheme 'eu-non-publication-justification', got {classification['scheme']}"
    assert (
        classification["id"] == "oth-int"
    ), f"Expected id 'oth-int', got {classification['id']}"
    assert (
        classification["description"] == "Other public interest"
    ), f"Expected description 'Other public interest', got {classification['description']}"
    assert (
        classification["uri"]
        == "http://publications.europa.eu/resource/authority/non-publication-justification/oth-int"
    ), f"Unexpected URI: {classification['uri']}"


def test_bt_197_bt_142_lotresult_multiple_lots(tmp_path):
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
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                                <efac:FieldsPrivacy>
                                    <efbc:FieldIdentifierCode>win-cho</efbc:FieldIdentifierCode>
                                    <cbc:ReasonCode listName="non-publication-justification">oth-int</cbc:ReasonCode>
                                </efac:FieldsPrivacy>
                            </efac:LotResult>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0002</cbc:ID>
                                <efac:FieldsPrivacy>
                                    <efbc:FieldIdentifierCode>win-cho</efbc:FieldIdentifierCode>
                                    <cbc:ReasonCode listName="non-publication-justification">fair-comp</cbc:ReasonCode>
                                </efac:FieldsPrivacy>
                            </efac:LotResult>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_bt197_bt142_multiple.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert (
        len(result["withheldInformation"]) == 2
    ), f"Expected 2 withheld information items, got {len(result['withheldInformation'])}"

    expected_data = [
        {
            "id": "win-cho-RES-0001",
            "code": "oth-int",
            "description": "Other public interest",
        },
        {
            "id": "win-cho-RES-0002",
            "code": "fair-comp",
            "description": "Fair competition",
        },
    ]

    for withheld_info, expected in zip(result["withheldInformation"], expected_data, strict=False):
        assert (
            withheld_info["id"] == expected["id"]
        ), f"Expected id '{expected['id']}', got {withheld_info['id']}"
        assert (
            "rationaleClassifications" in withheld_info
        ), f"Expected 'rationaleClassifications' in withheld_info for {expected['id']}"
        assert (
            len(withheld_info["rationaleClassifications"]) == 1
        ), f"Expected 1 rationale classification for {expected['id']}, got {len(withheld_info['rationaleClassifications'])}"

        classification = withheld_info["rationaleClassifications"][0]
        assert (
            classification["scheme"] == "eu-non-publication-justification"
        ), f"Expected scheme 'eu-non-publication-justification' for {expected['id']}, got {classification['scheme']}"
        assert (
            classification["id"] == expected["code"]
        ), f"Expected id '{expected['code']}' for {expected['id']}, got {classification['id']}"
        assert (
            classification["description"] == expected["description"]
        ), f"Expected description '{expected['description']}' for {expected['id']}, got {classification['description']}"


if __name__ == "__main__":
    pytest.main()
