import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import configure_logging, main


@pytest.fixture(scope="module")
def setup_logging():
    # Logging disabled for tests
    logger = logging.getLogger(__name__)
    logger.disabled = True
    return logger


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


def test_bt_195_bt_142_lotresult_integration(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
    xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
    xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
    xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
    xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
    <ext:UBLExtensions>
        <ext:UBLExtension>
            <ext:ExtensionContent>
                <efext:EformsExtension>
                    <efac:NoticeResult>
                        <efac:LotResult>
                            <efac:FieldsPrivacy>
                                <efbc:FieldIdentifierCode>win-cho</efbc:FieldIdentifierCode>
                            </efac:FieldsPrivacy>
                            <cbc:ID schemeName="result">RES-0001</cbc:ID>
                        </efac:LotResult>
                    </efac:NoticeResult>
                </efext:EformsExtension>
            </ext:ExtensionContent>
        </ext:UBLExtension>
    </ext:UBLExtensions>
    </ContractNotice>"""

    xml_file = tmp_path / "test_input_bt195_bt142.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert (
        len(result["withheldInformation"]) == 1
    ), f"Expected 1 withheld information item, got {len(result['withheldInformation'])}"

    withheld_info = result["withheldInformation"][0]
    assert (
        withheld_info["id"] == "win-cho-RES-0001"
    ), f"Expected id 'win-cho-RES-0001', got {withheld_info['id']}"
    assert (
        withheld_info["field"] == "win-cho"
    ), f"Expected field 'win-cho', got {withheld_info['field']}"
    assert (
        withheld_info["name"] == "Winner Chosen"
    ), f"Expected name 'Winner Chosen', got {withheld_info['name']}"


def test_bt_195_bt_142_lotresult_multiple_lots(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
    xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
    xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
    xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
    xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
    <ext:UBLExtensions>
        <ext:UBLExtension>
            <ext:ExtensionContent>
                <efext:EformsExtension>
                    <efac:NoticeResult>
                        <efac:LotResult>
                            <efac:FieldsPrivacy>
                                <efbc:FieldIdentifierCode>win-cho</efbc:FieldIdentifierCode>
                            </efac:FieldsPrivacy>
                            <cbc:ID schemeName="result">RES-0001</cbc:ID>
                        </efac:LotResult>
                        <efac:LotResult>
                            <efac:FieldsPrivacy>
                                <efbc:FieldIdentifierCode>win-cho</efbc:FieldIdentifierCode>
                            </efac:FieldsPrivacy>
                            <cbc:ID schemeName="result">RES-0002</cbc:ID>
                        </efac:LotResult>
                    </efac:NoticeResult>
                </efext:EformsExtension>
            </ext:ExtensionContent>
        </ext:UBLExtension>
    </ext:UBLExtensions>
    </ContractNotice>"""

    xml_file = tmp_path / "test_input_bt195_bt142_multiple.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert (
        len(result["withheldInformation"]) == 2
    ), f"Expected 2 withheld information items, got {len(result['withheldInformation'])}"

    for i, withheld_info in enumerate(result["withheldInformation"], 1):
        assert (
            withheld_info["id"] == f"win-cho-RES-000{i}"
        ), f"Expected id 'win-cho-RES-000{i}', got {withheld_info['id']}"
        assert (
            withheld_info["field"] == "win-cho"
        ), f"Expected field 'win-cho', got {withheld_info['field']}"
        assert (
            withheld_info["name"] == "Winner Chosen"
        ), f"Expected name 'Winner Chosen', got {withheld_info['name']}"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
