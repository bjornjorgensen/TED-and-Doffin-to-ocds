# tests/test_bt_195_bt_144_LotResult.py
from pathlib import Path
import pytest
import json
import sys

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_195_bt_144_lotresult_integration(tmp_path):
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
                                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                                <efac:DecisionReason>
                                    <efac:FieldsPrivacy>
                                        <efbc:FieldIdentifierCode>no-awa-rea</efbc:FieldIdentifierCode>
                                    </efac:FieldsPrivacy>
                                </efac:DecisionReason>
                            </efac:LotResult>
                        </efac:noticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_bt195_bt144.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert (
        len(result["withheldInformation"]) == 1
    ), f"Expected 1 withheld information item, got {len(result['withheldInformation'])}"

    withheld_info = result["withheldInformation"][0]
    assert (
        withheld_info["id"] == "no-awa-rea-RES-0001"
    ), f"Expected id 'no-awa-rea-RES-0001', got {withheld_info['id']}"
    assert (
        withheld_info["field"] == "no-awa-rea"
    ), f"Expected field 'no-awa-rea', got {withheld_info['field']}"
    assert (
        withheld_info["name"] == "Not Awarded Reason"
    ), f"Expected name 'Not Awarded Reason', got {withheld_info['name']}"


def test_bt_195_bt_144_lotresult_multiple_lots(tmp_path):
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
                                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                                <efac:DecisionReason>
                                    <efac:FieldsPrivacy>
                                        <efbc:FieldIdentifierCode>no-awa-rea</efbc:FieldIdentifierCode>
                                    </efac:FieldsPrivacy>
                                </efac:DecisionReason>
                            </efac:LotResult>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0002</cbc:ID>
                                <efac:DecisionReason>
                                    <efac:FieldsPrivacy>
                                        <efbc:FieldIdentifierCode>no-awa-rea</efbc:FieldIdentifierCode>
                                    </efac:FieldsPrivacy>
                                </efac:DecisionReason>
                            </efac:LotResult>
                        </efac:noticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_bt195_bt144_multiple.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert (
        len(result["withheldInformation"]) == 2
    ), f"Expected 2 withheld information items, got {len(result['withheldInformation'])}"

    for i, withheld_info in enumerate(result["withheldInformation"], 1):
        assert (
            withheld_info["id"] == f"no-awa-rea-RES-000{i}"
        ), f"Expected id 'no-awa-rea-RES-000{i}', got {withheld_info['id']}"
        assert (
            withheld_info["field"] == "no-awa-rea"
        ), f"Expected field 'no-awa-rea', got {withheld_info['field']}"
        assert (
            withheld_info["name"] == "Not Awarded Reason"
        ), f"Expected name 'Not Awarded Reason', got {withheld_info['name']}"


if __name__ == "__main__":
    pytest.main()
