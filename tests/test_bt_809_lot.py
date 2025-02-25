from src.ted_and_doffin_to_ocds.converters.eforms.bt_809_lot import (
    merge_selection_criteria_809,
    parse_selection_criteria_809,
)

SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<notice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1">
    <cac:ProcurementProjectLot>
        <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
        <cac:TenderingTerms>
            <ext:UBLExtensions>
                <ext:UBLExtension>
                    <ext:ExtensionContent>
                        <efext:EformsExtension>
                            <efac:SelectionCriteria>
                                <cbc:TendererRequirementTypeCode listName="selection-criterion">slc-suit</cbc:TendererRequirementTypeCode>
                            </efac:SelectionCriteria>
                            <efac:SelectionCriteria>
                                <cbc:TendererRequirementTypeCode listName="selection-criterion">slc-abil</cbc:TendererRequirementTypeCode>
                            </efac:SelectionCriteria>
                        </efext:EformsExtension>
                    </ext:ExtensionContent>
                </ext:UBLExtension>
            </ext:UBLExtensions>
        </cac:TenderingTerms>
    </cac:ProcurementProjectLot>
</notice>"""


def test_parse_selection_criteria():
    """Test parsing selection criteria from XML."""
    result = parse_selection_criteria_809(SAMPLE_XML)

    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1

    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001"
    assert "selectionCriteria" in lot
    assert "criteria" in lot["selectionCriteria"]

    criteria = lot["selectionCriteria"]["criteria"]
    assert len(criteria) == 2

    assert criteria[0]["type"] == "suitability"
    assert criteria[0]["subType"] == "slc-suit"

    assert criteria[1]["type"] == "technical"
    assert criteria[1]["subType"] == "slc-abil"


def test_parse_selection_criteria_no_criteria():
    """Test parsing XML with no selection criteria."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <notice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
            xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
        </cac:ProcurementProjectLot>
    </notice>"""

    result = parse_selection_criteria_809(xml)
    assert result is None


def test_merge_selection_criteria():
    """Test merging selection criteria into existing JSON."""
    existing_json = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "selectionCriteria": {
                        "criteria": [{"type": "economic", "subType": "slc-stand"}]
                    },
                }
            ]
        }
    }

    new_criteria = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "selectionCriteria": {
                        "criteria": [{"type": "technical", "subType": "slc-abil"}]
                    },
                }
            ]
        }
    }

    merge_selection_criteria_809(existing_json, new_criteria)

    lot = existing_json["tender"]["lots"][0]
    assert len(lot["selectionCriteria"]["criteria"]) == 2
    assert lot["selectionCriteria"]["criteria"][0]["subType"] == "slc-stand"
    assert lot["selectionCriteria"]["criteria"][1]["subType"] == "slc-abil"


def test_merge_selection_criteria_new_lot():
    """Test merging selection criteria with a new lot."""
    existing_json = {"tender": {"lots": []}}

    new_criteria = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "selectionCriteria": {
                        "criteria": [{"type": "technical", "subType": "slc-abil"}]
                    },
                }
            ]
        }
    }

    merge_selection_criteria_809(existing_json, new_criteria)

    assert len(existing_json["tender"]["lots"]) == 1
    assert existing_json["tender"]["lots"][0]["id"] == "LOT-0001"


def test_merge_selection_criteria_none():
    """Test merging with None selection criteria."""
    existing_json = {"tender": {"lots": []}}
    merge_selection_criteria_809(existing_json, None)
    assert existing_json == {"tender": {"lots": []}}


def test_parse_selection_criteria_with_suit_reg_prof():
    xml_content = """
    <cac:ProcurementProjectLot xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
                                xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
                                xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
                                xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
                                xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1">
        <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
        <cac:TenderingTerms>
            <ext:UBLExtensions>
                <ext:UBLExtension>
                    <ext:ExtensionContent>
                        <efext:EformsExtension>
                            <efac:SelectionCriteria>
                                <cbc:TendererRequirementTypeCode listName="selection-criterion">slc-suit-reg-prof</cbc:TendererRequirementTypeCode>
                            </efac:SelectionCriteria>
                        </efext:EformsExtension>
                    </ext:ExtensionContent>
                </ext:UBLExtension>
            </ext:UBLExtensions>
        </cac:TenderingTerms>
    </cac:ProcurementProjectLot>
    """
    expected_output = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "selectionCriteria": {
                        "criteria": [
                            {"type": "suitability", "subType": "slc-suit-reg-prof"}
                        ]
                    },
                }
            ]
        }
    }
    result = parse_selection_criteria_809(xml_content)
    assert result == expected_output
