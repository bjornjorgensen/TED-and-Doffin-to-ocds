# tests/test_bt_196_bt_142_LotResult.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_196_bt_142_lotresult_integration(tmp_path):
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
                        <efac:noticeResult>
                            <efac:LotResult>
                                <efac:FieldsPrivacy>
                                    <efbc:FieldIdentifierCode>win-cho</efbc:FieldIdentifierCode>
                                    <efbc:ReasonDescription>Information delayed publication because of ...</efbc:ReasonDescription>
                                </efac:FieldsPrivacy>
                                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                            </efac:LotResult>
                        </efac:noticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_bt196_bt142.xml"
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
    assert "rationale" in withheld_info, "Expected 'rationale' in withheld_info"
    assert (
        withheld_info["rationale"] == "Information delayed publication because of ..."
    ), f"Unexpected rationale: {withheld_info['rationale']}"


def test_bt_196_bt_142_lotresult_multiple_lots(tmp_path):
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
                        <efac:noticeResult>
                            <efac:LotResult>
                                <efac:FieldsPrivacy>
                                    <efbc:FieldIdentifierCode>win-cho</efbc:FieldIdentifierCode>
                                    <efbc:ReasonDescription>Reason for lot 1</efbc:ReasonDescription>
                                </efac:FieldsPrivacy>
                                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                            </efac:LotResult>
                            <efac:LotResult>
                                <efac:FieldsPrivacy>
                                    <efbc:FieldIdentifierCode>win-cho</efbc:FieldIdentifierCode>
                                    <efbc:ReasonDescription>Reason for lot 2</efbc:ReasonDescription>
                                </efac:FieldsPrivacy>
                                <cbc:ID schemeName="result">RES-0002</cbc:ID>
                            </efac:LotResult>
                        </efac:noticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_bt196_bt142_multiple.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert (
        len(result["withheldInformation"]) == 2
    ), f"Expected 2 withheld information items, got {len(result['withheldInformation'])}"

    for i, withheld_info in enumerate(result["withheldInformation"], 1):
        assert (
            withheld_info["id"] == f"win-cho-RES-000{i}"
        ), f"Expected id 'win-cho-RES-000{i}', got {withheld_info['id']}"
        assert (
            "rationale" in withheld_info
        ), f"Expected 'rationale' in withheld_info for lot {i}"
        assert (
            withheld_info["rationale"] == f"Reason for lot {i}"
        ), f"Unexpected rationale for lot {i}: {withheld_info['rationale']}"


if __name__ == "__main__":
    pytest.main()
