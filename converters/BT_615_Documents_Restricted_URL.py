# converters/BT_615_Documents_Restricted_URL.py
from lxml import etree

def parse_documents_restricted_url(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = []

    # Process Lots
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        documents = lot.xpath(".//cac:CallForTendersDocumentReference[cbc:DocumentType/text()='restricted-document']", namespaces=namespaces)
        for doc in documents:
            doc_id = doc.xpath("cbc:ID/text()", namespaces=namespaces)[0]
            url = doc.xpath("cac:Attachment/cac:ExternalReference/cbc:URI/text()", namespaces=namespaces)
            if url:
                result.append({
                    "id": doc_id,
                    "accessDetailsURL": url[0],
                    "relatedLots": [lot_id]
                })

    # Process Parts
    part_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']", namespaces=namespaces)
    for part in part_elements:
        documents = part.xpath(".//cac:CallForTendersDocumentReference[cbc:DocumentType/text()='restricted-document']", namespaces=namespaces)
        for doc in documents:
            doc_id = doc.xpath("cbc:ID/text()", namespaces=namespaces)[0]
            url = doc.xpath("cac:Attachment/cac:ExternalReference/cbc:URI/text()", namespaces=namespaces)
            if url:
                result.append({
                    "id": doc_id,
                    "accessDetailsURL": url[0]
                })

    return result

def merge_documents_restricted_url(release_json, documents_data):
    if documents_data:
        tender = release_json.setdefault("tender", {})
        documents = tender.setdefault("documents", [])

        for doc_data in documents_data:
            existing_doc = next((d for d in documents if d.get("id") == doc_data["id"]), None)
            if existing_doc:
                existing_doc.update(doc_data)
                if "relatedLots" in doc_data:
                    existing_doc.setdefault("relatedLots", []).extend(doc_data["relatedLots"])
                    existing_doc["relatedLots"] = list(set(existing_doc["relatedLots"]))  # Remove duplicates
            else:
                documents.append(doc_data)

    return release_json