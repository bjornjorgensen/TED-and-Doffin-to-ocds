# converters/opt_113_part_employlegis.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_part_employment_legislation_document_id(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    result = {"tender": {"documents": []}}

    empl_docs = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingTerms/cac:EmploymentLegislationDocumentReference",
        namespaces=namespaces,
    )

    for doc in empl_docs:
        doc_id = doc.xpath("cbc:ID/text()", namespaces=namespaces)
        if doc_id:
            document = {"id": doc_id[0], "documentType": "legislation"}
            result["tender"]["documents"].append(document)

    return result if result["tender"]["documents"] else None


def merge_part_employment_legislation_document_id(
    release_json, employment_legislation_data
):
    if not employment_legislation_data:
        return

    tender = release_json.setdefault("tender", {})
    existing_documents = tender.setdefault("documents", [])

    for new_doc in employment_legislation_data["tender"]["documents"]:
        existing_doc = next(
            (doc for doc in existing_documents if doc["id"] == new_doc["id"]), None
        )
        if existing_doc:
            existing_doc["documentType"] = "legislation"
        else:
            existing_documents.append(new_doc)

    logger.info(
        "Merged %d part employment legislation document(s)",
        len(employment_legislation_data["tender"]["documents"]),
    )