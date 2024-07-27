# converters/BT_707_Part.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

JUSTIFICATION_MAPPING = {
    "ipr-iss": "Restricted. Intellectual property rights issues",
    "phy-mod": "Restricted. Inclusion of a physical model",
    "sen-info": "Restricted. Protection of particularly sensitive information",
    "sp-of-eq": "Restricted. Buyer would need specialised office equipment",
    "tdf-non-av": "Restricted. Tools, devices, or file formats not generally available"
}

def parse_part_documents_restricted_justification(xml_content):
    """
    Parse the XML content to extract the documents restricted justification for each part.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed data in the format:
              {
                  "tender": {
                      "documents": [
                          {
                              "id": "document_id",
                              "accessDetails": "justification"
                          }
                      ]
                  }
              }
        None: If no relevant data is found.

    Raises:
        etree.XMLSyntaxError: If the input is not valid XML.
    """
    # Ensure xml_content is bytes 
    if isinstance(xml_content, str): 
        xml_content = xml_content.encode('utf-8')

    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"documents": []}}

    parts = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']", namespaces=namespaces)
    
    for part in parts:
        documents = part.xpath("cac:TenderingTerms/cac:CallForTendersDocumentReference", namespaces=namespaces)
        
        for doc in documents:
            doc_id = doc.xpath("cbc:ID/text()", namespaces=namespaces)[0]
            justification_code = doc.xpath("cbc:DocumentTypeCode[@listName='communication-justification']/text()", namespaces=namespaces)
            
            if justification_code:
                justification = JUSTIFICATION_MAPPING.get(justification_code[0], "Unknown justification")
                document = {
                    "id": doc_id,
                    "accessDetails": justification
                }
                result["tender"]["documents"].append(document)

    return result if result["tender"]["documents"] else None

def merge_part_documents_restricted_justification(release_json, part_documents_data):
    """
    Merge the parsed part documents restricted justification data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        part_documents_data (dict): The parsed part documents data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not part_documents_data:
        logger.warning("No part documents restricted justification data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_documents = tender.setdefault("documents", [])
    
    for new_doc in part_documents_data["tender"]["documents"]:
        existing_doc = next((doc for doc in existing_documents if doc["id"] == new_doc["id"]), None)
        if existing_doc:
            existing_doc["accessDetails"] = new_doc["accessDetails"]
        else:
            existing_documents.append(new_doc)

    logger.info(f"Merged part documents restricted justification data for {len(part_documents_data['tender']['documents'])} documents")