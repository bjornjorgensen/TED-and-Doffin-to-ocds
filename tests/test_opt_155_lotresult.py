# tests/test_OPT_155_LotResult.py
import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

from src.ted_and_doffin_to_ocds.converters.eforms.opt_155_lotresult import (
    merge_vehicle_type,
    parse_vehicle_type,
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


def test_parse_vehicle_type() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <efac:noticeResult>
            <efac:LotResult>
                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                <efac:StrategicProcurement>
                    <efac:StrategicProcurementInformation>
                        <efac:ProcurementDetails>
                            <efac:StrategicProcurementStatistics>
                                <efbc:StatisticsNumeric>1</efbc:StatisticsNumeric>
                                <efbc:StatisticsCode listName="vehicles">vehicles-zero-emission</efbc:StatisticsCode>
                            </efac:StrategicProcurementStatistics>
                        </efac:ProcurementDetails>
                    </efac:StrategicProcurementInformation>
                </efac:StrategicProcurement>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                </efac:TenderLot>
            </efac:LotResult>
        </efac:noticeResult>
    </root>
    """

    result = parse_vehicle_type(xml_content)

    assert result is not None
    assert "awards" in result
    assert len(result["awards"]) == 1
    assert result["awards"][0]["id"] == "RES-0001"
    assert len(result["awards"][0]["items"]) == 1
    assert (
        result["awards"][0]["items"][0]["additionalClassifications"][0]["id"]
        == "vehicles-zero-emission"
    )
    assert result["awards"][0]["relatedLots"] == ["LOT-0001"]


def test_merge_vehicle_type() -> None:
    release_json = {
        "awards": [
            {"id": "RES-0001", "items": [{"id": "1", "description": "Existing item"}]},
        ],
    }

    vehicle_type_data = {
        "awards": [
            {
                "id": "RES-0001",
                "items": [
                    {
                        "id": "1",
                        "additionalClassifications": [
                            {
                                "scheme": "vehicles",
                                "id": "vehicles-zero-emission",
                                "description": "Vehicles zero emission",
                            },
                        ],
                    },
                ],
                "relatedLots": ["LOT-0001"],
            },
        ],
    }

    merge_vehicle_type(release_json, vehicle_type_data)

    assert len(release_json["awards"]) == 1
    assert release_json["awards"][0]["id"] == "RES-0001"
    assert len(release_json["awards"][0]["items"]) == 1
    assert "additionalClassifications" in release_json["awards"][0]["items"][0]
    assert (
        release_json["awards"][0]["items"][0]["additionalClassifications"][0]["id"]
        == "vehicles-zero-emission"
    )
    assert release_json["awards"][0]["relatedLots"] == ["LOT-0001"]


def test_opt_155_lotresult_vehicle_type_integration(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging
    xml_content = """
    <ContractNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <efac:noticeResult>
            <efac:LotResult>
                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                <efac:StrategicProcurement>
                    <efac:StrategicProcurementInformation>
                        <efac:ProcurementDetails>
                            <efac:StrategicProcurementStatistics>
                                <efbc:StatisticsNumeric>1</efbc:StatisticsNumeric>
                                <efbc:StatisticsCode listName="vehicles">vehicles-zero-emission</efbc:StatisticsCode>
                            </efac:StrategicProcurementStatistics>
                        </efac:ProcurementDetails>
                    </efac:StrategicProcurementInformation>
                </efac:StrategicProcurement>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                </efac:TenderLot>
            </efac:LotResult>
            <efac:LotResult>
                <cbc:ID schemeName="result">RES-0002</cbc:ID>
                <efac:StrategicProcurement>
                    <efac:StrategicProcurementInformation>
                        <efac:ProcurementDetails>
                            <efac:StrategicProcurementStatistics>
                                <efbc:StatisticsNumeric>1</efbc:StatisticsNumeric>
                                <efbc:StatisticsCode listName="vehicles">vehicles-clean</efbc:StatisticsCode>
                            </efac:StrategicProcurementStatistics>
                        </efac:ProcurementDetails>
                    </efac:StrategicProcurementInformation>
                </efac:StrategicProcurement>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
                </efac:TenderLot>
            </efac:LotResult>
        </efac:noticeResult>
    </ContractNotice>
    """
    xml_file = tmp_path / "test_input_vehicle_type.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)
    logger.info("Result: %s", json.dumps(result, indent=2))

    assert "awards" in result
    assert len(result["awards"]) == 2

    award_1 = next(
        (award for award in result["awards"] if award["id"] == "RES-0001"),
        None,
    )
    assert award_1 is not None
    assert len(award_1["items"]) == 1
    assert (
        award_1["items"][0]["additionalClassifications"][0]["id"]
        == "vehicles-zero-emission"
    )
    assert award_1["relatedLots"] == ["LOT-0001"]

    award_2 = next(
        (award for award in result["awards"] if award["id"] == "RES-0002"),
        None,
    )
    assert award_2 is not None
    assert len(award_2["items"]) == 1
    assert award_2["items"][0]["additionalClassifications"][0]["id"] == "vehicles-clean"
    assert award_2["relatedLots"] == ["LOT-0002"]


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
