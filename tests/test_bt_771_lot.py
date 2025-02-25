# tests/test_bt_771_Lot.py
import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

from src.ted_and_doffin_to_ocds.converters.eforms.bt_771_lot import (
    merge_late_tenderer_info,
    parse_late_tenderer_info,
)

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
    logging.info(
        "Running main with xml_file: %s and output_dir: %s", xml_file, output_dir
    )
    try:
        main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
        logging.info("main() executed successfully.")
    except Exception:
        logging.exception("Exception occurred while running main():")
        raise

    output_files = list(output_dir.glob("*.json"))
    logging.info("Output files found: %s", output_files)
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_parse_late_tenderer_info() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:TendererQualificationRequest>
                    <cac:SpecificTendererRequirement>
                        <cbc:TendererRequirementTypeCode listName="missing-info-submission">late-all</cbc:TendererRequirementTypeCode>
                    </cac:SpecificTendererRequirement>
                </cac:TendererQualificationRequest>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_late_tenderer_info(xml_content)

    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert "submissionMethodDetails" in result["tender"]["lots"][0]
    assert (
        "all missing tenderer-related documents may be submitted later"
        in result["tender"]["lots"][0]["submissionMethodDetails"]
    )


def test_merge_late_tenderer_info() -> None:
    release_json = {"tender": {"lots": [{"id": "LOT-0001", "title": "Existing Lot"}]}}

    late_tenderer_info = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "submissionMethodDetails": "At the discretion of the buyer, all missing tenderer-related documents may be submitted later.",
                },
            ],
        },
    }

    merge_late_tenderer_info(release_json, late_tenderer_info)

    assert "submissionMethodDetails" in release_json["tender"]["lots"][0]
    assert (
        "all missing tenderer-related documents may be submitted later"
        in release_json["tender"]["lots"][0]["submissionMethodDetails"]
    )


def test_bt_771_lot_late_tenderer_info_integration(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging
    xml_content = """
    <ContractNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:TendererQualificationRequest>
                    <cac:SpecificTendererRequirement>
                        <cbc:TendererRequirementTypeCode listName="missing-info-submission">late-all</cbc:TendererRequirementTypeCode>
                    </cac:SpecificTendererRequirement>
                </cac:TendererQualificationRequest>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:TenderingTerms>
                <cac:TendererQualificationRequest>
                    <cac:SpecificTendererRequirement>
                        <cbc:TendererRequirementTypeCode listName="missing-info-submission">late-none</cbc:TendererRequirementTypeCode>
                    </cac:SpecificTendererRequirement>
                </cac:TendererQualificationRequest>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0003</cbc:ID>
            <cac:TenderingTerms>
                <cac:TendererQualificationRequest>
                    <cac:SpecificTendererRequirement>
                        <cbc:TendererRequirementTypeCode listName="other-requirement">not-late-info</cbc:TendererRequirementTypeCode>
                    </cac:SpecificTendererRequirement>
                </cac:TendererQualificationRequest>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </ContractNotice>
    """
    xml_file = tmp_path / "test_input_late_tenderer_info.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)
    logger.info("Result: %s", json.dumps(result, indent=2))

    assert "tender" in result
    assert "lots" in result["tender"]

    lots_with_info = [
        lot for lot in result["tender"]["lots"] if "submissionMethodDetails" in lot
    ]
    assert len(lots_with_info) == 2

    lot_1 = next((lot for lot in lots_with_info if lot["id"] == "LOT-0001"), None)
    assert lot_1 is not None
    assert (
        "all missing tenderer-related documents may be submitted later"
        in lot_1["submissionMethodDetails"]
    )

    lot_2 = next((lot for lot in lots_with_info if lot["id"] == "LOT-0002"), None)
    assert lot_2 is not None
    assert "No documents can be submitted later" in lot_2["submissionMethodDetails"]

    lot_3 = next(
        (lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0003"),
        None,
    )
    assert lot_3 is not None
    assert "submissionMethodDetails" not in lot_3


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
