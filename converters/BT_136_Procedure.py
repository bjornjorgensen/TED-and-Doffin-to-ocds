# converters/BT_136_Procedure.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_direct_award_justification(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {
        "tender": {"procurementMethodRationaleClassifications": []},
        "relatedProcesses": []
    }

    justification_code_mapping = {
        'additional': 'Need for additional works or services by the original contractor',
        'artistic': 'The contract can be provided only by a particular economic operator because of creation or acquisition of a unique work of art or artistic performance',
        'bargain': 'Bargain purchase taking advantage of a particularly advantageous opportunity available for a very short time at a price considerably lower than market prices',
        'below-thres': 'Contracts with estimated value below the procurement thresholds',
        'below-thres-sme': 'Small contract with a small or medium-sized enterprise (article 5(4) 2nd paragraph of Regulation 1370/2007)',
        'char-imp': 'Structural and geographical characteristics of market/network or improvement of quality of services or cost-efficiency – only for rail (article 5(4a) of Regulation 1370/2007)',
        'closure': 'Purchase on particularly advantageous terms from an economic operator which is definitely winding up its business activities',
        'commodity': 'Procurement of supplies quoted and purchased on a commodity market',
        'contest': 'Service contract to be awarded to the winner or one of winners under the rules of a design contest',
        'crisis': 'The periods for the restricted procedure and the negotiated procedure with prior publication of a contract notice are incompatible with the urgency resulting from a crisis',
        'defse-excl': 'Defence-specific and security-specific exclusions',
        'dir24-list': 'Contracts listed in Directive 2014/24/EU Art. 7, but not falling within the scope of Directive 2014/25/EU',
        'dir81-annexii': 'The contract falls within the services listed in Annex II of the Directive 2009/81/EC',
        'dir81-transport': 'Contract related to the provision of air and maritime transport services for the armed forces of a Member State deployed or to be deployed abroad, under the strict conditions stated in the Directive',
        'ecom-excl': 'Specific exclusion in the field of electronic communications',
        'energy-supply': 'Contracts awarded for the supply of energy or of fuels for the production of energy',
        'exc-circ-rail': 'Exceptional circumstances – only for rail (article 5(3a) of Regulation 1370/2007)',
        'exclusive': 'The contract can be provided only by a particular economic operator because of exclusive rights, including intellectual property rights',
        'existing': 'Partial replacement or extension of existing supplies or installations by the original supplier ordered under the strict conditions stated in the Directive',
        'in-house': 'Public contract between organisations within the public sector (\'in-house\'), contracts awarded to affiliated undertakings, or contracts awarded to a joint venture or within a joint venture',
        'int-oper': 'Internal operator (article 5(2) of Regulation 1370/2007)',
        'int-rules': 'Procedure according to international rules'
    }

    process_justifications = root.xpath("//cac:TenderingProcess/cac:ProcessJustification", namespaces=namespaces)
    
    for i, justification in enumerate(process_justifications, start=1):
        code = justification.xpath("cbc:ProcessReasonCode[@listName='direct-award-justification']/text()", namespaces=namespaces)
        description = justification.xpath("cbc:Description/text()", namespaces=namespaces)
        
        if code:
            classification = {
                "id": code[0],
                "description": justification_code_mapping.get(code[0], "Unknown"),
                "scheme": "eu-direct-award-justification"
            }
            result["tender"]["procurementMethodRationaleClassifications"].append(classification)

        if description:
            related_process = {
                "id": str(i),
                "identifier": description[0],
                "scheme": "eu-oj",
                "relationship": []
            }
            
            if code:
                if code[0] in ["irregular", "unsuitable"]:
                    related_process["relationship"].append("unsuccessfulProcess")
                elif code[0] in ["additional", "existing", "repetition"]:
                    related_process["relationship"].append("prior")
            
            result["relatedProcesses"].append(related_process)

    return result if (result["tender"]["procurementMethodRationaleClassifications"] or result["relatedProcesses"]) else None

def merge_direct_award_justification(release_json, direct_award_justification_data):
    if not direct_award_justification_data:
        logger.warning("No direct award justification data to merge")
        return

    existing_classifications = release_json.setdefault("tender", {}).setdefault("procurementMethodRationaleClassifications", [])
    new_classifications = direct_award_justification_data["tender"]["procurementMethodRationaleClassifications"]

    for new_classification in new_classifications:
        existing_classification = next((c for c in existing_classifications if c["id"] == new_classification["id"] and c["scheme"] == new_classification["scheme"]), None)
        if existing_classification:
            existing_classification.update(new_classification)
        else:
            existing_classifications.append(new_classification)

    existing_related_processes = release_json.setdefault("relatedProcesses", [])
    new_related_processes = direct_award_justification_data["relatedProcesses"]

    for new_process in new_related_processes:
        existing_process = next((p for p in existing_related_processes if p["id"] == new_process["id"]), None)
        if existing_process:
            existing_process.update(new_process)
        else:
            existing_related_processes.append(new_process)

    logger.info(f"Merged direct award justification data for {len(new_classifications)} classifications and {len(new_related_processes)} related processes")