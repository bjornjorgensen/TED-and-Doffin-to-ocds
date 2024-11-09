# tests/test_bt_762_ChangeReasonDescription.py
from pathlib import Path
import pytest
import json
import sys
import tempfile
import logging

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main, configure_logging


@pytest.fixture(scope="module")
def setup_logging():
    configure_logging()
    return logging.getLogger(__name__)


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


def run_main_and_get_result(xml_file, output_dir):
    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    output_files = list(output_dir.glob("*_release_0.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_762_change_reason_description_integration(
    tmp_path, setup_logging, temp_output_dir
):
    logger = setup_logging

    xml_content = """
    <ContractAwardNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
                          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
                          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
                          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
                          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
                          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:Changes>
                            <efac:ChangeReason>
                                <efbc:ReasonDescription languageID="ENG">Clerical corrections of ...</efbc:ReasonDescription>
                            </efac:ChangeReason>
                            <efac:ChangeReason>
                                <efbc:ReasonDescription languageID="ENG">Additional information added</efbc:ReasonDescription>
                            </efac:ChangeReason>
                        </efac:Changes>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </ContractAwardNotice>
    """
    xml_file = tmp_path / "test_input_change_reason_description.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)
    logger.info("Result: %s", json.dumps(result, indent=2))

    assert "tender" in result, "Expected 'tender' in result"
    assert "amendments" in result["tender"], "Expected 'amendments' in tender"
    assert (
        len(result["tender"]["amendments"]) == 2
    ), f"Expected 2 amendments, got {len(result['tender']['amendments'])}"

    amendment1 = result["tender"]["amendments"][0]
    amendment2 = result["tender"]["amendments"][1]

    assert "rationale" in amendment1, "Expected 'rationale' in first amendment"
    assert "rationale" in amendment2, "Expected 'rationale' in second amendment"
    assert (
        amendment1["rationale"] == "Clerical corrections of ..."
    ), f"Expected 'Clerical corrections of ...' for first amendment, got {amendment1['rationale']}"
    assert (
        amendment2["rationale"] == "Additional information added"
    ), f"Expected 'Additional information added' for second amendment, got {amendment2['rationale']}"

    logger.info(
        "Test bt_762_change_reason_description_integration passed successfully."
    )


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
