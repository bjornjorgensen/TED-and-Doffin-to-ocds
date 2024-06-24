# converters/BT_707_Documents_Restricted_Justification.py
from lxml import etree

JUSTIFICATION_MAPPING = {
    "ipr-iss": "Restricted. Intellectual property rights issues",
    "phy-mod": "Restricted. Inclusion of a physical model",
    "sen-info": "Restricted. Protection of particularly sensitive information",
    "sp-of-eq": "Restricted. Buyer would need specialised office equipment",
    "tdf-non-av": "Restricted. Tools, devices, or file formats not generally available"
}

def parse_documents_restricted_justification(xml_content):
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
        documents = lot.xpath(".//cac:CallForTendersDocumentReference", namespaces=namespaces)
        for doc in documents:
            doc_id = doc.xpath("cbc:ID/text()", namespaces=namespaces)[0]
            justification_code = doc.xpath("cbc:DocumentTypeCode[@listName='communication-justification']/text()", namespaces=namespaces)
            if justification_code:
                result.append({
                    "id": doc_id,
                    "accessDetails": JUSTIFICATION_MAPPING.get(justification_code[0], "Restricted"),
                    "relatedLots": [lot_id]
                })

    # Process Parts
    part_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']", namespaces=namespaces)
    for part in part_elements:
        documents = part.xpath(".//cac:CallForTendersDocumentReference", namespaces=namespaces)
        for doc in documents:
            doc_id = doc.xpath("cbc:ID/text()", namespaces=namespaces)[0]
            justification_code = doc.xpath("cbc:DocumentTypeCode[@listName='communication-justification']/text()", namespaces=namespaces)
            if justification_code:
                result.append({
                    "id": doc_id,
                    "accessDetails": JUSTIFICATION_MAPPING.get(justification_code[0], "Restricted")
                })

    return result

def merge_documents_restricted_justification(release_json, justification_data):
    if justification_data:
        tender = release_json.setdefault("tender", {})
        documents = tender.setdefault("documents", [])

        for doc_data in justification_data:
            existing_doc = next((d for d in documents if d.get("id") == doc_data["id"]), None)
            if existing_doc:
                existing_doc.update(doc_data)
                if "relatedLots" in doc_data:
                    existing_doc.setdefault("relatedLots", []).extend(doc_data["relatedLots"])
                    existing_doc["relatedLots"] = list(set(existing_doc["relatedLots"]))  # Remove duplicates
            else:
                documents.append(doc_data)

    return release_json