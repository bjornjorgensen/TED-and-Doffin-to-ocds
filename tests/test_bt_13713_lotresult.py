# tests/test_bt_13713_LotResult.py
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest
from lxml import etree

from ted_and_doffin_to_ocds.converters.eforms.bt_13713_lotresult import (
    parse_lot_result_identifier,
    merge_lot_result_identifier,
)

# Import main module
from ted_and_doffin_to_ocds.main import main


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


def run_main_and_get_result(xml_file, output_dir):
    """Run main function and return the parsed output JSON."""
    ocid_prefix = "ocds-test-prefix"
    organization_scheme = "test-scheme"
    
    main(str(xml_file), str(output_dir), ocid_prefix, organization_scheme)
    
    # Find and read the output file
    output_files = list(output_dir.glob("*.json"))
    assert len(output_files) > 0, f"No output files found in {output_dir}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_13713_lotresult_integration(tmp_path, temp_output_dir) -> None:
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                                </efac:TenderLot>
                            </efac:LotResult>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0002</cbc:ID>
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
                                </efac:TenderLot>
                            </efac:LotResult>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0002</cbc:ID>
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0003</cbc:ID>
                                </efac:TenderLot>
                            </efac:LotResult>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </ContractAwardNotice>
    """
    xml_file = tmp_path / "test_input_result_lot_identifier.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    assert "awards" in result, "Expected 'awards' in result"
    assert len(result["awards"]) == 2, f"Expected 2 awards, got {len(result['awards'])}"

    award_1 = next(award for award in result["awards"] if award["id"] == "RES-0001")
    assert "relatedLots" in award_1, "Expected 'relatedLots' in award RES-0001"
    assert award_1["relatedLots"] == [
        "LOT-0001",
    ], f"Expected ['LOT-0001'] in RES-0001 relatedLots, got {award_1['relatedLots']}"

    award_2 = next(award for award in result["awards"] if award["id"] == "RES-0002")
    assert "relatedLots" in award_2, "Expected 'relatedLots' in award RES-0002"
    assert (
        set(award_2["relatedLots"]) == {"LOT-0002", "LOT-0003"}
    ), f"Expected ['LOT-0002', 'LOT-0003'] in RES-0002 relatedLots, got {award_2['relatedLots']}"


def create_xml_with_lot_result(award_id="RES-0002", lot_id="LOT-0001") -> str:
    """Create test XML with lot result data."""
    lot_element = ""
    if lot_id:
        lot_element = f'<efac:TenderLot><cbc:ID schemeName="Lot">{lot_id}</cbc:ID></efac:TenderLot>'

    return f"""
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">{award_id}</cbc:ID>
                                {lot_element}
                            </efac:LotResult>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """


def test_parse_valid_lot_result_identifier():
    """Test parsing a valid lot result identifier."""
    xml = create_xml_with_lot_result("RES-0002", "LOT-0001")
    result = parse_lot_result_identifier(xml)

    assert result is not None
    assert len(result["awards"]) == 1
    assert result["awards"][0]["id"] == "RES-0002"
    assert result["awards"][0]["relatedLots"] == ["LOT-0001"]


def test_parse_invalid_lot_id_pattern():
    """Test parsing with an invalid lot ID pattern."""
    xml = create_xml_with_lot_result("RES-0002", "LOT-123")  # Invalid format
    result = parse_lot_result_identifier(xml)

    # Should still parse, but log a warning
    assert result is not None
    assert len(result["awards"]) == 1
    assert result["awards"][0]["relatedLots"] == ["LOT-123"]


def test_parse_missing_lot_id():
    """Test parsing with no lot ID - should use default."""
    xml = create_xml_with_lot_result("RES-0002", None)
    result = parse_lot_result_identifier(xml)

    assert result is not None
    assert len(result["awards"]) == 1
    assert result["awards"][0]["relatedLots"] == ["LOT-0001"]


def test_parse_missing_award_id():
    """Test missing award ID - should skip this entry."""
    xml = create_xml_with_lot_result(None, "LOT-0001")
    result = parse_lot_result_identifier(xml)

    # No valid award entries should be found since award_id is None
    assert result is None


def test_parse_multiple_lot_results():
    """Test parsing multiple lot results."""
    xml = f"""
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                                <efac:TenderLot><cbc:ID schemeName="Lot">LOT-0001</cbc:ID></efac:TenderLot>
                            </efac:LotResult>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0002</cbc:ID>
                                <efac:TenderLot><cbc:ID schemeName="Lot">LOT-0002</cbc:ID></efac:TenderLot>
                            </efac:LotResult>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    result = parse_lot_result_identifier(xml)

    assert result is not None
    assert len(result["awards"]) == 2
    assert result["awards"][0]["id"] == "RES-0001"
    assert result["awards"][0]["relatedLots"] == ["LOT-0001"]
    assert result["awards"][1]["id"] == "RES-0002"
    assert result["awards"][1]["relatedLots"] == ["LOT-0002"]


def test_merge_new_lot_result():
    """Test merging lot result data into empty release."""
    release_json = {}
    lot_result_data = {
        "awards": [
            {"id": "RES-0001", "relatedLots": ["LOT-0001"]},
            {"id": "RES-0002", "relatedLots": ["LOT-0002"]},
        ]
    }

    merge_lot_result_identifier(release_json, lot_result_data)

    assert len(release_json["awards"]) == 2
    assert release_json["awards"][0]["id"] == "RES-0001"
    assert release_json["awards"][0]["relatedLots"] == ["LOT-0001"]
    assert release_json["awards"][1]["id"] == "RES-0002"
    assert release_json["awards"][1]["relatedLots"] == ["LOT-0002"]


def test_merge_with_existing_awards():
    """Test merging lot result data into release with existing awards."""
    release_json = {
        "awards": [
            {"id": "RES-0001", "relatedLots": ["LOT-0001"]},
            {"id": "RES-0003", "value": {"amount": 100000}},
        ]
    }
    lot_result_data = {
        "awards": [
            {"id": "RES-0001", "relatedLots": ["LOT-0002"]},
            {"id": "RES-0002", "relatedLots": ["LOT-0003"]},
        ]
    }

    merge_lot_result_identifier(release_json, lot_result_data)

    # Should have 3 awards total
    assert len(release_json["awards"]) == 3

    # RES-0001 should have both LOT-0001 and LOT-0002
    award1 = next(a for a in release_json["awards"] if a["id"] == "RES-0001")
    assert sorted(award1["relatedLots"]) == ["LOT-0001", "LOT-0002"]

    # RES-0002 should be added with LOT-0003
    award2 = next(a for a in release_json["awards"] if a["id"] == "RES-0002")
    assert award2["relatedLots"] == ["LOT-0003"]

    # RES-0003 should remain unchanged
    award3 = next(a for a in release_json["awards"] if a["id"] == "RES-0003")
    assert award3["value"]["amount"] == 100000
    assert "relatedLots" not in award3 or award3["relatedLots"] == []


def test_merge_with_none_data():
    """Test merging with None data should not modify the release."""
    release_json = {"awards": [{"id": "RES-0001"}]}
    merge_lot_result_identifier(release_json, None)

    # Release should remain unchanged
    assert len(release_json["awards"]) == 1
    assert release_json["awards"][0]["id"] == "RES-0001"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
