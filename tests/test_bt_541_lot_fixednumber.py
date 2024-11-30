# tests/test_bt_541_lot_fixednumber.py
import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import configure_logging, main
from ted_and_doffin_to_ocds.converters.bt_541_lot_fixednumber import (
    merge_award_criterion_fixed_number,
    parse_award_criterion_fixed_number,
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


def test_parse_award_criterion_fixed_number() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:AwardingTerms>
                    <cac:AwardingCriterion>
                        <cac:SubordinateAwardingCriterion>
                            <ext:UBLExtensions>
                                <ext:UBLExtension>
                                    <ext:ExtensionContent>
                                        <efext:EformsExtension>
                                            <efac:AwardCriterionParameter>
                                                <efbc:ParameterCode listName="number-fixed"/>
                                                <efbc:ParameterNumeric>50</efbc:ParameterNumeric>
                                            </efac:AwardCriterionParameter>
                                        </efext:EformsExtension>
                                    </ext:ExtensionContent>
                                </ext:UBLExtension>
                            </ext:UBLExtensions>
                        </cac:SubordinateAwardingCriterion>
                    </cac:AwardingCriterion>
                </cac:AwardingTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_award_criterion_fixed_number(xml_content)

    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1

    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001"
    assert "awardCriteria" in lot
    assert "criteria" in lot["awardCriteria"]
    assert len(lot["awardCriteria"]["criteria"]) == 1
    assert "numbers" in lot["awardCriteria"]["criteria"][0]
    assert len(lot["awardCriteria"]["criteria"][0]["numbers"]) == 1
    assert lot["awardCriteria"]["criteria"][0]["numbers"][0]["number"] == 50.0


def test_merge_award_criterion_fixed_number() -> None:
    release_json = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "awardCriteria": {
                        "criteria": [{"description": "Quality criterion"}],
                    },
                },
            ],
        },
    }

    award_criterion_fixed_number_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "awardCriteria": {"criteria": [{"numbers": [{"number": 50.0}]}]},
                },
                {
                    "id": "LOT-0002",
                    "awardCriteria": {"criteria": [{"numbers": [{"number": 75.0}]}]},
                },
            ],
        },
    }

    merge_award_criterion_fixed_number(release_json, award_criterion_fixed_number_data)

    assert len(release_json["tender"]["lots"]) == 2

    lot1 = release_json["tender"]["lots"][0]
    assert lot1["id"] == "LOT-0001"
    assert len(lot1["awardCriteria"]["criteria"]) == 1
    assert "description" in lot1["awardCriteria"]["criteria"][0]
    assert "numbers" in lot1["awardCriteria"]["criteria"][0]
    assert len(lot1["awardCriteria"]["criteria"][0]["numbers"]) == 1
    assert lot1["awardCriteria"]["criteria"][0]["numbers"][0]["number"] == 50.0

    lot2 = release_json["tender"]["lots"][1]
    assert lot2["id"] == "LOT-0002"
    assert len(lot2["awardCriteria"]["criteria"]) == 1
    assert "numbers" in lot2["awardCriteria"]["criteria"][0]
    assert len(lot2["awardCriteria"]["criteria"][0]["numbers"]) == 1
    assert lot2["awardCriteria"]["criteria"][0]["numbers"][0]["number"] == 75.0


def test_bt_541_lot_fixed_number_integration(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
        xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:AwardingTerms>
                    <cac:AwardingCriterion>
                        <cac:SubordinateAwardingCriterion>
                            <ext:UBLExtensions>
                                <ext:UBLExtension>
                                    <ext:ExtensionContent>
                                        <efext:EformsExtension>
                                            <efac:AwardCriterionParameter>
                                                <efbc:ParameterCode listName="number-fixed"/>
                                                <efbc:ParameterNumeric>50</efbc:ParameterNumeric>
                                            </efac:AwardCriterionParameter>
                                        </efext:EformsExtension>
                                    </ext:ExtensionContent>
                                </ext:UBLExtension>
                            </ext:UBLExtensions>
                        </cac:SubordinateAwardingCriterion>
                    </cac:AwardingCriterion>
                </cac:AwardingTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """
    xml_file = tmp_path / "test_input_bt_541_lot_fixed_number.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    logger.info("Test result: %s", json.dumps(result, indent=2))

    # Verify the results
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1

    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001"
    assert "awardCriteria" in lot
    assert "criteria" in lot["awardCriteria"]
    assert len(lot["awardCriteria"]["criteria"]) == 1
    assert "numbers" in lot["awardCriteria"]["criteria"][0]
    assert len(lot["awardCriteria"]["criteria"][0]["numbers"]) == 1
    assert lot["awardCriteria"]["criteria"][0]["numbers"][0]["number"] == 50.0


if __name__ == "__main__":
    pytest.main(["-v"])
