# tests/test_bt_712a_LotResult.py

import pytest
from ted_and_doffin_to_ocds.converters.bt_712a_lotresult import (
    parse_buyer_review_complainants,
    merge_buyer_review_complainants,
)
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_parse_buyer_review_complainants():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <efac:noticeResult>
            <efac:LotResult>
                <efac:AppealRequestsStatistics>
                    <efbc:StatisticsCode listName="review-type">complainants</efbc:StatisticsCode>
                </efac:AppealRequestsStatistics>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                </efac:TenderLot>
            </efac:LotResult>
        </efac:noticeResult>
    </root>
    """

    result = parse_buyer_review_complainants(xml_content)

    assert result is not None
    assert "statistics" in result
    assert len(result["statistics"]) == 1
    assert result["statistics"][0]["measure"] == "complainants"
    assert result["statistics"][0]["relatedLot"] == "LOT-0001"


def test_merge_buyer_review_complainants():
    release_json = {
        "statistics": [
            {"id": "1", "measure": "otherMeasure", "relatedLot": "LOT-0001"},
        ],
    }

    buyer_review_complainants_data = {
        "statistics": [
            {"id": "2", "measure": "complainants", "relatedLot": "LOT-0001"},
        ],
    }

    merge_buyer_review_complainants(release_json, buyer_review_complainants_data)

    assert len(release_json["statistics"]) == 2
    assert any(
        stat["measure"] == "complainants" and stat["relatedLot"] == "LOT-0001"
        for stat in release_json["statistics"]
    )


def test_bt_712a_lotresult_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <efac:noticeResult>
            <efac:LotResult>
                <efac:AppealRequestsStatistics>
                    <efbc:StatisticsCode listName="review-type">complainants</efbc:StatisticsCode>
                </efac:AppealRequestsStatistics>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                </efac:TenderLot>
            </efac:LotResult>
        </efac:noticeResult>
    </root>
    """
    xml_file = tmp_path / "test_input_buyer_review_complainants.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "statistics" in result
    assert any(
        stat["measure"] == "complainants" and stat["relatedLot"] == "LOT-0001"
        for stat in result["statistics"]
    )


if __name__ == "__main__":
    pytest.main()
