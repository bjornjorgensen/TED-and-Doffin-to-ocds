# converters/BT_71_Reserved_Participation.py
from lxml import etree

def parse_reserved_participation(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {
        'lots': {},
        'tender': []
    }

    # Process Lots
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        reserved_procurement = lot.xpath(".//cac:TendererQualificationRequest[not(cbc:CompanyLegalFormCode)][not(cac:SpecificTendererRequirement/cbc:TendererRequirementTypeCode[@listName='missing-info-submission'])]/cac:SpecificTendererRequirement[cbc:TendererRequirementTypeCode/@listName='reserved-procurement']/cbc:TendererRequirementTypeCode/text()", namespaces=namespaces)
        
        if reserved_procurement:
            result['lots'][lot_id] = [map_reserved_procurement(code) for code in reserved_procurement if code != 'none']

    # Process Parts
    part_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']", namespaces=namespaces)
    for part in part_elements:
        reserved_procurement = part.xpath(".//cac:TendererQualificationRequest[not(cbc:CompanyLegalFormCode)][not(cac:SpecificTendererRequirement/cbc:TendererRequirementTypeCode[@listName='missing-info-submission'])]/cac:SpecificTendererRequirement[cbc:TendererRequirementTypeCode/@listName='reserved-procurement']/cbc:TendererRequirementTypeCode/text()", namespaces=namespaces)
        
        if reserved_procurement:
            result['tender'].extend([map_reserved_procurement(code) for code in reserved_procurement if code != 'none'])

    return result

def map_reserved_procurement(code):
    if code == 'res-pub-ser':
        return 'publicServiceMissionOrganization'
    elif code == 'res-ws':
        return 'shelteredWorkshop'
    else:
        return None

def merge_reserved_participation(release_json, reserved_participation_data):
    tender = release_json.setdefault('tender', {})
    
    # Process Lots
    lots = tender.setdefault('lots', [])
    for lot_id, reserved_participation in reserved_participation_data['lots'].items():
        lot = next((l for l in lots if l.get('id') == lot_id), None)
        if not lot:
            lot = {'id': lot_id}
            lots.append(lot)
        
        if reserved_participation:
            other_requirements = lot.setdefault('otherRequirements', {})
            other_requirements['reservedParticipation'] = reserved_participation

    # Process Parts (Tender-level)
    if reserved_participation_data['tender']:
        other_requirements = tender.setdefault('otherRequirements', {})
        other_requirements['reservedParticipation'] = list(set(reserved_participation_data['tender']))

    return release_json