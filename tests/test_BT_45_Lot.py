# tests/test_bt_45_Lot.py

from lxml import etree
from ted_and_doffin_to_ocds.converters.bt_45_lot import (
    parse_lot_rewards_other,
    merge_lot_rewards_other,
)


def create_xml_root(content):
    return etree.fromstring(f"""
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        {content}
    </root>
    """)


def test_parse_lot_rewards_other_single_lot():
    xml_content = create_xml_root("""
    <cac:ProcurementProjectLot>
        <cbc:ID schemeName="Lot">LOT-001</cbc:ID>
        <cac:TenderingTerms>
            <cac:AwardingTerms>
                <cac:Prize>
                    <cbc:Description>First prize: €10,000</cbc:Description>
                </cac:Prize>
            </cac:AwardingTerms>
        </cac:TenderingTerms>
    </cac:ProcurementProjectLot>
    """)

    result = parse_lot_rewards_other(etree.tostring(xml_content))

    assert result is not None
    assert len(result["tender"]["lots"]) == 1
    assert result["tender"]["lots"][0]["id"] == "LOT-001"
    assert len(result["tender"]["lots"][0]["designContest"]["prizes"]["details"]) == 1
    assert (
        result["tender"]["lots"][0]["designContest"]["prizes"]["details"][0][
            "description"
        ]
        == "First prize: €10,000"
    )


def test_parse_lot_rewards_other_multiple_lots():
    xml_content = create_xml_root("""
    <cac:ProcurementProjectLot>
        <cbc:ID schemeName="Lot">LOT-001</cbc:ID>
        <cac:TenderingTerms>
            <cac:AwardingTerms>
                <cac:Prize>
                    <cbc:Description>First prize: €10,000</cbc:Description>
                </cac:Prize>
            </cac:AwardingTerms>
        </cac:TenderingTerms>
    </cac:ProcurementProjectLot>
    <cac:ProcurementProjectLot>
        <cbc:ID schemeName="Lot">LOT-002</cbc:ID>
        <cac:TenderingTerms>
            <cac:AwardingTerms>
                <cac:Prize>
                    <cbc:Description>Second prize: €5,000</cbc:Description>
                </cac:Prize>
            </cac:AwardingTerms>
        </cac:TenderingTerms>
    </cac:ProcurementProjectLot>
    """)

    result = parse_lot_rewards_other(etree.tostring(xml_content))

    assert result is not None
    assert len(result["tender"]["lots"]) == 2
    assert result["tender"]["lots"][0]["id"] == "LOT-001"
    assert result["tender"]["lots"][1]["id"] == "LOT-002"
    assert (
        result["tender"]["lots"][0]["designContest"]["prizes"]["details"][0][
            "description"
        ]
        == "First prize: €10,000"
    )
    assert (
        result["tender"]["lots"][1]["designContest"]["prizes"]["details"][0][
            "description"
        ]
        == "Second prize: €5,000"
    )


def test_parse_lot_rewards_other_no_prizes():
    xml_content = create_xml_root("""
    <cac:ProcurementProjectLot>
        <cbc:ID schemeName="Lot">LOT-001</cbc:ID>
        <cac:TenderingTerms>
            <cac:AwardingTerms>
            </cac:AwardingTerms>
        </cac:TenderingTerms>
    </cac:ProcurementProjectLot>
    """)

    result = parse_lot_rewards_other(etree.tostring(xml_content))

    assert result is None


def test_merge_lot_rewards_other_new_lot():
    release_json = {"tender": {"lots": []}}
    lot_rewards_other_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-001",
                    "designContest": {
                        "prizes": {
                            "details": [
                                {"id": "0", "description": "First prize: €10,000"},
                            ],
                        },
                    },
                },
            ],
        },
    }

    merge_lot_rewards_other(release_json, lot_rewards_other_data)

    assert len(release_json["tender"]["lots"]) == 1
    assert release_json["tender"]["lots"][0]["id"] == "LOT-001"
    assert (
        release_json["tender"]["lots"][0]["designContest"]["prizes"]["details"][0][
            "description"
        ]
        == "First prize: €10,000"
    )


def test_merge_lot_rewards_other_existing_lot():
    release_json = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-001",
                    "designContest": {
                        "prizes": {
                            "details": [{"id": "0", "description": "Old description"}],
                        },
                    },
                },
            ],
        },
    }
    lot_rewards_other_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-001",
                    "designContest": {
                        "prizes": {
                            "details": [
                                {"id": "0", "description": "Updated description"},
                            ],
                        },
                    },
                },
            ],
        },
    }

    merge_lot_rewards_other(release_json, lot_rewards_other_data)

    assert len(release_json["tender"]["lots"]) == 1
    assert release_json["tender"]["lots"][0]["id"] == "LOT-001"
    assert (
        release_json["tender"]["lots"][0]["designContest"]["prizes"]["details"][0][
            "description"
        ]
        == "Updated description"
    )


def test_merge_lot_rewards_other_no_data():
    release_json = {"tender": {"lots": []}}
    lot_rewards_other_data = None

    merge_lot_rewards_other(release_json, lot_rewards_other_data)

    assert len(release_json["tender"]["lots"]) == 0
