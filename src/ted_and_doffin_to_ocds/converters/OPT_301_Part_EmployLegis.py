# converters/OPT_301_Part_EmployLegis.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_part_employlegis(xml_content):
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

    xpath = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingTerms/cac:EmploymentLegislationDocumentReference"
    employ_legis_refs = root.xpath(xpath, namespaces=namespaces)

    for ref in employ_legis_refs:
        doc_id = ref.xpath("cbc:ID/text()", namespaces=namespaces)
        doc_id = doc_id[0] if doc_id else None

        uri = ref.xpath(
            "cac:Attachment/cac:ExternalReference/cbc:URI/text()", namespaces=namespaces,
        )
        uri = uri[0] if uri else None

        if doc_id:
            document = {"id": doc_id}
            if uri:
                document["url"] = uri
            result["tender"]["documents"].append(document)

    return result if result["tender"]["documents"] else None


def merge_part_employlegis(release_json, employlegis_data):
    if not employlegis_data:
        logger.warning("No Part Employment Legislation data to merge")
        return

    # Merge documents
    existing_docs = {
        doc["id"]: doc for doc in release_json.get("tender", {}).get("documents", [])
    }
    for doc in employlegis_data["tender"]["documents"]:
        if doc["id"] in existing_docs:
            existing_docs[doc["id"]].update(doc)
        else:
            release_json.setdefault("tender", {}).setdefault("documents", []).append(
                doc,
            )

    logger.info(
        f"Merged Part Employment Legislation data for {len(employlegis_data['tender']['documents'])} documents",
    )
