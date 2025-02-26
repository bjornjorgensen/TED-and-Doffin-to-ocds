# tests/test_bt_726_part.py
import json
import sys
import tempfile
from pathlib import Path

import pytest

from src.ted_and_doffin_to_ocds.converters.eforms.bt_726_part import (
    merge_part_sme_suitability,
    parse_part_sme_suitability,
)

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main

TEST_NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


@pytest.fixture
def sample_xml_true() -> str:
    """XML with SME suitability set to true."""
    return """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
          xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:ProcurementProject>
                <cbc:SMESuitableIndicator>true</cbc:SMESuitableIndicator>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </ContractNotice>
    """


@pytest.fixture
def sample_xml_false() -> str:
    """XML with SME suitability set to false."""
    return """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
          xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:ProcurementProject>
                <cbc:SMESuitableIndicator>false</cbc:SMESuitableIndicator>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </ContractNotice>
    """


def run_main_and_get_result(xml_file, output_dir):
    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    output_files = list(output_dir.glob("*.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_726_part_integration(tmp_path, temp_output_dir) -> None:
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
          xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="part">PART-0001</cbc:ID>
            <cac:ProcurementProject>
                <cbc:SMESuitableIndicator>true</cbc:SMESuitableIndicator>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </ContractNotice>
    """
    xml_file = tmp_path / "test_input_part_sme_suitability.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    assert "tender" in result, "Expected 'tender' in result"


def test_parse_part_sme_suitability_true(sample_xml_true) -> None:
    """Test parsing when SME suitability is true."""
    result = parse_part_sme_suitability(sample_xml_true)
    assert result is not None
    assert result["tender"]["suitability"]["sme"] is True


def test_parse_part_sme_suitability_false(sample_xml_false) -> None:
    """Test parsing when SME suitability is false."""
    result = parse_part_sme_suitability(sample_xml_false)
    assert result is not None
    assert result["tender"]["suitability"]["sme"] is False


def test_parse_part_sme_suitability_missing() -> None:
    """Test parsing when SME suitability indicator is missing."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
          xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:ProcurementProject>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </ContractNotice>
    """
    result = parse_part_sme_suitability(xml_content)
    assert result is None


def test_merge_part_sme_suitability() -> None:
    """Test merging SME suitability data into release JSON."""
    release_json = {}
    part_sme_data = {"tender": {"suitability": {"sme": True}}}

    merge_part_sme_suitability(release_json, part_sme_data)

    assert "tender" in release_json
    assert "suitability" in release_json["tender"]
    assert "sme" in release_json["tender"]["suitability"]
    assert release_json["tender"]["suitability"]["sme"] is True


def test_merge_part_sme_suitability_none() -> None:
    """Test merging when no SME suitability data is provided."""
    release_json = {}
    merge_part_sme_suitability(release_json, None)
    assert release_json == {}


def test_merge_part_sme_suitability_existing() -> None:
    """Test merging when release JSON already has some data."""
    release_json = {"tender": {"suitability": {"other": "value"}}}
    part_sme_data = {"tender": {"suitability": {"sme": True}}}

    merge_part_sme_suitability(release_json, part_sme_data)

    assert release_json["tender"]["suitability"]["other"] == "value"
    assert release_json["tender"]["suitability"]["sme"] is True


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
