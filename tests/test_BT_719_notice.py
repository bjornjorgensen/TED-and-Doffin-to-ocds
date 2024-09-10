# tests/test_BT_719_notice.py

import pytest
from ted_and_doffin_to_ocds.converters.BT_719_notice import (
    parse_procurement_documents_change_date,
    merge_procurement_documents_change_date,
)


@pytest.fixture
def sample_xml():
    return """
    <root xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:Changes>
                            <efac:Change>
                                <efbc:ProcurementDocumentsChangeDate>2023-05-15+01:00</efbc:ProcurementDocumentsChangeDate>
                                <efac:ChangedSection>
                                    <efbc:ChangedSectionIdentifier>LOT-0001</efbc:ChangedSectionIdentifier>
                                </efac:ChangedSection>
                            </efac:Change>
                            <efac:Change>
                                <efbc:ProcurementDocumentsChangeDate>2023-05-16+01:00</efbc:ProcurementDocumentsChangeDate>
                            </efac:Change>
                        </efac:Changes>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """


def test_parse_procurement_documents_change_date(sample_xml):
    result = parse_procurement_documents_change_date(sample_xml)
    assert result is not None
    assert "tender" in result
    assert "documents" in result["tender"]
    assert len(result["tender"]["documents"]) == 2

    lot_specific_doc = result["tender"]["documents"][0]
    assert lot_specific_doc["dateModified"] == "2023-05-15T00:00:00+01:00"
    assert lot_specific_doc["documentType"] == "biddingDocuments"
    assert lot_specific_doc["relatedLots"] == ["LOT-0001"]

    general_doc = result["tender"]["documents"][1]
    assert general_doc["dateModified"] == "2023-05-16T00:00:00+01:00"
    assert general_doc["documentType"] == "biddingDocuments"
    assert "relatedLots" not in general_doc


def test_parse_procurement_documents_change_date_no_data():
    xml_without_data = "<root></root>"
    result = parse_procurement_documents_change_date(xml_without_data)
    assert result is None


def test_merge_procurement_documents_change_date():
    existing_release = {
        "tender": {
            "documents": [
                {
                    "id": "doc1",
                    "documentType": "biddingDocuments",
                    "relatedLots": ["LOT-0001"],
                },
                {"id": "doc2", "documentType": "biddingDocuments"},
            ]
        }
    }

    change_date_data = {
        "tender": {
            "documents": [
                {
                    "dateModified": "2023-05-15T00:00:00+01:00",
                    "documentType": "biddingDocuments",
                    "relatedLots": ["LOT-0001"],
                },
                {
                    "dateModified": "2023-05-16T00:00:00+01:00",
                    "documentType": "biddingDocuments",
                },
            ]
        }
    }

    merge_procurement_documents_change_date(existing_release, change_date_data)

    assert len(existing_release["tender"]["documents"]) == 2
    assert (
        existing_release["tender"]["documents"][0]["dateModified"]
        == "2023-05-15T00:00:00+01:00"
    )
    assert (
        existing_release["tender"]["documents"][1]["dateModified"]
        == "2023-05-16T00:00:00+01:00"
    )


def test_merge_procurement_documents_change_date_new_document():
    existing_release = {
        "tender": {"documents": [{"id": "doc1", "documentType": "biddingDocuments"}]}
    }

    change_date_data = {
        "tender": {
            "documents": [
                {
                    "dateModified": "2023-05-15T00:00:00+01:00",
                    "documentType": "biddingDocuments",
                    "relatedLots": ["LOT-0001"],
                }
            ]
        }
    }

    merge_procurement_documents_change_date(existing_release, change_date_data)

    assert len(existing_release["tender"]["documents"]) == 2
    assert (
        existing_release["tender"]["documents"][1]["dateModified"]
        == "2023-05-15T00:00:00+01:00"
    )
    assert existing_release["tender"]["documents"][1]["relatedLots"] == ["LOT-0001"]


def test_merge_procurement_documents_change_date_no_data():
    existing_release = {"tender": {"documents": []}}
    merge_procurement_documents_change_date(existing_release, None)
    assert existing_release == {"tender": {"documents": []}}


if __name__ == "__main__":
    pytest.main()
