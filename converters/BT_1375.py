from lxml import etree

def parse_group_lot_identifier(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    lot_groups = []
    lots_groups = root.xpath("//cac:TenderingTerms/cac:LotDistribution/cac:LotsGroup", namespaces=namespaces)
    
    for lots_group in lots_groups:
        group_id_elements = lots_group.xpath("cbc:LotsGroupID/text()", namespaces=namespaces)
        lot_id_elements = lots_group.xpath("cac:ProcurementProjectLotReference/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
        
        if group_id_elements:
            group_id = group_id_elements[0]
            
            lot_group = next((lg for lg in lot_groups if lg["id"] == group_id), None)
            if lot_group is None:
                lot_group = {"id": group_id, "relatedLots": []}
                lot_groups.append(lot_group)
            
            for lot_id in lot_id_elements:
                if lot_id not in lot_group["relatedLots"]:
                    lot_group["relatedLots"].append(lot_id)

    return {"tender": {"lotGroups": lot_groups}} if lot_groups else None