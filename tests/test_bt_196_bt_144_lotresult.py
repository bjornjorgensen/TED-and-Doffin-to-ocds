import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


def run_main_and_get_result(xml_file, output_dir):
    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    output_files = list(output_dir.glob("*.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_196_bt_144_lotresult_integration(tmp_path, temp_output_dir) -> None:
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
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
                                        <efbc:ReasonDescription>Information delayed publication because of ...</efbc:ReasonDescription>
                                    </efac:FieldsPrivacy>
                                </efac:DecisionReason>
                            </efac:LotResult>
                        </efac:noticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </ContractNotice>
    """
    xml_file = tmp_path / "test_input_bt196_bt144.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert (
        len(result["withheldInformation"]) == 1
    ), f"Expected 1 withheld information item, got {len(result['withheldInformation'])}"

    withheld_info = result["withheldInformation"][0]
    assert (
        withheld_info["id"] == "no-awa-rea-RES-0001"
    ), f"Expected id 'no-awa-rea-RES-0001', got {withheld_info['id']}"
    assert "rationale" in withheld_info, "Expected 'rationale' in withheld_info"
    assert (
        withheld_info["rationale"] == "Information delayed publication because of ..."
    ), f"Unexpected rationale: {withheld_info['rationale']}"


def test_bt_196_bt_144_lotresult_multiple_lots(tmp_path, temp_output_dir) -> None:
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
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
                                        <efbc:ReasonDescription>Reason for lot 1</efbc:ReasonDescription>
                                    </efac:FieldsPrivacy>
                                </efac:DecisionReason>
                            </efac:LotResult>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0002</cbc:ID>
                                <efac:DecisionReason>
                                    <efac:FieldsPrivacy>
                                        <efbc:FieldIdentifierCode>no-awa-rea</efbc:FieldIdentifierCode>
                                        <efbc:ReasonDescription>Reason for lot 2</efbc:ReasonDescription>
                                    </efac:FieldsPrivacy>
                                </efac:DecisionReason>
                            </efac:LotResult>
                        </efac:noticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </ContractNotice>
    """
    xml_file = tmp_path / "test_input_bt196_bt144_multiple.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert (
        len(result["withheldInformation"]) == 2
    ), f"Expected 2 withheld information items, got {len(result['withheldInformation'])}"

    for i, withheld_info in enumerate(result["withheldInformation"], 1):
        assert (
            withheld_info["id"] == f"no-awa-rea-RES-000{i}"
        ), f"Expected id 'no-awa-rea-RES-000{i}', got {withheld_info['id']}"
        assert (
            "rationale" in withheld_info
        ), f"Expected 'rationale' in withheld_info for lot {i}"
        assert (
            withheld_info["rationale"] == f"Reason for lot {i}"
        ), f"Unexpected rationale for lot {i}: {withheld_info['rationale']}"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
