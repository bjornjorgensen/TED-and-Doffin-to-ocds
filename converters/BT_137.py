from lxml import etree

def parse_purpose_lot_identifier(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {}}

    # Parse for Lots
    lot_ids = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cbc:ID/text()", namespaces=namespaces)
    if lot_ids:
        result["tender"]["lots"] = [{"id": lot_id} for lot_id in lot_ids]

    # Parse for Lot Groups
    lot_group_ids = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']/cbc:ID/text()", namespaces=namespaces)
    if lot_group_ids:
        result["tender"]["lotGroups"] = [{"id": lot_group_id} for lot_group_id in lot_group_ids]

    # Parse for Parts
    part_id = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cbc:ID/text()", namespaces=namespaces)
    if part_id:
        result["tender"]["id"] = part_id[0]

    return result if result["tender"] else None