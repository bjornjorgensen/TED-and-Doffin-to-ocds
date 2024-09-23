# tests/test_OPT_155_LotResult.py

import pytest
from ted_and_doffin_to_ocds.converters.opt_155_lotresult import (
    parse_vehicle_type,
    merge_vehicle_type,
)
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_parse_vehicle_type():
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


def test_merge_vehicle_type():
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


def test_opt_155_lotresult_vehicle_type_integration(tmp_path):
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
    </root>
    """
    xml_file = tmp_path / "test_input_vehicle_type.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

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
    pytest.main()
