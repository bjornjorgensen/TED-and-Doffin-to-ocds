# tests/test_opt_301_part_employlegis.py

from src.ted_and_doffin_to_ocds.converters.eforms.opt_301_part_employlegis import (
    part_merge_employment_legislation_org_reference,
    part_parse_employment_legislation_org_reference,
)


def test_parse_employment_legislation() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:Organizations>
                            <efac:Organization>
                                <efac:Company>
                                    <cac:PartyIdentification>
                                        <cbc:ID schemeName="organization">ORG-0001</cbc:ID>
                                    </cac:PartyIdentification>
                                </efac:Company>
                            </efac:Organization>
                        </efac:Organizations>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">1</cbc:ID>
            <cac:TenderingTerms>
                <cac:EmploymentLegislationDocumentReference>
                    <cbc:ID>Empl1</cbc:ID>
                    <cac:IssuerParty>
                        <cac:PartyIdentification>
                            <cbc:ID schemeName="organization">ORG-0001</cbc:ID>
                        </cac:PartyIdentification>
                    </cac:IssuerParty>
                </cac:EmploymentLegislationDocumentReference>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    result = part_parse_employment_legislation_org_reference(xml_content)
    assert result == {
        "parties": [{"id": "ORG-0001", "roles": ["informationService"]}],
        "tender": {"documents": [{"id": "Empl1", "publisher": {"id": "ORG-0001"}}]},
    }


def test_merge_employment_legislation() -> None:
    release_json = {
        "parties": [{"id": "ORG-0001", "roles": ["buyer"]}],
        "tender": {"documents": [{"id": "Doc1", "title": "Existing Document"}]},
    }
    employment_legislation_data = {
        "parties": [{"id": "ORG-0001", "roles": ["informationService"]}],
        "tender": {"documents": [{"id": "Empl1", "publisher": {"id": "ORG-0001"}}]},
    }
    part_merge_employment_legislation_org_reference(
        release_json, employment_legislation_data
    )
    assert release_json == {
        "parties": [{"id": "ORG-0001", "roles": ["buyer", "informationService"]}],
        "tender": {
            "documents": [
                {"id": "Doc1", "title": "Existing Document"},
                {"id": "Empl1", "publisher": {"id": "ORG-0001"}},
            ]
        },
    }


def test_merge_employment_legislation_new_party() -> None:
    release_json = {"parties": [{"id": "ORG-0002", "roles": ["buyer"]}]}
    employment_legislation_data = {
        "parties": [{"id": "ORG-0001", "roles": ["informationService"]}],
        "tender": {"documents": [{"id": "Empl1", "publisher": {"id": "ORG-0001"}}]},
    }
    part_merge_employment_legislation_org_reference(
        release_json, employment_legislation_data
    )
    assert release_json == {
        "parties": [
            {"id": "ORG-0002", "roles": ["buyer"]},
            {"id": "ORG-0001", "roles": ["informationService"]},
        ],
        "tender": {"documents": [{"id": "Empl1", "publisher": {"id": "ORG-0001"}}]},
    }
