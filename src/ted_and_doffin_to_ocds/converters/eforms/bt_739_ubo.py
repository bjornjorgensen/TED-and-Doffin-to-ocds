# converters/bt_739_ubo.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
}


def parse_ubo_contact_fax(xml_content: str | bytes) -> dict | None:
    """Parse BT-739: Ultimate Beneficial Owner contact fax number.

    Extracts fax numbers for contacting UBOs, following data protection
    regulations regarding personal information.

    Args:
        xml_content: XML content to parse, either as string or bytes

    Returns:
        Optional[Dict]: Parsed data in format:
            {
                "parties": [
                    {
                        "id": str,  # organization ID
                        "beneficialOwners": [
                            {
                                "id": str,  # UBO ID
                                "faxNumber": str
                            }
                        ]
                    }
                ]
            }
        Returns None if no relevant data found or on error

    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = etree.fromstring(xml_content)
        result = {"parties": []}

        organizations = root.xpath(
            "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent"
            "/efext:EformsExtension/efac:Organizations/efac:Organization",
            namespaces=NAMESPACES,
        )

        for org in organizations:
            org_id = org.xpath(
                ".//cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()",
                namespaces=NAMESPACES,
            )

            if not org_id:
                continue

            ubos = []
            ubo_elements = root.xpath(
                "//efac:UltimateBeneficialOwner",
                namespaces=NAMESPACES,
            )

            for ubo in ubo_elements:
                ubo_id = ubo.xpath(
                    "cbc:ID[@schemeName='ubo']/text()",
                    namespaces=NAMESPACES,
                )
                fax = ubo.xpath(
                    "cac:Contact/cbc:Telefax/text()",
                    namespaces=NAMESPACES,
                )

                if ubo_id and fax:
                    fax_number = fax[0].strip()
                    logger.info("Found fax number %s for UBO %s", fax_number, ubo_id[0])
                    ubos.append({"id": ubo_id[0], "faxNumber": fax_number})

            if ubos:
                result["parties"].append({"id": org_id[0], "beneficialOwners": ubos})

        return result if result["parties"] else None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing UBO contact fax")
        return None


def merge_ubo_contact_fax(release_json: dict, ubo_data: dict | None) -> None:
    """Merge UBO fax number data into the release JSON.

    Updates or adds fax numbers to organization's beneficial owners.

    Args:
        release_json: Main OCDS release JSON to update
        ubo_data: UBO fax data to merge, can be None

    Note:
        - Updates release_json in-place
        - Creates parties array if needed
        - Updates existing organizations' beneficialOwners

    """
    if not ubo_data:
        logger.warning("No UBO contact fax data to merge")
        return

    parties = release_json.setdefault("parties", [])

    for new_party in ubo_data["parties"]:
        existing_party = next((p for p in parties if p["id"] == new_party["id"]), None)

        if existing_party:
            existing_ubos = existing_party.setdefault("beneficialOwners", [])
            for new_ubo in new_party["beneficialOwners"]:
                existing_ubo = next(
                    (u for u in existing_ubos if u["id"] == new_ubo["id"]), None
                )
                if existing_ubo:
                    existing_ubo["faxNumber"] = new_ubo["faxNumber"]
                else:
                    existing_ubos.append(new_ubo)
        else:
            parties.append(new_party)

    logger.info(
        "Merged UBO contact fax data for %d organizations", len(ubo_data["parties"])
    )
