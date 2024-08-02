# converters/BT_615_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_documents_restricted_url(xml_content):
    """
    Parse the XML content to extract documents restricted URL information for each lot.

    This function processes the BT-615-Lot business term, which represents
    the internet address with information on accessing the restricted (part of the) procurement documents.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed documents restricted URL data in the format:
              {
                  "tender": {
                      "documents": [
                          {
                              "id": "document_id",
                              "accessDetailsURL": "url",
                              "relatedLots": ["lot_id"]
                          }
                      ]
                  }
              }
        None: If no relevant data is found.

    Raises:
        etree.XMLSyntaxError: If the input is not valid XML.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode('utf-8')
    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    result = {"tender": {"documents": []}}

    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        documents = lot.xpath("cac:TenderingTerms/cac:CallForTendersDocumentReference[cbc:DocumentType/text()='restricted-document']", namespaces=namespaces)
        
        for document in documents:
            doc_id = document.xpath("cbc:ID/text()", namespaces=namespaces)
            url = document.xpath("cac:Attachment/cac:ExternalReference/cbc:URI/text()", namespaces=namespaces)
            
            if doc_id and url:
                doc_data = {
                    "id": doc_id[0],
                    "accessDetailsURL": url[0],
                    "relatedLots": [lot_id]
                }
                result["tender"]["documents"].append(doc_data)

    return result if result["tender"]["documents"] else None

def merge_documents_restricted_url(release_json, documents_data):
    """
    Merge the parsed documents restricted URL data into the main OCDS release JSON.

    This function updates the existing documents in the release JSON with the
    restricted URL information. If a document doesn't exist, it adds a new document to the release.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        documents_data (dict): The parsed documents restricted URL data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not documents_data:
        logger.warning("BT-615-Lot: No documents restricted URL data to merge")
        return

    existing_documents = release_json.setdefault("tender", {}).setdefault("documents", [])
    
    for new_doc in documents_data["tender"]["documents"]:
        existing_doc = next((doc for doc in existing_documents if doc["id"] == new_doc["id"]), None)
        if existing_doc:
            existing_doc["accessDetailsURL"] = new_doc["accessDetailsURL"]
            existing_doc.setdefault("relatedLots", []).extend(new_doc["relatedLots"])
            existing_doc["relatedLots"] = list(set(existing_doc["relatedLots"]))  # Remove duplicates
        else:
            existing_documents.append(new_doc)

    logger.info(f"BT-615-Lot: Merged documents restricted URL data for {len(documents_data['tender']['documents'])} documents")