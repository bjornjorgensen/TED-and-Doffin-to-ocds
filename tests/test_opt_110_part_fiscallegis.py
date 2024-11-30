# tests/test_opt_110_part_fiscallegis.py

from ted_and_doffin_to_ocds.converters.opt_110_part_fiscallegis import (
    merge_part_fiscal_legislation_url,
    parse_part_fiscal_legislation_url,
)


def test_parse_part_fiscal_legislation_url() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:FiscalLegislationDocumentReference>
                    <cbc:ID>Fiscal1</cbc:ID>
                    <cac:Attachment>
                        <cac:ExternalReference>
                            <cbc:URI>https://fiscal-legislation.gov.stat</cbc:URI>
                        </cac:ExternalReference>
                    </cac:Attachment>
                </cac:FiscalLegislationDocumentReference>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    result = parse_part_fiscal_legislation_url(xml_content)
    assert result == {
        "tender": {
            "documents": [
                {"id": "Fiscal1", "url": "https://fiscal-legislation.gov.stat"}
            ]
        }
    }


def test_merge_part_fiscal_legislation_url() -> None:
    release_json = {
        "tender": {"documents": [{"id": "Fiscal1", "title": "Existing Document"}]}
    }
    part_fiscal_legislation_url_data = {
        "tender": {
            "documents": [
                {"id": "Fiscal1", "url": "https://fiscal-legislation.gov.stat"}
            ]
        }
    }
    merge_part_fiscal_legislation_url(release_json, part_fiscal_legislation_url_data)
    assert release_json == {
        "tender": {
            "documents": [
                {
                    "id": "Fiscal1",
                    "title": "Existing Document",
                    "url": "https://fiscal-legislation.gov.stat",
                }
            ]
        }
    }
