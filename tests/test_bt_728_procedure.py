# tests/test_bt_728_procedure.py
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
    configure_logging()
    return logging.getLogger(__name__)


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


def run_main_and_get_result(xml_file, output_dir):
    main(str(xml_file), str(output_dir), "ocds-test-prefix")
    output_files = list(output_dir.glob("*_release_*.json"))
    assert len(output_files) > 0, "No output files generated"
    with output_files[0].open() as f:
        return json.load(f)


@pytest.mark.parametrize(
    ("xml_content", "expected_descriptions"),
    [
        # Basic case
        (
            """<?xml version="1.0" encoding="UTF-8"?>
            <ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
                  xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
                  xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
                <cac:ProcurementProject>
                    <cac:RealizedLocation>
                        <cbc:Description>Further realizations ...</cbc:Description>
                    </cac:RealizedLocation>
                </cac:ProcurementProject>
            </ContractNotice>
            """,
            ["Further realizations ..."],
        ),
        # Multiple locations
        (
            """<?xml version="1.0" encoding="UTF-8"?>
            <ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
                  xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
                  xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
                <cac:ProcurementProject>
                    <cac:RealizedLocation>
                        <cbc:Description>Location 1</cbc:Description>
                    </cac:RealizedLocation>
                    <cac:RealizedLocation>
                        <cbc:Description>Location 2</cbc:Description>
                    </cac:RealizedLocation>
                </cac:ProcurementProject>
            </ContractNotice>
            """,
            ["Location 1", "Location 2"],
        ),
        # Empty case
        (
            """<?xml version="1.0" encoding="UTF-8"?>
            <ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
                  xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
                  xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
                <cac:ProcurementProject/>
            </ContractNotice>
            """,
            [],
        ),
    ],
)
def test_bt_728_procedure_integration(
    xml_content, expected_descriptions, tmp_path, temp_output_dir, setup_logging
) -> None:
    """Test BT-728 Place Performance Additional Information integration"""
    logger = setup_logging

    # Write test XML file
    xml_file = tmp_path / "test_bt_728.xml"
    xml_file.write_text(xml_content)
    logger.info("Testing with XML file: %s", xml_file)

    # Process the notice
    result = run_main_and_get_result(xml_file, temp_output_dir)
    logger.info("Processing result: %s", json.dumps(result, indent=2))

    # Verify tender section exists when expected
    if expected_descriptions:
        assert "tender" in result, "Missing tender section in result"
        assert (
            "deliveryAddresses" in result["tender"]
        ), "Missing deliveryAddresses in tender"

        # Verify all descriptions are present
        actual_descriptions = [
            addr["description"] for addr in result["tender"]["deliveryAddresses"]
        ]
        assert sorted(actual_descriptions) == sorted(
            expected_descriptions
        ), f"Expected descriptions {expected_descriptions}, got {actual_descriptions}"
    else:
        assert "tender" not in result or "deliveryAddresses" not in result.get(
            "tender", {}
        ), "Should not have deliveryAddresses for empty input"


def test_bt_728_description_concatenation(tmp_path, temp_output_dir) -> None:
    """Test that descriptions are properly concatenated when addresses match"""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
              xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
              xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
            <cac:ProcurementProject>
                <cac:RealizedLocation>
                    <cbc:Description>Initial description</cbc:Description>
                </cac:RealizedLocation>
                <cac:RealizedLocation>
                    <cbc:Description>Additional info</cbc:Description>
                </cac:RealizedLocation>
            </cac:ProcurementProject>
        </ContractNotice>
    """
    xml_file = tmp_path / "test_bt_728_concat.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    assert "tender" in result
    assert "deliveryAddresses" in result["tender"]
    assert len(result["tender"]["deliveryAddresses"]) == 2

    descriptions = {
        addr["description"] for addr in result["tender"]["deliveryAddresses"]
    }
    assert "Initial description" in descriptions
    assert "Additional info" in descriptions


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
