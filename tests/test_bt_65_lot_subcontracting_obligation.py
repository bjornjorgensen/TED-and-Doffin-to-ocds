# tests/test_bt_65_Lot_Subcontracting_Obligation.py

from ted_and_doffin_to_ocds.converters.bt_65_lot_subcontracting_obligation import (
    SUBCONTRACTING_OBLIGATION_MAPPING,
    merge_subcontracting_obligation,
    parse_subcontracting_obligation,
)


def test_parse_subcontracting_obligation() -> None:
    xml_content = b"""
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:AllowedSubcontractTerms>
                    <cbc:SubcontractingConditionsCode listName="subcontracting-obligation">subc-min</cbc:SubcontractingConditionsCode>
                </cac:AllowedSubcontractTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_subcontracting_obligation(xml_content)

    assert result is not None
    assert len(result["tender"]["lots"]) == 1
    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001"
    assert (
        lot["subcontractingTerms"]["description"]
        == SUBCONTRACTING_OBLIGATION_MAPPING["subc-min"]
    )


def test_parse_subcontracting_obligation_none() -> None:
    xml_content = b"""
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:AllowedSubcontractTerms>
                    <cbc:SubcontractingConditionsCode listName="subcontracting-obligation">none</cbc:SubcontractingConditionsCode>
                </cac:AllowedSubcontractTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_subcontracting_obligation(xml_content)

    assert result is None


def test_parse_subcontracting_obligation_no_data() -> None:
    xml_content = b"""
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_subcontracting_obligation(xml_content)

    assert result is None


def test_merge_subcontracting_obligation() -> None:
    existing_release = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "subcontractingTerms": {"description": "Old description"},
                },
            ],
        },
    }

    new_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "subcontractingTerms": {"description": "New description"},
                },
            ],
        },
    }

    merge_subcontracting_obligation(existing_release, new_data)

    assert len(existing_release["tender"]["lots"]) == 1
    lot = existing_release["tender"]["lots"][0]
    assert lot["subcontractingTerms"]["description"] == "New description"


def test_merge_subcontracting_obligation_new_lot() -> None:
    existing_release = {"tender": {"lots": []}}

    new_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "subcontractingTerms": {"description": "New description"},
                },
            ],
        },
    }

    merge_subcontracting_obligation(existing_release, new_data)

    assert len(existing_release["tender"]["lots"]) == 1
    lot = existing_release["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001"
    assert lot["subcontractingTerms"]["description"] == "New description"
