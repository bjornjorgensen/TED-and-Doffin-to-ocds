# converters/opt_110_part_fiscallegis.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_part_fiscal_legislation_url(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    # Check if the relevant XPath exists
    relevant_xpath = "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingTerms/cac:FiscalLegislationDocumentReference"
    if not root.xpath(relevant_xpath, namespaces=namespaces):
        logger.info(
            "No part fiscal legislation URL data found. Skipping parse_part_fiscal_legislation_url."
        )
        return None

    result = {"tender": {"documents": []}}

    fiscal_docs = root.xpath(relevant_xpath, namespaces=namespaces)
    for doc in fiscal_docs:
        doc_id = doc.xpath("cbc:ID/text()", namespaces=namespaces)
        url = doc.xpath(
            "cac:Attachment/cac:ExternalReference/cbc:URI/text()", namespaces=namespaces
        )

        if doc_id and url:
            document = {"id": doc_id[0], "url": url[0]}
            result["tender"]["documents"].append(document)

    return result if result["tender"]["documents"] else None


def merge_part_fiscal_legislation_url(
    release_json, part_fiscal_legislation_url_data
) -> None:
    if not part_fiscal_legislation_url_data:
        logger.info("No part fiscal legislation URL data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_documents = tender.setdefault("documents", [])

    for new_doc in part_fiscal_legislation_url_data["tender"]["documents"]:
        existing_doc = next(
            (doc for doc in existing_documents if doc["id"] == new_doc["id"]), None
        )
        if existing_doc:
            existing_doc["url"] = new_doc["url"]
        else:
            existing_documents.append(new_doc)

    logger.info(
        "Merged part fiscal legislation URL data for %d documents",
        len(part_fiscal_legislation_url_data["tender"]["documents"]),
    )
