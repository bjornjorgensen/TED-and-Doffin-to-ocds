# tests/test_BT_636_LotResult.py

import pytest
from ted_and_doffin_to_ocds.converters.BT_636_LotResult import (
    parse_irregularity_type,
    merge_irregularity_type,
    IRREGULARITY_TYPE_MAPPING,
)


def test_parse_irregularity_type():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <efac:NoticeResult>
            <efac:LotResult>
                <efac:AppealRequestsStatistics>
                    <efbc:StatisticsCode listName="irregularity-type">unj-lim-subc</efbc:StatisticsCode>
                </efac:AppealRequestsStatistics>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                </efac:TenderLot>
            </efac:LotResult>
        </efac:NoticeResult>
    </root>
    """

    result = parse_irregularity_type(xml_content)

    assert result is not None
    assert "statistics" in result
    assert len(result["statistics"]) == 1
    assert result["statistics"][0]["id"] == "1"
    assert result["statistics"][0]["measure"] == "unj-lim-subc"
    assert result["statistics"][0]["scope"] == "complaints"
    assert result["statistics"][0]["relatedLot"] == "LOT-0001"
    assert result["statistics"][0]["notes"] == IRREGULARITY_TYPE_MAPPING["unj-lim-subc"]


def test_merge_irregularity_type():
    release_json = {
        "statistics": [
            {
                "id": "1",
                "measure": "existing-measure",
                "scope": "existing-scope",
                "relatedLot": "LOT-0001",
            },
        ],
    }

    irregularity_type_data = {
        "statistics": [
            {
                "id": "1",
                "measure": "unj-lim-subc",
                "scope": "complaints",
                "relatedLot": "LOT-0001",
                "notes": IRREGULARITY_TYPE_MAPPING["unj-lim-subc"],
            },
            {
                "id": "2",
                "measure": "ab-low",
                "scope": "complaints",
                "relatedLot": "LOT-0002",
                "notes": IRREGULARITY_TYPE_MAPPING["ab-low"],
            },
        ],
    }

    merge_irregularity_type(release_json, irregularity_type_data)

    assert len(release_json["statistics"]) == 2
    assert release_json["statistics"][0]["measure"] == "unj-lim-subc"
    assert release_json["statistics"][0]["scope"] == "complaints"
    assert (
        release_json["statistics"][0]["notes"]
        == IRREGULARITY_TYPE_MAPPING["unj-lim-subc"]
    )
    assert release_json["statistics"][1]["id"] == "2"
    assert release_json["statistics"][1]["measure"] == "ab-low"
    assert release_json["statistics"][1]["notes"] == IRREGULARITY_TYPE_MAPPING["ab-low"]


if __name__ == "__main__":
    pytest.main()
