# tests/test_bt_727_part.py
import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

from src.ted_and_doffin_to_ocds.converters.eforms.bt_727_part import (
    merge_part_place_performance,
    parse_part_place_performance,
)

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


def test_parse_part_place_performance() -> None:
    """Test parsing place performance from XML."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
          xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:RealizedLocation>
                    <cac:Address>
                        <cbc:Region>anyw-eea</cbc:Region>
                    </cac:Address>
                </cac:RealizedLocation>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </ContractNotice>
    """

    result = parse_part_place_performance(xml_content)

    assert result is not None
    assert "tender" in result
    assert "deliveryLocations" in result["tender"]
    assert len(result["tender"]["deliveryLocations"]) == 1
    assert (
        result["tender"]["deliveryLocations"][0]["description"]
        == "Anywhere in the European Economic Area"
    )


def test_merge_part_place_performance() -> None:
    """Test merging place performance data into release JSON."""
    release_json = {"tender": {}}

    part_data = {
        "tender": {
            "deliveryLocations": [
                {"description": "Anywhere in the European Economic Area"}
            ]
        }
    }

    merge_part_place_performance(release_json, part_data)

    assert "deliveryLocations" in release_json["tender"]
    assert len(release_json["tender"]["deliveryLocations"]) == 1
    assert (
        release_json["tender"]["deliveryLocations"][0]["description"]
        == "Anywhere in the European Economic Area"
    )


def test_merge_multiple_locations() -> None:
    """Test merging multiple locations without duplicates."""
    release_json = {"tender": {"deliveryLocations": [{"description": "Anywhere"}]}}

    part_data = {
        "tender": {
            "deliveryLocations": [
                {"description": "Anywhere"},
                {"description": "Anywhere in the European Economic Area"},
            ]
        }
    }

    merge_part_place_performance(release_json, part_data)

    assert len(release_json["tender"]["deliveryLocations"]) == 2
    descriptions = {
        loc["description"] for loc in release_json["tender"]["deliveryLocations"]
    }
    assert descriptions == {"Anywhere", "Anywhere in the European Economic Area"}


def test_integration(tmp_path, temp_output_dir) -> None:
    """Test integration with main converter."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
          xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:RealizedLocation>
                    <cac:Address>
                        <cbc:Region>anyw-eea</cbc:Region>
                    </cac:Address>
                </cac:RealizedLocation>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </ContractNotice>
    """
    xml_file = tmp_path / "test_input.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    assert "tender" in result
    assert "deliveryLocations" in result["tender"]
    assert len(result["tender"]["deliveryLocations"]) == 1
    assert (
        result["tender"]["deliveryLocations"][0]["description"]
        == "Anywhere in the European Economic Area"
    )


def test_invalid_xml() -> None:
    """Test handling of invalid XML."""
    invalid_xml = "<invalid>"
    result = parse_part_place_performance(invalid_xml)
    assert result is None


def test_empty_regions() -> None:
    """Test handling of XML with no regions."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
          xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
        </cac:ProcurementProjectLot>
    </ContractNotice>
    """

    result = parse_part_place_performance(xml_content)
    assert result is None


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
