# tests/test_opt_140_lot_procurement_docs.py

from ted_and_doffin_to_ocds.converters.opt_140_lot_procurement_docs import (
    parse_procurement_documents_id,
    merge_procurement_documents_id,
)


def test_parse_procurement_documents_id():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:CallForTendersDocumentReference>
                    <cbc:ID>20210521/CTFD/ENG/7654-02</cbc:ID>
                </cac:CallForTendersDocumentReference>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_procurement_documents_id(xml_content)

    assert result is not None
    assert "tender" in result
    assert "documents" in result["tender"]
    assert len(result["tender"]["documents"]) == 1

    doc = result["tender"]["documents"][0]
    assert doc["id"] == "20210521/CTFD/ENG/7654-02"
    assert doc["relatedLots"] == ["LOT-0001"]


def test_merge_procurement_documents_id():
    release_json = {"tender": {"documents": []}}
    proc_docs_data = {
        "tender": {
            "documents": [
                {"id": "20210521/CTFD/ENG/7654-02", "relatedLots": ["LOT-0001"]}
            ]
        }
    }

    merge_procurement_documents_id(release_json, proc_docs_data)

    assert "documents" in release_json["tender"]
    assert len(release_json["tender"]["documents"]) == 1

    doc = release_json["tender"]["documents"][0]
    assert doc["id"] == "20210521/CTFD/ENG/7654-02"
    assert doc["relatedLots"] == ["LOT-0001"]


def test_merge_procurement_documents_id_existing_document():
    release_json = {
        "tender": {
            "documents": [
                {"id": "20210521/CTFD/ENG/7654-02", "relatedLots": ["LOT-0002"]}
            ]
        }
    }
    proc_docs_data = {
        "tender": {
            "documents": [
                {"id": "20210521/CTFD/ENG/7654-02", "relatedLots": ["LOT-0001"]}
            ]
        }
    }

    merge_procurement_documents_id(release_json, proc_docs_data)

    assert len(release_json["tender"]["documents"]) == 1

    doc = release_json["tender"]["documents"][0]
    assert doc["id"] == "20210521/CTFD/ENG/7654-02"
    assert set(doc["relatedLots"]) == {"LOT-0001", "LOT-0002"}
