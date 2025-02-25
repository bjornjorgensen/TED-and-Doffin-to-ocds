# tests/test_bt_539_LotsGroup.py
import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import configure_logging, main
from src.ted_and_doffin_to_ocds.converters.eforms.bt_539_lotsgroup import (
    merge_award_criterion_type_lots_group,
    parse_award_criterion_type_lots_group,
)


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


def test_parse_award_criterion_type_lots_group() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="LotsGroup">GLO-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:AwardingTerms>
                    <cac:AwardingCriterion>
                        <cac:SubordinateAwardingCriterion>
                            <cbc:AwardingCriterionTypeCode listName="award-criterion-type">quality</cbc:AwardingCriterionTypeCode>
                        </cac:SubordinateAwardingCriterion>
                    </cac:AwardingCriterion>
                </cac:AwardingTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_award_criterion_type_lots_group(xml_content)

    assert result is not None
    assert "tender" in result
    assert "lotGroups" in result["tender"]
    assert len(result["tender"]["lotGroups"]) == 1

    lot_group = result["tender"]["lotGroups"][0]
    assert lot_group["id"] == "GLO-0001"
    assert "awardCriteria" in lot_group
    assert "criteria" in lot_group["awardCriteria"]
    assert len(lot_group["awardCriteria"]["criteria"]) == 1
    assert lot_group["awardCriteria"]["criteria"][0]["type"] == "quality"


def test_merge_award_criterion_type_lots_group() -> None:
    release_json = {
        "tender": {
            "lotGroups": [
                {"id": "GLO-0001", "awardCriteria": {"criteria": [{"type": "price"}]}},
            ],
        },
    }

    award_criterion_type_data = {
        "tender": {
            "lotGroups": [
                {
                    "id": "GLO-0001",
                    "awardCriteria": {"criteria": [{"type": "quality"}]},
                },
                {"id": "GLO-0002", "awardCriteria": {"criteria": [{"type": "cost"}]}},
            ],
        },
    }

    merge_award_criterion_type_lots_group(release_json, award_criterion_type_data)

    assert len(release_json["tender"]["lotGroups"]) == 2

    lot_group1 = release_json["tender"]["lotGroups"][0]
    assert lot_group1["id"] == "GLO-0001"
    assert len(lot_group1["awardCriteria"]["criteria"]) == 2
    assert {"type": "price"} in lot_group1["awardCriteria"]["criteria"]
    assert {"type": "quality"} in lot_group1["awardCriteria"]["criteria"]

    lot_group2 = release_json["tender"]["lotGroups"][1]
    assert lot_group2["id"] == "GLO-0002"
    assert len(lot_group2["awardCriteria"]["criteria"]) == 1
    assert lot_group2["awardCriteria"]["criteria"][0]["type"] == "cost"


def test_bt_539_lots_group_integration(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="LotsGroup">GLO-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:AwardingTerms>
                    <cac:AwardingCriterion>
                        <cac:SubordinateAwardingCriterion>
                            <cbc:AwardingCriterionTypeCode listName="award-criterion-type">quality</cbc:AwardingCriterionTypeCode>
                        </cac:SubordinateAwardingCriterion>
                    </cac:AwardingCriterion>
                </cac:AwardingTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """
    xml_file = tmp_path / "test_input_bt_539_lots_group.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    logger.info("Test result: %s", json.dumps(result, indent=2))

    # Verify the results
    assert "tender" in result
    assert "lotGroups" in result["tender"]
    assert len(result["tender"]["lotGroups"]) == 1

    lot_group = result["tender"]["lotGroups"][0]
    assert lot_group["id"] == "GLO-0001"
    assert "awardCriteria" in lot_group
    assert "criteria" in lot_group["awardCriteria"]
    assert len(lot_group["awardCriteria"]["criteria"]) == 1
    assert lot_group["awardCriteria"]["criteria"][0]["type"] == "quality"


if __name__ == "__main__":
    pytest.main(["-v"])
