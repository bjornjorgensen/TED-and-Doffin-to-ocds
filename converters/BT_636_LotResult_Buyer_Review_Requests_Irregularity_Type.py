# converters/BT_636_LotResult_Buyer_Review_Requests_Irregularity_Type.py
from lxml import etree

IRREGULARITY_TYPE_MAPPING = {
    "ab-low": "Unjustified rejection of abnormally low tenders",
    "ar-split": "Artificial splitting of contracts",
    "bid-rigging": "Bid-rigging (established by a competition / anti-cartel office, a court or other competent body)",
    "change-eval": "Negotiation during the award procedure, including modification of the winning tender during evaluation",
    "conf-int": "Conflict of interest with impact on the outcome of the procurement procedure",
    "cp-mod-cond": "Competitive procedure with negotiation, with substantial modification of the conditions set out in the contract notice or tender specifications",
    "elem-mod": "Modifications of the contract elements set out in the contract notice or tender specifications, not in compliance with the relevant rules",
    "eva-add-crit": "Evaluation using additional award criteria that were not published",
    "eva-diff-crit": "Evaluation of tenders using award criteria that are different from the ones stated in the contract notice or tender specifications",
    "formal": "Formal",
    "ins-audit": "Insufficient audit trail for the award of the contract",
    "insuf-timl": "Insufficient time for potential tenderers/candidates to obtain the procurement documents",
    "irr-involv": "Irregular prior involvement of candidates or tenderers with the buyer",
    "mod-inco": "Selection criteria or technical specifications were modified after opening of tenders or were incorrectly applied",
    "nc-proc-eap": "Non-compliance with the procedure for electronic and aggregated procurement",
    "nc-timl": "Non-compliance with time limits for receipt of tenders or time limits for receipt of requests to participate",
    "ncompl-awcrit": "Failure to describe in sufficient detail the award criteria and their weighting",
    "ncompl-cn": "Failure to publish in the contract notice the technical specifications, selection criteria, award criteria (and their weighing), or contract performance conditions",
    "ncompl-com": "Failure to communicate and/or publish clarifications and/or additional information",
    "ncompl-sub": "Insufficient or imprecise definition of the subject matter of the contract",
    "no-notice": "Lack of publication of contract notice or unjustified direct award",
    "noex-addinfo": "Failure to extend time limits for receipt of tenders or requests to participate where additional information, although requested by the economic operator in good time, is not supplied at the latest six days before the time limit",
    "noex-timl": "Failure to extend time limits for receipt of tenders or requests to participate where significant changes are made to the procurement documents",
    "nojust-nolots": "Lack of justification for not subdividing contract into lots",
    "npub-limit": "Lack of publication of extended time limits for receipt of tenders or requests to participate",
    "other": "Other",
    "restr-not-tlim": "Restrictions to obtaining the procurement documents, other than insufficient time",
    "unj-comp-pro": "Unjustified use of competitive procedure with negotiation, competitive dialogue or innovative partnership",
    "unj-excl": "Unjustified exclusion of tenderers or candidates",
    "unj-lim-subc": "Unjustified limitation of subcontracting",
    "unj-na-ppr": "Unjustified non-application of public procurement rules",
    "unj-nrl": "Use of technical specification, selection criterion, award criterion, exclusion criterion, or contract performance condition that are discriminatory because of unjustified national, regional or local preferences",
    "unj-nrl-other": "Use of technical specifications, selection criteria, award criteria, exclusion criteria, or contract performance conditions that are discriminatory (i.e. restrict access for economic operators) for other reasons than unjustified national, regional or local preferences"
}

def parse_buyer_review_requests_irregularity_type(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = []

    lot_results = root.xpath("//efac:NoticeResult/efac:LotResult", namespaces=namespaces)
    for lot_result in lot_results:
        lot_id = lot_result.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
        irregularity_types = lot_result.xpath("efac:AppealRequestsStatistics[efbc:StatisticsCode/@listName='irregularity-type']/efbc:StatisticsCode/text()", namespaces=namespaces)
        
        if lot_id and irregularity_types:
            for irregularity_type in irregularity_types:
                result.append({
                    "lotId": lot_id[0],
                    "measure": irregularity_type,
                    "notes": IRREGULARITY_TYPE_MAPPING.get(irregularity_type, "Unknown irregularity type")
                })

    return result

def merge_buyer_review_requests_irregularity_type(release_json, irregularity_type_data):
    if irregularity_type_data:
        statistics = release_json.setdefault("statistics", [])
        
        # Find the highest existing id
        max_id = max([int(stat.get("id", 0)) for stat in statistics], default=0)

        for data in irregularity_type_data:
            # Check if a statistic for this lot and measure already exists
            existing_stat = next((stat for stat in statistics if stat.get("relatedLot") == data["lotId"] and stat.get("measure") == data["measure"] and stat.get("scope") == "complaints"), None)
            
            if existing_stat:
                existing_stat["notes"] = data["notes"]
            else:
                max_id += 1
                new_stat = {
                    "id": str(max_id),
                    "measure": data["measure"],
                    "scope": "complaints",
                    "notes": data["notes"],
                    "relatedLot": data["lotId"]
                }
                statistics.append(new_stat)

    return release_json