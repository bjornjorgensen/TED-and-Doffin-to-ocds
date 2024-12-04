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

EINVOICING_MAPPING = {
    "required": "Required",
    "allowed": "Allowed",
    "notAllowed": "Not allowed",
}


def parse_lot_einvoicing_policy(xml_content: str | bytes) -> dict | None:
    """
    Parse BT-743: Electronic invoicing policy for lots.

    Extracts whether buyers will require, allow or not allow electronic invoices
    for each lot.

    Args:
        xml_content: XML content to parse, either as string or bytes

    Returns:
        Optional[Dict]: Parsed data in format:
            {
                "tender": {
                    "lots": [
                        {
                            "id": str,
                            "contractTerms": {
                                "electronicInvoicingPolicy": str  # one of: required, allowed, notAllowed
                            }
                        }
                    ]
                }
            }
        Returns None if no relevant data found or on error
    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = etree.fromstring(xml_content)
        result = {"tender": {"lots": []}}

        lots = root.xpath(
            "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
            namespaces=NAMESPACES,
        )

        for lot in lots:
            lot_id = lot.xpath("cbc:ID/text()", namespaces=NAMESPACES)[0]
            einvoicing_code = lot.xpath(
                ".//cac:ContractExecutionRequirement[cbc:ExecutionRequirementCode/@listName='einvoicing']"
                "/cbc:ExecutionRequirementCode/text()",
                namespaces=NAMESPACES,
            )

            if einvoicing_code:
                code = einvoicing_code[0]
                policy = EINVOICING_MAPPING.get(code)
                if policy:
                    logger.info(
                        "Found e-invoicing policy '%s' for lot %s", policy, lot_id
                    )
                    lot_data = {
                        "id": lot_id,
                        "contractTerms": {"electronicInvoicingPolicy": policy},
                    }
                    result["tender"]["lots"].append(lot_data)
                else:
                    logger.warning("Unknown e-invoicing code: %s", code)

        return result if result["tender"]["lots"] else None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing e-invoicing policy")
        return None


def merge_lot_einvoicing_policy(
    release_json: dict, einvoicing_data: dict | None
) -> None:
    """
    Merge electronic invoicing policy data into the release JSON.

    Updates or adds e-invoicing policies for lots.

    Args:
        release_json: Main OCDS release JSON to update
        einvoicing_data: E-invoicing policy data to merge, can be None

    Note:
        - Updates release_json in-place
        - Creates tender.lots array if needed
        - Updates existing lots' contractTerms
    """
    if not einvoicing_data:
        logger.warning("No electronic invoicing policy data to merge")
        return

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for new_lot in einvoicing_data["tender"]["lots"]:
        existing_lot = next((lot for lot in lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            contract_terms = existing_lot.setdefault("contractTerms", {})
            contract_terms["electronicInvoicingPolicy"] = new_lot["contractTerms"][
                "electronicInvoicingPolicy"
            ]
        else:
            lots.append(new_lot)

    logger.info(
        "Merged electronic invoicing policy data for %d lots",
        len(einvoicing_data["tender"]["lots"]),
    )
