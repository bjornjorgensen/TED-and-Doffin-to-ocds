from ted_and_doffin_to_ocds.converters.bt_806_procedure import (
    merge_exclusion_grounds_sources,
    parse_exclusion_grounds_sources,
)

SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<notice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cac:TenderingTerms>
        <cac:TendererQualificationRequest>
            <cac:SpecificTendererRequirement>
                <cbc:TendererRequirementTypeCode listName="exclusion-grounds-source">epo-procurement-document</cbc:TendererRequirementTypeCode>
            </cac:SpecificTendererRequirement>
        </cac:TendererQualificationRequest>
        <cac:TendererQualificationRequest>
            <cac:SpecificTendererRequirement>
                <cbc:TendererRequirementTypeCode listName="exclusion-grounds-source">espd-request</cbc:TendererRequirementTypeCode>
            </cac:SpecificTendererRequirement>
        </cac:TendererQualificationRequest>
    </cac:TenderingTerms>
</notice>"""

EMPTY_XML = """<?xml version="1.0" encoding="UTF-8"?>
<notice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cac:TenderingTerms>
    </cac:TenderingTerms>
</notice>"""


def test_parse_exclusion_grounds_sources():
    result = parse_exclusion_grounds_sources(SAMPLE_XML)
    expected = {
        "tender": {
            "exclusionGrounds": {
                "sources": ["epo-procurement-document", "espd-request"]
            }
        }
    }
    assert result == expected


def test_parse_exclusion_grounds_sources_empty():
    result = parse_exclusion_grounds_sources(EMPTY_XML)
    assert result is None


def test_merge_exclusion_grounds_sources():
    release = {}
    sources = {
        "tender": {
            "exclusionGrounds": {
                "sources": ["epo-procurement-document", "espd-request"]
            }
        }
    }
    merge_exclusion_grounds_sources(release, sources)

    expected = {
        "tender": {
            "exclusionGrounds": {
                "sources": ["epo-procurement-document", "espd-request"]
            }
        }
    }
    assert release == expected


def test_merge_exclusion_grounds_sources_existing():
    release = {
        "tender": {"exclusionGrounds": {"sources": ["epo-procurement-document"]}}
    }
    sources = {
        "tender": {
            "exclusionGrounds": {
                "sources": ["epo-procurement-document", "espd-request"]
            }
        }
    }
    merge_exclusion_grounds_sources(release, sources)

    expected = {
        "tender": {
            "exclusionGrounds": {
                "sources": ["epo-procurement-document", "espd-request"]
            }
        }
    }
    assert release == expected


def test_merge_exclusion_grounds_sources_none():
    release = {}
    merge_exclusion_grounds_sources(release, None)
    assert release == {}
