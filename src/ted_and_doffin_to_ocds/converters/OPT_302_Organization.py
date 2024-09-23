# converters/OPT_302_Organization.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_beneficial_owner_reference(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    result = {"parties": []}
    organizations = root.xpath("//efac:Organization", namespaces=namespaces)

    for org in organizations:
        org_id = org.xpath(
            ".//efac:Company/cac:PartyIdentification/cbc:ID/text()",
            namespaces=namespaces,
        )
        ubo_id = org.xpath(
            ".//efac:UltimateBeneficialOwner/cbc:ID/text()", namespaces=namespaces,
        )

        if org_id and ubo_id:
            org_id = org_id[0]
            ubo_id = ubo_id[0]

            party = next((p for p in result["parties"] if p["id"] == org_id), None)
            if not party:
                party = {"id": org_id, "beneficialOwners": []}
                result["parties"].append(party)

            if not any(bo for bo in party["beneficialOwners"] if bo["id"] == ubo_id):
                party["beneficialOwners"].append({"id": ubo_id})

    return result if result["parties"] else None


def merge_beneficial_owner_reference(release_json, bo_reference_data):
    if not bo_reference_data:
        logger.warning("No Beneficial Owner Reference data to merge")
        return

    if "parties" not in release_json:
        release_json["parties"] = []

    for new_party in bo_reference_data["parties"]:
        existing_party = next(
            (
                party
                for party in release_json["parties"]
                if party["id"] == new_party["id"]
            ),
            None,
        )
        if existing_party:
            if "beneficialOwners" not in existing_party:
                existing_party["beneficialOwners"] = []
            for new_bo in new_party["beneficialOwners"]:
                if not any(
                    bo
                    for bo in existing_party["beneficialOwners"]
                    if bo["id"] == new_bo["id"]
                ):
                    existing_party["beneficialOwners"].append(new_bo)
        else:
            release_json["parties"].append(new_party)

    logger.info(
        f"Merged Beneficial Owner Reference data for {len(bo_reference_data['parties'])} parties",
    )
