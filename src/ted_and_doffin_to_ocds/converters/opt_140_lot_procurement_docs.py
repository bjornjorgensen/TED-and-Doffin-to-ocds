# converters/opt_140_lot_procurement_docs.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_procurement_documents_id(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    result = {"tender": {"documents": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        doc_refs = lot.xpath(
            "cac:TenderingTerms/cac:CallForTendersDocumentReference/cbc:ID/text()",
            namespaces=namespaces,
        )

        for doc_id in doc_refs:
            result["tender"]["documents"].append(
                {"id": doc_id, "relatedLots": [lot_id]}
            )

    return result if result["tender"]["documents"] else None


def merge_procurement_documents_id(release_json, proc_docs_data) -> None:
    if not proc_docs_data:
        logger.info("No procurement documents ID data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_docs = tender.setdefault("documents", [])

    for new_doc in proc_docs_data["tender"]["documents"]:
        existing_doc = next(
            (doc for doc in existing_docs if doc["id"] == new_doc["id"]), None
        )
        if existing_doc:
            existing_doc.setdefault("relatedLots", []).extend(new_doc["relatedLots"])
            existing_doc["relatedLots"] = list(
                set(existing_doc["relatedLots"])
            )  # Remove duplicates
        else:
            existing_docs.append(new_doc)

    logger.info(
        "Merged procurement documents ID data for %d documents",
        len(proc_docs_data["tender"]["documents"]),
    )
