# converters/OPP_140_ProcurementDocs.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_procurement_documents(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    result = {"tender": {"documents": []}}

    # Process Lot-specific procurement documents
    lot_docs = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cac:CallForTendersDocumentReference",
        namespaces=namespaces,
    )

    for doc in lot_docs:
        doc_id = doc.xpath("cbc:ID/text()", namespaces=namespaces)
        lot_id = doc.xpath("../../cbc:ID/text()", namespaces=namespaces)

        if doc_id and lot_id:
            result["tender"]["documents"].append(
                {"id": doc_id[0], "relatedLots": [lot_id[0]]}
            )

    # Process Part-specific procurement documents
    part_docs = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingTerms/cac:CallForTendersDocumentReference",
        namespaces=namespaces,
    )

    for doc in part_docs:
        doc_id = doc.xpath("cbc:ID/text()", namespaces=namespaces)

        if doc_id:
            result["tender"]["documents"].append({"id": doc_id[0]})

    return result if result["tender"]["documents"] else None


def merge_procurement_documents(release_json, procurement_docs_data):
    if not procurement_docs_data:
        logger.warning("No Procurement Documents data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_documents = tender.setdefault("documents", [])

    for new_doc in procurement_docs_data["tender"]["documents"]:
        existing_doc = next(
            (doc for doc in existing_documents if doc["id"] == new_doc["id"]), None
        )
        if existing_doc:
            if "relatedLots" in new_doc:
                existing_doc.setdefault("relatedLots", []).extend(
                    lot
                    for lot in new_doc["relatedLots"]
                    if lot not in existing_doc.get("relatedLots", [])
                )
        else:
            existing_documents.append(new_doc)

    logger.info(
        f"Merged Procurement Documents data for {len(procurement_docs_data['tender']['documents'])} documents"
    )
