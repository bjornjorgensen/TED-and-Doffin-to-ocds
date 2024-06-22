from lxml import etree

def parse_documents_url(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"documents": []}}

    # Parse for Lots
    lot_documents = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cac:CallForTendersDocumentReference[cbc:DocumentType/text()='non-restricted-document']", namespaces=namespaces)
    for doc in lot_documents:
        doc_id = doc.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        url = doc.xpath("cac:Attachment/cac:ExternalReference/cbc:URI/text()", namespaces=namespaces)
        if url:
            lot_id = doc.xpath("ancestor::cac:ProcurementProjectLot/cbc:ID/text()", namespaces=namespaces)[0]
            result["tender"]["documents"].append({
                "id": doc_id,
                "documentType": "biddingDocuments",
                "url": url[0],
                "relatedLots": [lot_id]
            })

    # Parse for Parts
    part_documents = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingTerms/cac:CallForTendersDocumentReference[cbc:DocumentType/text()='non-restricted-document']", namespaces=namespaces)
    for doc in part_documents:
        doc_id = doc.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        url = doc.xpath("cac:Attachment/cac:ExternalReference/cbc:URI/text()", namespaces=namespaces)
        if url:
            result["tender"]["documents"].append({
                "id": doc_id,
                "documentType": "biddingDocuments",
                "url": url[0]
            })

    return result if result["tender"]["documents"] else None