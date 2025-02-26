# tests/test_bt_539_lot.py
import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import configure_logging, main
from src.ted_and_doffin_to_ocds.converters.eforms.bt_539_lot import (
    merge_award_criterion_type,
    parse_award_criterion_type,
)


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
    output_files = list(output_dir.glob("*_release_0.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_parse_award_criterion_type() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
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

    result = parse_award_criterion_type(xml_content)

    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1

    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001"
    assert "awardCriteria" in lot
    assert "criteria" in lot["awardCriteria"]
    assert len(lot["awardCriteria"]["criteria"]) == 1
    assert lot["awardCriteria"]["criteria"][0]["type"] == "quality"


def test_merge_award_criterion_type() -> None:
    release_json = {
        "tender": {
            "lots": [
                {"id": "LOT-0001", "awardCriteria": {"criteria": [{"type": "price"}]}},
            ],
        },
    }

    award_criterion_type_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "awardCriteria": {"criteria": [{"type": "quality"}]},
                },
                {"id": "LOT-0002", "awardCriteria": {"criteria": [{"type": "cost"}]}},
            ],
        },
    }

    merge_award_criterion_type(release_json, award_criterion_type_data)

    assert len(release_json["tender"]["lots"]) == 2

    lot1 = release_json["tender"]["lots"][0]
    assert lot1["id"] == "LOT-0001"
    assert len(lot1["awardCriteria"]["criteria"]) == 2
    assert {"type": "price"} in lot1["awardCriteria"]["criteria"]
    assert {"type": "quality"} in lot1["awardCriteria"]["criteria"]

    lot2 = release_json["tender"]["lots"][1]
    assert lot2["id"] == "LOT-0002"
    assert len(lot2["awardCriteria"]["criteria"]) == 1
    assert lot2["awardCriteria"]["criteria"][0]["type"] == "cost"


def test_bt_539_lot_integration(tmp_path, setup_logging, temp_output_dir) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
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
    xml_file = tmp_path / "test_input_bt_539_lot.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # logger.info("Test result: %s", json.dumps(result, indent=2) # Logging disabled)

    # Verify the results
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1

    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001"
    assert "awardCriteria" in lot
    assert "criteria" in lot["awardCriteria"]
    assert len(lot["awardCriteria"]["criteria"]) == 1
    assert lot["awardCriteria"]["criteria"][0]["type"] == "quality"


if __name__ == "__main__":
    pytest.main(["-v"])
