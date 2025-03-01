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


def test_bt_197_bt_144_lotresult_integration(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging
    xml_content = """
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
                        <efac:NoticeResult>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                                <efac:DecisionReason>
                                    <efac:FieldsPrivacy>
                                        <efbc:FieldIdentifierCode>no-awa-rea</efbc:FieldIdentifierCode>
                                        <cbc:ReasonCode listName="non-publication-justification">oth-int</cbc:ReasonCode>
                                    </efac:FieldsPrivacy>
                                </efac:DecisionReason>
                            </efac:LotResult>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </ContractNotice>
    """
    xml_file = tmp_path / "test_input_bt197_bt144.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert (
        len(result["withheldInformation"]) == 1
    ), f"Expected 1 withheld information item, got {len(result['withheldInformation'])}"

    withheld_info = result["withheldInformation"][0]
    assert (
        withheld_info["id"] == "no-awa-rea-RES-0001"
    ), f"Expected id 'no-awa-rea-RES-0001', got {withheld_info['id']}"
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


def test_bt_197_bt_144_lotresult_multiple_lots(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging
    xml_content = """
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
                        <efac:NoticeResult>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                                <efac:DecisionReason>
                                    <efac:FieldsPrivacy>
                                        <efbc:FieldIdentifierCode>no-awa-rea</efbc:FieldIdentifierCode>
                                        <cbc:ReasonCode listName="non-publication-justification">oth-int</cbc:ReasonCode>
                                    </efac:FieldsPrivacy>
                                </efac:DecisionReason>
                            </efac:LotResult>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0002</cbc:ID>
                                <efac:DecisionReason>
                                    <efac:FieldsPrivacy>
                                        <efbc:FieldIdentifierCode>no-awa-rea</efbc:FieldIdentifierCode>
                                        <cbc:ReasonCode listName="non-publication-justification">fair-comp</cbc:ReasonCode>
                                    </efac:FieldsPrivacy>
                                </efac:DecisionReason>
                            </efac:LotResult>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </ContractNotice>
    """
    xml_file = tmp_path / "test_input_bt197_bt144_multiple.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert (
        len(result["withheldInformation"]) == 2
    ), f"Expected 2 withheld information items, got {len(result['withheldInformation'])}"

    expected_data = [
        {
            "id": "no-awa-rea-RES-0001",
            "code": "oth-int",
            "description": "Other public interest",
        },
        {
            "id": "no-awa-rea-RES-0002",
            "code": "fair-comp",
            "description": "Fair competition",
        },
    ]

    for withheld_info, expected in zip(
        result["withheldInformation"],
        expected_data,
        strict=False,
    ):
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
    pytest.main(["-v", "-s"])
