# tests/test_bt_137_LotsGroup.py
import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import configure_logging, main
from src.ted_and_doffin_to_ocds.converters.eforms.bt_137_lotsgroup import parse_lots_group_identifier, merge_lots_group_identifier


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


def test_bt_137_lots_group_integration(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="LotsGroup">GLO-0001</cbc:ID>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="LotsGroup">GLO-0002</cbc:ID>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_lots_group_identifier.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)
    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    # Verify the results
    assert "tender" in result, "Expected 'tender' in result"
    assert "lotGroups" in result["tender"], "Expected 'lotGroups' in tender"

    lot_groups = result["tender"]["lotGroups"]
    assert len(lot_groups) == 2, f"Expected 2 unique lot groups, got {len(lot_groups)}"
    assert {"id": "GLO-0001"} in lot_groups, "Expected lot group with id 'GLO-0001'"
    assert {"id": "GLO-0002"} in lot_groups, "Expected lot group with id 'GLO-0002'"


def test_parse_lots_group_identifier() -> None:
    """Test parsing of lot group identifiers."""
    # Valid XML with lot groups
    valid_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="LotsGroup">GLO-0001</cbc:ID>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="LotsGroup">GLO-9999</cbc:ID>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="LotsGroup">LOT-0001</cbc:ID>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """
    result = parse_lots_group_identifier(valid_xml)
    assert result is not None
    assert len(result["tender"]["lotGroups"]) == 3
    assert {"id": "GLO-0001"} in result["tender"]["lotGroups"]
    assert {"id": "GLO-9999"} in result["tender"]["lotGroups"]
    assert {"id": "LOT-0001"} in result["tender"]["lotGroups"]

    # XML with no lot groups
    no_lots_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">L1</cbc:ID>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """
    result = parse_lots_group_identifier(no_lots_xml)
    assert result is None, "Expected None when no LotsGroup identifiers are found"


def test_merge_lots_group_identifier() -> None:
    """Test merging lot group identifiers into existing release data."""
    # Test merging with empty release
    release_json = {}
    lots_group_data = {
        "tender": {
            "lotGroups": [
                {"id": "GLO-0001"},
                {"id": "GLO-0002"}
            ]
        }
    }
    merge_lots_group_identifier(release_json, lots_group_data)
    assert "tender" in release_json
    assert "lotGroups" in release_json["tender"]
    assert len(release_json["tender"]["lotGroups"]) == 2
    
    # Test merging with existing data (should not duplicate)
    release_json = {
        "tender": {
            "lotGroups": [
                {"id": "GLO-0001"},
                {"id": "GLO-0003"}
            ]
        }
    }
    lots_group_data = {
        "tender": {
            "lotGroups": [
                {"id": "GLO-0001"},
                {"id": "GLO-0002"}
            ]
        }
    }
    merge_lots_group_identifier(release_json, lots_group_data)
    assert len(release_json["tender"]["lotGroups"]) == 3
    assert {"id": "GLO-0001"} in release_json["tender"]["lotGroups"]
    assert {"id": "GLO-0002"} in release_json["tender"]["lotGroups"]
    assert {"id": "GLO-0003"} in release_json["tender"]["lotGroups"]
    
    # Test with None lots_group_data
    release_json = {"tender": {"lotGroups": [{"id": "GLO-0001"}]}}
    merge_lots_group_identifier(release_json, None)
    assert len(release_json["tender"]["lotGroups"]) == 1


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
