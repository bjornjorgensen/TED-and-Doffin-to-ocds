# converters/BT_707_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

JUSTIFICATION_MAPPING = {
    "ipr-iss": "Restricted. Intellectual property rights issues",
    "phy-mod": "Restricted. Inclusion of a physical model",
    "sen-info": "Restricted. Protection of particularly sensitive information",
    "sp-of-eq": "Restricted. Buyer would need specialised office equipment",
    "tdf-non-av": "Restricted. Tools, devices, or file formats not generally available",
}


def parse_lot_documents_restricted_justification(xml_content):
    """
    Parse the XML content to extract the documents restricted justification for each lot.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed data in the format:
              {
                  "tender": {
                      "documents": [
                          {
                              "id": "document_id",
                              "accessDetails": "justification",
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
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    result = {"tender": {"documents": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        documents = lot.xpath(
            "cac:TenderingTerms/cac:CallForTendersDocumentReference",
            namespaces=namespaces,
        )

        for doc in documents:
            doc_id = doc.xpath("cbc:ID/text()", namespaces=namespaces)[0]
            justification_code = doc.xpath(
                "cbc:DocumentTypeCode[@listName='communication-justification']/text()",
                namespaces=namespaces,
            )

            if justification_code:
                justification = JUSTIFICATION_MAPPING.get(
                    justification_code[0], "Unknown justification",
                )
                document = {
                    "id": doc_id,
                    "accessDetails": justification,
                    "relatedLots": [lot_id],
                }
                result["tender"]["documents"].append(document)

    return result if result["tender"]["documents"] else None


def merge_lot_documents_restricted_justification(release_json, lot_documents_data):
    """
    Merge the parsed lot documents restricted justification data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        lot_documents_data (dict): The parsed lot documents data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not lot_documents_data:
        logger.warning("No lot documents restricted justification data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_documents = tender.setdefault("documents", [])

    for new_doc in lot_documents_data["tender"]["documents"]:
        existing_doc = next(
            (doc for doc in existing_documents if doc["id"] == new_doc["id"]), None,
        )
        if existing_doc:
            existing_doc["accessDetails"] = new_doc["accessDetails"]
            existing_doc.setdefault("relatedLots", []).extend(new_doc["relatedLots"])
            existing_doc["relatedLots"] = list(
                set(existing_doc["relatedLots"]),
            )  # Remove duplicates
        else:
            existing_documents.append(new_doc)

    logger.info(
        f"Merged lot documents restricted justification data for {len(lot_documents_data['tender']['documents'])} documents",
    )
