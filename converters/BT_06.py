# converters/BT_06.py
from lxml import etree

class Sustainability:
    def __init__(self, goal, strategies):
        self.goal = goal
        self.strategies = strategies

class Lot:
    def __init__(self, id):
        self.id = id
        self.hasSustainability = False
        self.sustainability = []

def parse_procurement_project_lot(xml_content):
    """
    Parses the XML content to extract the procurement project lot information
    and updates the tender object accordingly.
    
    :param xml_content: The XML content as a string.
    :return: A dictionary containing the updated tender object.
    """
    tree = etree.fromstring(xml_content)
    tender = {"lots": []}
    
    # XPath to get all ProcurementProjectLot elements
    procurement_project_lots = tree.xpath("//cac:ProcurementProjectLot", namespaces={"cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"})
    
    for lot_elem in procurement_project_lots:
        lot_id = lot_elem.xpath("./cbc:ID", namespaces={"cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"})[0].text
        lot = Lot(lot_id)
        
        procurement_additional_types = lot_elem.xpath("./cac:ProcurementProject/cac:ProcurementAdditionalType", namespaces={"cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"})
        
        for additional_type in procurement_additional_types:
            procurement_type_code = additional_type.xpath("./cbc:ProcurementTypeCode", namespaces={"cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"})[0].text
            
            if procurement_type_code == "none":
                continue
            
            lot.hasSustainability = True
            
            goal_mapping = {
                "env-imp": "environmental",
                "inn-pur": "economic.innovativePurchase",
                "soc-obj": "social"
            }
            
            sustainability = Sustainability(
                goal=goal_mapping.get(procurement_type_code, "unknown"),
                strategies=["awardCriteria", "contractPerformanceConditions", "selectionCriteria", "technicalSpecifications"]
            )
            
            lot.sustainability.append(sustainability.__dict__)
        
        tender["lots"].append(lot.__dict__)
    
    return tender