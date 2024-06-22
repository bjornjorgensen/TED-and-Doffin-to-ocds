from lxml import etree

def parse_gpa_coverage(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {}}
    lots = []

    # Parse GPA coverage for lots
    procurement_project_lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in procurement_project_lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        gpa_covered = lot.xpath(
            "cac:TenderingProcess/cbc:GovernmentAgreementConstraintIndicator/text()",
            namespaces=namespaces
        )
        
        if gpa_covered and gpa_covered[0].lower() == 'true':
            lots.append({
                "id": lot_id,
                "coveredBy": ["GPA"]
            })

    if lots:
        result["tender"]["lots"] = lots

    # Parse GPA coverage for parts
    part_gpa_covered = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingProcess/cbc:GovernmentAgreementConstraintIndicator/text()",
        namespaces=namespaces
    )

    if part_gpa_covered and part_gpa_covered[0].lower() == 'true':
        result["tender"]["coveredBy"] = ["GPA"]

    return result if result["tender"] else None