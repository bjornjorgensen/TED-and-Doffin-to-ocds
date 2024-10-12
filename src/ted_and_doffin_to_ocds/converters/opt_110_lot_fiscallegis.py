# converters/opt_110_lot_fiscallegis.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_fiscal_legislation_url(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    # Check if the relevant XPath exists
    relevant_xpath = "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cac:FiscalLegislationDocumentReference"
    if not root.xpath(relevant_xpath, namespaces=namespaces):
        logger.info(
            "No fiscal legislation URL data found. Skipping parse_fiscal_legislation_url."
        )
        return None

    result = {"tender": {"documents": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces
    )
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        fiscal_docs = lot.xpath(
            "cac:TenderingTerms/cac:FiscalLegislationDocumentReference",
            namespaces=namespaces,
        )

        for doc in fiscal_docs:
            doc_id = doc.xpath("cbc:ID/text()", namespaces=namespaces)
            url = doc.xpath(
                "cac:Attachment/cac:ExternalReference/cbc:URI/text()",
                namespaces=namespaces,
            )

            if doc_id and url:
                document = {"id": doc_id[0], "url": url[0], "relatedLots": [lot_id]}
                result["tender"]["documents"].append(document)

    return result if result["tender"]["documents"] else None


def merge_fiscal_legislation_url(release_json, fiscal_legislation_url_data):
    if not fiscal_legislation_url_data:
        logger.info("No fiscal legislation URL data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_documents = tender.setdefault("documents", [])

    for new_doc in fiscal_legislation_url_data["tender"]["documents"]:
        existing_doc = next(
            (doc for doc in existing_documents if doc["id"] == new_doc["id"]), None
        )
        if existing_doc:
            existing_doc["url"] = new_doc["url"]
            existing_doc.setdefault("relatedLots", []).extend(
                lot_id
                for lot_id in new_doc["relatedLots"]
                if lot_id not in existing_doc["relatedLots"]
            )
        else:
            existing_documents.append(new_doc)

    logger.info(
        "Merged fiscal legislation URL data for %d documents",
        len(fiscal_legislation_url_data["tender"]["documents"]),
    )
