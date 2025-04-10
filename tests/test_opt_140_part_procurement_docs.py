# tests/test_opt_140_part_procurement_docs.py

from src.ted_and_doffin_to_ocds.converters.eforms.opt_140_part_procurement_docs import (
    merge_procurement_documents_id_part,
    parse_procurement_documents_id_part,
)


def test_parse_procurement_documents_id_part() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:CallForTendersDocumentReference>
                    <cbc:ID>20210521/CTFD/ENG/7654-02</cbc:ID>
                </cac:CallForTendersDocumentReference>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_procurement_documents_id_part(xml_content)

    assert result is not None
    assert "tender" in result
    assert "documents" in result["tender"]
    assert len(result["tender"]["documents"]) == 1

    doc = result["tender"]["documents"][0]
    assert doc["id"] == "20210521/CTFD/ENG/7654-02"


def test_merge_procurement_documents_id_part() -> None:
    release_json = {"tender": {"documents": []}}
    proc_docs_data = {"tender": {"documents": [{"id": "20210521/CTFD/ENG/7654-02"}]}}

    merge_procurement_documents_id_part(release_json, proc_docs_data)

    assert "documents" in release_json["tender"]
    assert len(release_json["tender"]["documents"]) == 1

    doc = release_json["tender"]["documents"][0]
    assert doc["id"] == "20210521/CTFD/ENG/7654-02"


def test_merge_procurement_documents_id_part_existing_document() -> None:
    release_json = {"tender": {"documents": [{"id": "20210521/CTFD/ENG/7654-02"}]}}
    proc_docs_data = {
        "tender": {
            "documents": [
                {"id": "20210521/CTFD/ENG/7654-02"},
                {"id": "20210522/CTFD/ENG/7654-03"},
            ]
        }
    }

    merge_procurement_documents_id_part(release_json, proc_docs_data)

    assert len(release_json["tender"]["documents"]) == 2

    doc_ids = [doc["id"] for doc in release_json["tender"]["documents"]]
    assert "20210521/CTFD/ENG/7654-02" in doc_ids
    assert "20210522/CTFD/ENG/7654-03" in doc_ids
