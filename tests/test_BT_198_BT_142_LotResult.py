# tests/test_BT_198_BT_142_LotResult.py

import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_198_bt_142_lotresult_integration(tmp_path):
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
                                    <efbc:PublicationDate>2025-03-31+01:00</efbc:PublicationDate>
                                </efac:FieldsPrivacy>
                            </efac:LotResult>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_bt198_bt142.xml"
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
        "availabilityDate" in withheld_info
    ), "Expected 'availabilityDate' in withheld_info"
    assert (
        withheld_info["availabilityDate"] == "2025-03-31T00:00:00+01:00"
    ), f"Expected availabilityDate '2025-03-31T00:00:00+01:00', got {withheld_info['availabilityDate']}"


def test_bt_198_bt_142_lotresult_multiple_lots(tmp_path):
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
                                    <efbc:PublicationDate>2025-03-31+01:00</efbc:PublicationDate>
                                </efac:FieldsPrivacy>
                            </efac:LotResult>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0002</cbc:ID>
                                <efac:FieldsPrivacy>
                                    <efbc:FieldIdentifierCode>win-cho</efbc:FieldIdentifierCode>
                                    <efbc:PublicationDate>2025-04-30+02:00</efbc:PublicationDate>
                                </efac:FieldsPrivacy>
                            </efac:LotResult>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_bt198_bt142_multiple.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert (
        len(result["withheldInformation"]) == 2
    ), f"Expected 2 withheld information items, got {len(result['withheldInformation'])}"

    expected_data = [
        {"id": "win-cho-RES-0001", "availabilityDate": "2025-03-31T00:00:00+01:00"},
        {"id": "win-cho-RES-0002", "availabilityDate": "2025-04-30T00:00:00+02:00"},
    ]

    for withheld_info, expected in zip(
        result["withheldInformation"], expected_data, strict=False
    ):
        assert (
            withheld_info["id"] == expected["id"]
        ), f"Expected id '{expected['id']}', got {withheld_info['id']}"
        assert (
            "availabilityDate" in withheld_info
        ), f"Expected 'availabilityDate' in withheld_info for {expected['id']}"
        assert (
            withheld_info["availabilityDate"] == expected["availabilityDate"]
        ), f"Expected availabilityDate '{expected['availabilityDate']}' for {expected['id']}, got {withheld_info['availabilityDate']}"
