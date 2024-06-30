# converters/OPP_112_120_EnvironLegis.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_environmental_legislation(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"documents": []}}

    # Process Lot-specific environmental legislation
    lot_environ_docs = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cac:EnvironmentalLegislationDocumentReference", namespaces=namespaces)
    
    for doc in lot_environ_docs:
        doc_id = doc.xpath("cbc:ID/text()", namespaces=namespaces)
        url = doc.xpath("cac:Attachment/cac:ExternalReference/cbc:URI/text()", namespaces=namespaces)
        lot_id = doc.xpath("../../cbc:ID/text()", namespaces=namespaces)
        
        if doc_id:
            document = {
                "id": doc_id[0],
                "documentType": "legislation",
                "relatedLots": [lot_id[0]] if lot_id else []
            }
            if url:
                document["url"] = url[0]
            result["tender"]["documents"].append(document)

    # Process Part-specific environmental legislation
    part_environ_docs = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingTerms/cac:EnvironmentalLegislationDocumentReference", namespaces=namespaces)
    
    for doc in part_environ_docs:
        doc_id = doc.xpath("cbc:ID/text()", namespaces=namespaces)
        url = doc.xpath("cac:Attachment/cac:ExternalReference/cbc:URI/text()", namespaces=namespaces)
        
        if doc_id:
            document = {
                "id": doc_id[0],
                "documentType": "legislation"
            }
            if url:
                document["url"] = url[0]
            result["tender"]["documents"].append(document)

    return result if result["tender"]["documents"] else None

def merge_environmental_legislation(release_json, environmental_legislation_data):
    if not environmental_legislation_data:
        logger.warning("No Environmental Legislation data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_documents = tender.setdefault("documents", [])

    for new_doc in environmental_legislation_data["tender"]["documents"]:
        existing_doc = next((doc for doc in existing_documents if doc["id"] == new_doc["id"]), None)
        if existing_doc:
            existing_doc.update(new_doc)
            if "relatedLots" in new_doc:
                existing_doc.setdefault("relatedLots", []).extend(
                    lot for lot in new_doc["relatedLots"] if lot not in existing_doc.get("relatedLots", [])
                )
        else:
            existing_documents.append(new_doc)

    logger.info(f"Merged Environmental Legislation data for {len(environmental_legislation_data['tender']['documents'])} documents")