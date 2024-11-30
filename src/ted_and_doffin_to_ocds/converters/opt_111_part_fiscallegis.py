# converters/opt_111_part_fiscallegis.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_part_fiscal_legislation_document_id(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    result = {"tender": {"documents": []}}

    fiscal_docs = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingTerms/cac:FiscalLegislationDocumentReference",
        namespaces=namespaces,
    )

    for doc in fiscal_docs:
        doc_id = doc.xpath("cbc:ID/text()", namespaces=namespaces)
        if doc_id:
            document = {"id": doc_id[0], "documentType": "legislation"}
            result["tender"]["documents"].append(document)

    return result if result["tender"]["documents"] else None


def merge_part_fiscal_legislation_document_id(
    release_json, fiscal_legislation_data
) -> None:
    if not fiscal_legislation_data:
        return

    tender = release_json.setdefault("tender", {})
    existing_documents = tender.setdefault("documents", [])

    for new_doc in fiscal_legislation_data["tender"]["documents"]:
        existing_doc = next(
            (doc for doc in existing_documents if doc["id"] == new_doc["id"]), None
        )
        if existing_doc:
            existing_doc["documentType"] = "legislation"
        else:
            existing_documents.append(new_doc)

    logger.info(
        "Merged %d part fiscal legislation document(s)",
        len(fiscal_legislation_data["tender"]["documents"]),
    )
