# tests/test_BT_67_Exclusion_Grounds.py

import pytest
from lxml import etree
from converters.BT_67_Exclusion_Grounds import (
    parse_exclusion_grounds,
    merge_exclusion_grounds,
)

# Define the namespaces
NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}


def create_xml_with_exclusion_grounds(grounds):
    root = etree.Element("root", nsmap=NAMESPACES)
    terms = etree.SubElement(root, "{{{}}}TenderingTerms".format(NAMESPACES["cac"]))
    qual_request = etree.SubElement(
        terms, "{{{}}}TendererQualificationRequest".format(NAMESPACES["cac"])
    )

    for ground in grounds:
        requirement = etree.SubElement(
            qual_request, "{{{}}}SpecificTendererRequirement".format(NAMESPACES["cac"])
        )
        if "type" in ground:
            type_code = etree.SubElement(
                requirement,
                "{{{}}}TendererRequirementTypeCode".format(NAMESPACES["cbc"]),
            )
            type_code.set("listName", "exclusion-ground")
            type_code.text = ground["type"]
        if "description" in ground:
            description = etree.SubElement(
                requirement, "{{{}}}Description".format(NAMESPACES["cbc"])
            )
            description.text = ground["description"]

    return etree.tostring(root)


def test_parse_exclusion_grounds_with_type_and_description():
    xml_content = create_xml_with_exclusion_grounds(
        [
            {
                "type": "crime-org",
                "description": "Additional details about criminal organization",
            },
            {"type": "corruption", "description": "Specific corruption criteria"},
        ]
    )

    result = parse_exclusion_grounds(xml_content)

    assert result is not None
    assert len(result["tender"]["exclusionGrounds"]["criteria"]) == 2
    assert result["tender"]["exclusionGrounds"]["criteria"][0] == {
        "type": "crime-org",
        "description": "Participation in a criminal organisation: Additional details about criminal organization",
    }
    assert result["tender"]["exclusionGrounds"]["criteria"][1] == {
        "type": "corruption",
        "description": "Corruption: Specific corruption criteria",
    }


def test_parse_exclusion_grounds_with_type_only():
    xml_content = create_xml_with_exclusion_grounds(
        [{"type": "bankruptcy"}, {"type": "fraud"}]
    )

    result = parse_exclusion_grounds(xml_content)

    assert result is not None
    assert len(result["tender"]["exclusionGrounds"]["criteria"]) == 2
    assert result["tender"]["exclusionGrounds"]["criteria"][0] == {
        "type": "bankruptcy",
        "description": "Bankruptcy",
    }
    assert result["tender"]["exclusionGrounds"]["criteria"][1] == {
        "type": "fraud",
        "description": "Fraud",
    }


def test_parse_exclusion_grounds_with_unknown_type():
    xml_content = create_xml_with_exclusion_grounds(
        [{"type": "unknown-type", "description": "Some description"}]
    )

    result = parse_exclusion_grounds(xml_content)

    assert result is not None
    assert len(result["tender"]["exclusionGrounds"]["criteria"]) == 1
    assert result["tender"]["exclusionGrounds"]["criteria"][0] == {
        "type": "unknown-type",
        "description": ": Some description",
    }


def test_parse_exclusion_grounds_empty():
    xml_content = create_xml_with_exclusion_grounds([])

    result = parse_exclusion_grounds(xml_content)

    assert result is None


def test_merge_exclusion_grounds():
    release_json = {
        "tender": {
            "exclusionGrounds": {
                "criteria": [
                    {"type": "existing-ground", "description": "Existing ground"}
                ]
            }
        }
    }

    exclusion_grounds_data = {
        "tender": {
            "exclusionGrounds": {
                "criteria": [{"type": "new-ground", "description": "New ground"}]
            }
        }
    }

    merge_exclusion_grounds(release_json, exclusion_grounds_data)

    assert len(release_json["tender"]["exclusionGrounds"]["criteria"]) == 2
    assert release_json["tender"]["exclusionGrounds"]["criteria"][0] == {
        "type": "existing-ground",
        "description": "Existing ground",
    }
    assert release_json["tender"]["exclusionGrounds"]["criteria"][1] == {
        "type": "new-ground",
        "description": "New ground",
    }


def test_merge_exclusion_grounds_empty():
    release_json = {"tender": {}}
    exclusion_grounds_data = None

    merge_exclusion_grounds(release_json, exclusion_grounds_data)

    assert "exclusionGrounds" not in release_json["tender"]


if __name__ == "__main__":
    pytest.main()
