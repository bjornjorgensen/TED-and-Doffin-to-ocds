# converters/bt_707_part.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
    "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
}

JUSTIFICATION_MAPPING = {
    "ipr-iss": "Restricted. Intellectual property rights issues",
    "phy-mod": "Restricted. Inclusion of a physical model",
    "sen-info": "Restricted. Protection of particularly sensitive information",
    "sp-of-eq": "Restricted. buyer would need specialised office equipment",
    "tdf-non-av": "Restricted. Tools, devices, or file formats not generally available",
}


def parse_part_documents_restricted_justification(xml_content):
    """
    Parse the XML content to extract the documents restricted justification for each part.

    Args:
        xml_content (str | bytes): The XML content to parse

    Returns:
        dict: A dictionary containing the parsed data in OCDS format, or None if no data found
    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")

        root = etree.fromstring(xml_content)
        result = {"tender": {"documents": []}}

        # Find all parts and their document references
        document_refs = root.xpath(
            """//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/
               cac:TenderingTerms/cac:CallForTendersDocumentReference""",
            namespaces=NAMESPACES,
        )

        for doc in document_refs:
            doc_id = doc.xpath("cbc:ID/text()", namespaces=NAMESPACES)
            justification = doc.xpath(
                """cbc:DocumentTypeCode[@listName='communication-justification']/
                   text()""",
                namespaces=NAMESPACES,
            )

            if doc_id and justification:
                document = {
                    "id": doc_id[0],
                    "accessDetails": JUSTIFICATION_MAPPING.get(
                        justification[0], "Unknown justification"
                    ),
                }
                result["tender"]["documents"].append(document)

        return result if result["tender"]["documents"] else None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise


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
        existing_doc = next(
            (doc for doc in existing_documents if doc["id"] == new_doc["id"]),
            None,
        )
        if existing_doc:
            existing_doc["accessDetails"] = new_doc["accessDetails"]
        else:
            existing_documents.append(new_doc)

    logger.info(
        "Merged part documents restricted justification data for %d documents",
        len(part_documents_data["tender"]["documents"]),
    )
