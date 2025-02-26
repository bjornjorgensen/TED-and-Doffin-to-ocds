# tests/test_OPT_156_LotResult.py
import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

from src.ted_and_doffin_to_ocds.converters.eforms.opt_156_lotresult import (
    merge_vehicle_numeric,
    parse_vehicle_numeric,
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


def test_parse_vehicle_numeric() -> None:
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
                                <efbc:StatisticsNumeric>10</efbc:StatisticsNumeric>
                                <efbc:StatisticsCode>vehicles</efbc:StatisticsCode>
                            </efac:StrategicProcurementStatistics>
                            <efac:StrategicProcurementStatistics>
                                <efbc:StatisticsNumeric>3</efbc:StatisticsNumeric>
                                <efbc:StatisticsCode>vehicles-zero-emission</efbc:StatisticsCode>
                            </efac:StrategicProcurementStatistics>
                            <efac:StrategicProcurementStatistics>
                                <efbc:StatisticsNumeric>2</efbc:StatisticsNumeric>
                                <efbc:StatisticsCode>vehicles-clean</efbc:StatisticsCode>
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

    result = parse_vehicle_numeric(xml_content)

    assert result is not None
    assert "awards" in result
    assert len(result["awards"]) == 1
    assert result["awards"][0]["id"] == "RES-0001"
    assert len(result["awards"][0]["items"]) == 3
    assert result["awards"][0]["items"][0]["quantity"] == 3
    assert result["awards"][0]["items"][1]["quantity"] == 2
    assert result["awards"][0]["items"][2]["quantity"] == 5
    assert result["awards"][0]["relatedLots"] == ["LOT-0001"]


def test_merge_vehicle_numeric() -> None:
    release_json = {
        "awards": [
            {"id": "RES-0001", "items": [{"id": "1", "description": "Existing item"}]},
        ],
    }

    vehicle_numeric_data = {
        "awards": [
            {
                "id": "RES-0001",
                "items": [
                    {
                        "id": "1",
                        "quantity": 3,
                        "classification": {
                            "scheme": "vehicles",
                            "id": "vehicles-zero-emission",
                            "description": "Vehicles Zero Emission",
                        },
                    },
                    {
                        "id": "2",
                        "quantity": 2,
                        "classification": {
                            "scheme": "vehicles",
                            "id": "vehicles-clean",
                            "description": "Vehicles Clean",
                        },
                    },
                ],
                "relatedLots": ["LOT-0001"],
            },
        ],
    }

    merge_vehicle_numeric(release_json, vehicle_numeric_data)

    assert len(release_json["awards"]) == 1
    assert release_json["awards"][0]["id"] == "RES-0001"
    assert len(release_json["awards"][0]["items"]) == 2
    assert release_json["awards"][0]["items"][0]["quantity"] == 3
    assert release_json["awards"][0]["items"][1]["quantity"] == 2
    assert release_json["awards"][0]["relatedLots"] == ["LOT-0001"]


def test_opt_156_lotresult_vehicle_numeric_integration(
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
                                <efbc:StatisticsNumeric>10</efbc:StatisticsNumeric>
                                <efbc:StatisticsCode>vehicles</efbc:StatisticsCode>
                            </efac:StrategicProcurementStatistics>
                            <efac:StrategicProcurementStatistics>
                                <efbc:StatisticsNumeric>3</efbc:StatisticsNumeric>
                                <efbc:StatisticsCode>vehicles-zero-emission</efbc:StatisticsCode>
                            </efac:StrategicProcurementStatistics>
                            <efac:StrategicProcurementStatistics>
                                <efbc:StatisticsNumeric>2</efbc:StatisticsNumeric>
                                <efbc:StatisticsCode>vehicles-clean</efbc:StatisticsCode>
                            </efac:StrategicProcurementStatistics>
                        </efac:ProcurementDetails>
                    </efac:StrategicProcurementInformation>
                </efac:StrategicProcurement>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                </efac:TenderLot>
            </efac:LotResult>
        </efac:noticeResult>
    </ContractNotice>
    """
    xml_file = tmp_path / "test_input_vehicle_numeric.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)
    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    assert "awards" in result
    assert len(result["awards"]) == 1

    award = result["awards"][0]
    assert award["id"] == "RES-0001"
    assert len(award["items"]) == 3

    zero_emission = next(
        item
        for item in award["items"]
        if item["classification"]["id"] == "vehicles-zero-emission"
    )
    assert zero_emission["quantity"] == 3

    clean = next(
        item
        for item in award["items"]
        if item["classification"]["id"] == "vehicles-clean"
    )
    assert clean["quantity"] == 2

    regular = next(
        item for item in award["items"] if item["classification"]["id"] == "vehicles"
    )
    assert regular["quantity"] == 5

    assert award["relatedLots"] == ["LOT-0001"]


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
