# tests/test_OPT_156_LotResult.py

import pytest
from ted_and_doffin_to_ocds.converters.OPT_156_LotResult import (
    parse_vehicle_numeric,
    merge_vehicle_numeric,
)
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_parse_vehicle_numeric():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <efac:NoticeResult>
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
        </efac:NoticeResult>
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


def test_merge_vehicle_numeric():
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


def test_opt_156_lotresult_vehicle_numeric_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <efac:NoticeResult>
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
        </efac:NoticeResult>
    </root>
    """
    xml_file = tmp_path / "test_input_vehicle_numeric.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

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
    pytest.main()
