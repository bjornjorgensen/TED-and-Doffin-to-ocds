# converters/opt_301_part_docprovider.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def part_parse_document_provider(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    xpath = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingTerms/cac:DocumentProviderParty/cac:PartyIdentification/cbc:ID[@schemeName='touchpoint']"
    document_providers = root.xpath(xpath, namespaces=namespaces)

    if not document_providers:
        logger.info("No Document Provider Technical Identifier found.")
        return None

    result = {"parties": []}
    for provider in document_providers:
        result["parties"].append(
            {"id": provider.text, "roles": ["processContactPoint"]}
        )

    return result


def part_merge_document_provider(release_json, document_provider_data):
    if not document_provider_data:
        logger.info("No Document Provider data to merge.")
        return

    parties = release_json.setdefault("parties", [])

    for new_party in document_provider_data["parties"]:
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]), None
        )
        if existing_party:
            if "processContactPoint" not in existing_party["roles"]:
                existing_party["roles"].append("processContactPoint")
        else:
            parties.append(new_party)

    logger.info(
        "Merged Document Provider data for %d parties.",
        len(document_provider_data["parties"]),
    )
