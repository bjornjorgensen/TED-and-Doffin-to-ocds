# converters/BT_719_notice.py

import logging
from lxml import etree
from utils.date_utils import convert_to_iso_format

logger = logging.getLogger(__name__)


def parse_procurement_documents_change_date(xml_content):
    """
    Parse the XML content to extract the procurement documents change date.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed data in the format:
              {
                  "tender": {
                      "documents": [
                          {
                              "dateModified": "ISO_formatted_date",
                              "documentType": "biddingDocuments",
                              "relatedLots": ["LOT-XXXX"]  # Optional
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

    changes = root.xpath("//efac:Changes/efac:Change", namespaces=namespaces)

    for change in changes:
        date = change.xpath(
            "efbc:ProcurementDocumentsChangeDate/text()", namespaces=namespaces
        )
        if not date:
            continue

        # Specify is_start_date=True when calling convert_to_iso_format
        iso_date = convert_to_iso_format(date[0], is_start_date=True)

        lot_identifiers = change.xpath(
            "efac:ChangedSection/efbc:ChangedSectionIdentifier[starts-with(text(), 'LOT-')]/text()",
            namespaces=namespaces,
        )

        document = {"dateModified": iso_date, "documentType": "biddingDocuments"}

        if lot_identifiers:
            document["relatedLots"] = lot_identifiers

        result["tender"]["documents"].append(document)

    return result if result["tender"]["documents"] else None


def merge_procurement_documents_change_date(release_json, change_date_data):
    """
    Merge the parsed procurement documents change date data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        change_date_data (dict): The parsed change date data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not change_date_data:
        logger.warning("No procurement documents change date data to merge")
        return

    tender_documents = release_json.setdefault("tender", {}).setdefault("documents", [])

    for new_doc in change_date_data["tender"]["documents"]:
        if "relatedLots" in new_doc:
            for lot_id in new_doc["relatedLots"]:
                existing_doc = next(
                    (
                        doc
                        for doc in tender_documents
                        if doc.get("documentType") == "biddingDocuments"
                        and lot_id in doc.get("relatedLots", [])
                    ),
                    None,
                )
                if existing_doc:
                    existing_doc["dateModified"] = new_doc["dateModified"]
                else:
                    tender_documents.append(new_doc)
        else:
            existing_doc = next(
                (
                    doc
                    for doc in tender_documents
                    if doc.get("documentType") == "biddingDocuments"
                    and "relatedLots" not in doc
                ),
                None,
            )
            if existing_doc:
                existing_doc["dateModified"] = new_doc["dateModified"]
            else:
                tender_documents.append(new_doc)

    logger.info(
        f"Merged procurement documents change date data for {len(change_date_data['tender']['documents'])} documents"
    )
