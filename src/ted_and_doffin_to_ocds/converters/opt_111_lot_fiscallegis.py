# converters/opt_111_lot_fiscallegis.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_fiscal_legislation_document_id(xml_content):
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
        fiscal_docs = lot.xpath(
            "cac:TenderingTerms/cac:FiscalLegislationDocumentReference",
            namespaces=namespaces,
        )

        for doc in fiscal_docs:
            doc_id = doc.xpath("cbc:ID/text()", namespaces=namespaces)
            if doc_id:
                document = {
                    "id": doc_id[0],
                    "documentType": "legislation",
                    "relatedLots": [lot_id],
                }
                result["tender"]["documents"].append(document)

    return result if result["tender"]["documents"] else None


def merge_fiscal_legislation_document_id(release_json, fiscal_legislation_data):
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
            existing_doc.setdefault("relatedLots", []).extend(new_doc["relatedLots"])
            existing_doc["relatedLots"] = list(
                set(existing_doc["relatedLots"])
            )  # Remove duplicates
        else:
            existing_documents.append(new_doc)

    logger.info(
        "Merged %d fiscal legislation document(s)",
        len(fiscal_legislation_data["tender"]["documents"]),
    )
