from lxml import etree

def parse_previous_planning_identifiers(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"relatedProcesses": []}

    # Parse for Lots
    lot_references = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingProcess/cac:NoticeDocumentReference", namespaces=namespaces)
    for ref in lot_references:
        identifier = ref.xpath("cbc:ID/text()", namespaces=namespaces)
        part_identifier = ref.xpath("cbc:ReferencedDocumentInternalAddress/text()", namespaces=namespaces)
        
        if identifier:
            related_process = {
                "id": "1",
                "relationship": ["planning"],
                "scheme": "eu-oj",
                "identifier": identifier[0]
            }
            if part_identifier:
                related_process["relatedLots"] = part_identifier

            result["relatedProcesses"].append(related_process)

    # Parse for Parts
    part_references = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingProcess/cac:NoticeDocumentReference", namespaces=namespaces)
    for ref in part_references:
        identifier = ref.xpath("cbc:ID/text()", namespaces=namespaces)
        part_identifier = ref.xpath("cbc:ReferencedDocumentInternalAddress/text()", namespaces=namespaces)
        
        if identifier and part_identifier:
            result["relatedProcesses"].append({
                "id": "1",
                "relationship": ["planning"],
                "scheme": "eu-oj",
                "identifier": f"{identifier[0]}-{part_identifier[0]}"
            })

    return result if result["relatedProcesses"] else None