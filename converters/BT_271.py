# converters/BT_271.py
from lxml import etree

def parse_framework_maximum_value(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }
    
    result = {"tender": {"lots": [], "lotGroups": []}}
    
    # Parse Lots
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot_element in lot_elements:
        lot_id = lot_element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        framework_max_amount = lot_element.xpath("cac:ProcurementProject/cac:RequestedTenderTotal/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efbc:FrameworkMaximumAmount", namespaces=namespaces)
        if framework_max_amount:
            lot = {
                "id": lot_id,
                "techniques": {
                    "frameworkAgreement": {
                        "value": {
                            "amount": float(framework_max_amount[0].text),
                            "currency": framework_max_amount[0].get("currencyID")
                        }
                    }
                }
            }
            result["tender"]["lots"].append(lot)
    
    # Parse Lot Groups
    lotgroup_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']", namespaces=namespaces)
    for lotgroup_element in lotgroup_elements:
        lotgroup_id = lotgroup_element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        framework_max_amount = lotgroup_element.xpath("cac:ProcurementProject/cac:RequestedTenderTotal/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efbc:FrameworkMaximumAmount", namespaces=namespaces)
        if framework_max_amount:
            lotgroup = {
                "id": lotgroup_id,
                "techniques": {
                    "frameworkAgreement": {
                        "value": {
                            "amount": float(framework_max_amount[0].text),
                            "currency": framework_max_amount[0].get("currencyID")
                        }
                    }
                }
            }
            result["tender"]["lotGroups"].append(lotgroup)
    
    # Parse Procedure
    procedure_element = root.xpath("/*/cac:ProcurementProject/cac:RequestedTenderTotal/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efbc:FrameworkMaximumAmount", namespaces=namespaces)
    if procedure_element:
        result["tender"]["techniques"] = {
            "frameworkAgreement": {
                "value": {
                    "amount": float(procedure_element[0].text),
                    "currency": procedure_element[0].get("currencyID")
                }
            }
        }
    
    return result if (result["tender"]["lots"] or result["tender"]["lotGroups"] or "techniques" in result["tender"]) else None

def merge_framework_maximum_value(release_json, framework_max_value_data):
    if framework_max_value_data and "tender" in framework_max_value_data:
        tender = release_json.setdefault("tender", {})
        
        # Merge lots
        if "lots" in framework_max_value_data["tender"]:
            existing_lots = tender.setdefault("lots", [])
            for new_lot in framework_max_value_data["tender"]["lots"]:
                existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
                if existing_lot:
                    existing_lot.setdefault("techniques", {}).setdefault("frameworkAgreement", {})["value"] = new_lot["techniques"]["frameworkAgreement"]["value"]
                else:
                    existing_lots.append(new_lot)
        
        # Merge lot groups
        if "lotGroups" in framework_max_value_data["tender"]:
            existing_lotgroups = tender.setdefault("lotGroups", [])
            for new_lotgroup in framework_max_value_data["tender"]["lotGroups"]:
                existing_lotgroup = next((lotgroup for lotgroup in existing_lotgroups if lotgroup["id"] == new_lotgroup["id"]), None)
                if existing_lotgroup:
                    existing_lotgroup.setdefault("techniques", {}).setdefault("frameworkAgreement", {})["value"] = new_lotgroup["techniques"]["frameworkAgreement"]["value"]
                else:
                    existing_lotgroups.append(new_lotgroup)
        
        # Merge tender techniques (Procedure)
        if "techniques" in framework_max_value_data["tender"]:
            tender.setdefault("techniques", {}).setdefault("frameworkAgreement", {})["value"] = framework_max_value_data["tender"]["techniques"]["frameworkAgreement"]["value"]
