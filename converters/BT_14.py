from lxml import etree

def parse_documents_restricted(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"documents": []}}

    # Parse for Lots
    lot_documents = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cac:CallForTendersDocumentReference", namespaces=namespaces)
    for doc in lot_documents:
        doc_id = doc.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        doc_type = doc.xpath("cbc:DocumentType/text()", namespaces=namespaces)
        if doc_type and doc_type[0] == 'restricted-document':
            lot_id = doc.xpath("ancestor::cac:ProcurementProjectLot/cbc:ID/text()", namespaces=namespaces)[0]
            result["tender"]["documents"].append({
                "id": doc_id,
                "documentType": "biddingDocuments",
                "accessDetails": "Restricted.",
                "relatedLots": [lot_id]
            })

    # Parse for Parts
    part_documents = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingTerms/cac:CallForTendersDocumentReference", namespaces=namespaces)
    for doc in part_documents:
        doc_id = doc.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        doc_type = doc.xpath("cbc:DocumentType/text()", namespaces=namespaces)
        if doc_type and doc_type[0] == 'restricted-document':
            result["tender"]["documents"].append({
                "id": doc_id,
                "documentType": "biddingDocuments",
                "accessDetails": "Restricted."
            })

    return result if result["tender"]["documents"] else None