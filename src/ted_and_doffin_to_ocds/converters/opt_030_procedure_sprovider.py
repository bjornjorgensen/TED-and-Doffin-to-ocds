# converters/OPT_030_procedure_sprovider.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_provided_service_type(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

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

    result = {"parties": []}
    service_providers = root.xpath(
        "//cac:Contractingparty/cac:party/cac:ServiceProviderparty",
        namespaces=namespaces,
    )

    for provider in service_providers:
        service_type = provider.xpath(
            "cbc:ServiceTypeCode[@listName='organisation-role']/text()",
            namespaces=namespaces,
        )
        org_id = provider.xpath(
            "cac:party/cac:partyIdentification/cbc:ID/text()",
            namespaces=namespaces,
        )

        if service_type and org_id:
            role = None
            if service_type[0] == "serv-prov":
                role = "procurementServiceProvider"
            elif service_type[0] == "ted-esen":
                role = "eSender"

            if role:
                result["parties"].append({"id": org_id[0], "roles": [role]})

    return result if result["parties"] else None


def merge_provided_service_type(release_json, service_type_data):
    if not service_type_data:
        logger.warning("No Provided Service Type data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in service_type_data["parties"]:
        existing_party = next(
            (p for p in existing_parties if p["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_roles = set(existing_party.get("roles", []))
            existing_roles.update(new_party["roles"])
            existing_party["roles"] = list(existing_roles)
        else:
            existing_parties.append(new_party)

    logger.info(
        f"Merged Provided Service Type for {len(service_type_data['parties'])} parties",
    )
