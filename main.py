#main.py
import json
import uuid
from datetime import datetime
from lxml import etree
from converters.Common_operations import NoticeProcessor
from converters.BT_01 import parse_legal_basis
from converters.BT_03 import parse_form_type
from converters.BT_04 import parse_procedure_identifier
from converters.BT_05 import parse_notice_dispatch_date_time
from converters.BT_06 import parse_procurement_project_lot
from converters.BT_09 import parse_xml_to_json
from converters.BT_10 import parse_contract_xml
from converters.BT_11 import parse_buyer_legal_type
from converters.BT_88 import parse_procedure_features
from converters.BT_105 import parse_procurement_procedure_type
from converters.BT_106 import parse_accelerated_procedure
from converters.BT_109 import parse_framework_duration_justification
from converters.BT_111 import parse_framework_buyer_categories
from converters.BT_113 import parse_framework_max_participants
from converters.BT_115 import parse_gpa_coverage
from converters.BT_13713 import parse_result_lot_identifier
from converters.BT_13714 import parse_tender_lot_identifier
from converters.BT_1375 import parse_group_lot_identifier
from converters.BT_119 import parse_dps_termination
from converters.BT_120 import parse_no_negotiation_necessary
from converters.BT_122 import parse_electronic_auction_description
from converters.BT_123 import parse_electronic_auction_url
from converters.BT_124 import parse_tool_atypical_url
from converters.BT_125 import parse_previous_planning_identifiers
from converters.BT_1252 import parse_direct_award_justification
from converters.BT_127 import parse_future_notice_date
from converters.BT_13 import parse_additional_info_deadline
from converters.BT_130_131_1311 import parse_tender_deadlines_invitations
from converters.BT_132 import parse_public_opening_date
from converters.BT_133 import parse_public_opening_place
from converters.BT_134 import parse_public_opening_description
from converters.BT_135 import parse_direct_award_justification_text
from converters.BT_1351 import parse_procedure_accelerated_justification
from converters.BT_136 import parse_direct_award_justification_code
from converters.BT_137 import parse_purpose_lot_identifier
from converters.BT_14 import parse_documents_restricted
from converters.BT_140 import parse_change_reason_code_and_description
from converters.BT_142 import parse_winner_chosen
from converters.BT_144 import parse_not_awarded_reason
from converters.BT_145 import parse_contract_conclusion_date
from converters.BT_1451 import parse_winner_decision_date
from converters.BT_15 import parse_documents_url
from converters.BT_150 import parse_contract_identifier
from converters.BT_151 import parse_contract_url
from converters.BT_16 import parse_organisation_part_name
from converters.BT_160 import parse_concession_revenue_buyer
from converters.BT_162 import parse_concession_revenue_user
from converters.BT_163 import parse_concession_value_description
from converters.BT_165 import parse_winner_size
from converters.BT_17 import parse_submission_electronic
from converters.BT_171 import parse_tender_rank
from converters.BT_1711 import parse_tender_ranked
from converters.BT_18 import parse_submission_url
from converters.BT_19 import parse_submission_nonelectronic_justification
from converters.BT_191 import parse_country_origin
from converters.BT_193 import parse_tender_variant
from converters.BT_195 import parse_unpublished_identifier
from converters.BT_21 import parse_lot_lotgroup_part_and_procedure_title
from converters.BT_22 import parse_internal_identifiers
from converters.BT_23 import parse_main_nature

def main(xml_path, ocid_prefix):
    # Read the XML content from the file
    with open(xml_path, 'rb') as xml_file:
        xml_content = xml_file.read()

    # Initialize NoticeProcessor
    notice_processor = NoticeProcessor(ocid_prefix)

    # Create the release JSON
    release_json_str = notice_processor.create_release(xml_content)
    release_json = json.loads(release_json_str)  # Parse the JSON string into a dictionary
    
    # Parse the legal basis
    legal_basis = parse_legal_basis(xml_content)
    
    # Merge legal basis into the release JSON
    if legal_basis:
        release_json.setdefault('tender', {}).update(legal_basis)

    # Parse the form type
    form_type = parse_form_type(xml_content)
    
    # Merge form type into the release JSON
    if form_type:
        if form_type.get("tag"):
            release_json.setdefault("tag", []).extend(form_type["tag"])
        if form_type.get("tender"):
            release_json.setdefault("tender", {}).update(form_type["tender"])

    # Parse the procedure identifier
    procedure_identifier = parse_procedure_identifier(xml_content)
    
    # Merge procedure identifier into the release JSON
    if procedure_identifier:
        if procedure_identifier.get("tender"):
            release_json.setdefault("tender", {}).update(procedure_identifier["tender"])

    # Parse the notice dispatch date and time
    notice_dispatch_date_time = parse_notice_dispatch_date_time(xml_content)
    
    # Merge notice dispatch date and time into the release JSON
    if notice_dispatch_date_time:
        release_json.setdefault('date', notice_dispatch_date_time['date'])

    # Parse the procurement project lot
    procurement_project_lot = parse_procurement_project_lot(xml_content)
    
    # Merge procurement project lot into the release JSON
    if procurement_project_lot:
        valid_lots = [lot for lot in procurement_project_lot.get("lots", []) if lot.get("hasSustainability", False)]
        if valid_lots:
            release_json.setdefault("tender", {}).setdefault("lots", []).extend(valid_lots)
    
    # Parse the cross-border law information
    cross_border_law_info = parse_xml_to_json(xml_content)
    
    # Merge cross-border law information into the release JSON
    if cross_border_law_info:
        cross_border_law_dict = json.loads(cross_border_law_info)
        if cross_border_law_dict.get("tender"):
            release_json.setdefault("tender", {}).update(cross_border_law_dict["tender"])
    
    contract_info = parse_contract_xml(xml_content)
    if contract_info:
        if contract_info.get("parties"):
            for new_party in contract_info["parties"]:
                existing_party = next((party for party in release_json.get("parties", []) if party["id"] == new_party["id"]), None)
                if existing_party:
                    if "details" not in existing_party:
                        existing_party["details"] = {"classifications": []}
                    elif "classifications" not in existing_party["details"]:
                        existing_party["details"]["classifications"] = []
                    existing_party["details"]["classifications"].extend(new_party["details"]["classifications"])
                else:
                    release_json.setdefault("parties", []).append(new_party)

    buyer_legal_type_info = parse_buyer_legal_type(xml_content)
    if buyer_legal_type_info:
        for new_party in buyer_legal_type_info["parties"]:
            existing_party = next((party for party in release_json.get("parties", []) if party["id"] == new_party["id"]), None)
            if existing_party:
                if "details" not in existing_party:
                    existing_party["details"] = {"classifications": []}
                elif "classifications" not in existing_party["details"]:
                    existing_party["details"]["classifications"] = []
                existing_party["details"]["classifications"].extend(new_party["details"]["classifications"])
            else:
                release_json.setdefault("parties", []).append(new_party)

    # Parse the procedure features (BT-88)
    procedure_features = parse_procedure_features(xml_content)
    
    # Merge procedure features into the release JSON
    if procedure_features:
        release_json.setdefault("tender", {}).update(procedure_features["tender"])

    # Parse the procurement procedure type (BT-105)
    procurement_procedure_type = parse_procurement_procedure_type(xml_content)
    
    # Merge procurement procedure type into the release JSON
    if procurement_procedure_type:
        release_json.setdefault("tender", {}).update(procurement_procedure_type["tender"])

    # Parse the accelerated procedure (BT-106)
    accelerated_procedure = parse_accelerated_procedure(xml_content)
    
    # Merge accelerated procedure into the release JSON
    if accelerated_procedure:
        release_json.setdefault("tender", {}).update(accelerated_procedure["tender"])

    # Parse the framework duration justification (BT-109)
    framework_duration_justification = parse_framework_duration_justification(xml_content)
    
    # Merge framework duration justification into the release JSON
    if framework_duration_justification:
        existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
        new_lots = framework_duration_justification["tender"]["lots"]
        
        for new_lot in new_lots:
            existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
            if existing_lot:
                existing_lot.setdefault("techniques", {}).setdefault("frameworkAgreement", {}).update(new_lot["techniques"]["frameworkAgreement"])
            else:
                existing_lots.append(new_lot)    

    # Parse the framework buyer categories (BT-111)
    framework_buyer_categories = parse_framework_buyer_categories(xml_content)
    
    # Merge framework buyer categories into the release JSON
    if framework_buyer_categories:
        existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
        new_lots = framework_buyer_categories["tender"]["lots"]
        
        for new_lot in new_lots:
            existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
            if existing_lot:
                existing_lot.setdefault("techniques", {}).setdefault("frameworkAgreement", {}).update(new_lot["techniques"]["frameworkAgreement"])
            else:
                existing_lots.append(new_lot)     

    # Parse the framework maximum participants number (BT-113)
    framework_max_participants = parse_framework_max_participants(xml_content)
    
    # Merge framework maximum participants number into the release JSON
    if framework_max_participants:
        existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
        new_lots = framework_max_participants["tender"]["lots"]
        
        for new_lot in new_lots:
            existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
            if existing_lot:
                existing_lot.setdefault("techniques", {}).setdefault("frameworkAgreement", {}).update(new_lot["techniques"]["frameworkAgreement"])
            else:
                existing_lots.append(new_lot)                   

    # Parse the GPA coverage (BT-115)
    gpa_coverage = parse_gpa_coverage(xml_content)
    
    # Merge GPA coverage into the release JSON
    if gpa_coverage:
        if "lots" in gpa_coverage["tender"]:
            existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
            new_lots = gpa_coverage["tender"]["lots"]
            
            for new_lot in new_lots:
                existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
                if existing_lot:
                    existing_lot.setdefault("coveredBy", []).extend(new_lot["coveredBy"])
                else:
                    existing_lots.append(new_lot)
        
        if "coveredBy" in gpa_coverage["tender"]:
            release_json.setdefault("tender", {}).setdefault("coveredBy", []).extend(gpa_coverage["tender"]["coveredBy"])

    # Parse the Result Lot Identifier (BT-13713)
    result_lot_identifier = parse_result_lot_identifier(xml_content)
    
    # Merge Result Lot Identifier into the release JSON
    if result_lot_identifier:
        existing_awards = release_json.setdefault("awards", [])
        new_awards = result_lot_identifier["awards"]
        
        for new_award in new_awards:
            existing_award = next((a for a in existing_awards if a["id"] == new_award["id"]), None)
            if existing_award:
                existing_award.setdefault("relatedLots", []).extend(
                    lot for lot in new_award["relatedLots"] if lot not in existing_award.get("relatedLots", [])
                )
            else:
                existing_awards.append(new_award)
            
    # Parse the Tender Lot Identifier (BT-13714)
    tender_lot_identifier = parse_tender_lot_identifier(xml_content)
    
    # Merge Tender Lot Identifier into the release JSON
    if tender_lot_identifier:
        existing_bids = release_json.setdefault("bids", {}).setdefault("details", [])
        new_bids = tender_lot_identifier["bids"]["details"]
        
        for new_bid in new_bids:
            existing_bid = next((b for b in existing_bids if b["id"] == new_bid["id"]), None)
            if existing_bid:
                existing_bid.setdefault("relatedLots", []).extend(
                    lot for lot in new_bid["relatedLots"] if lot not in existing_bid.get("relatedLots", [])
                )
            else:
                existing_bids.append(new_bid)

    # Parse the Group Lot Identifier (BT-1375)
    try:
        group_lot_identifier = parse_group_lot_identifier(xml_content)
        
        # Merge Group Lot Identifier into the release JSON
        if group_lot_identifier:
            existing_lot_groups = release_json.setdefault("tender", {}).setdefault("lotGroups", [])
            new_lot_groups = group_lot_identifier["tender"]["lotGroups"]
            
            for new_group in new_lot_groups:
                existing_group = next((g for g in existing_lot_groups if g["id"] == new_group["id"]), None)
                if existing_group:
                    existing_group.setdefault("relatedLots", []).extend(
                        lot for lot in new_group["relatedLots"] if lot not in existing_group.get("relatedLots", [])
                    )
                else:
                    existing_lot_groups.append(new_group)
    except Exception as e:
        print(f"Error parsing Group Lot Identifier: {str(e)}")

    # Parse the Dynamic Purchasing System Termination (BT-119)
    try:
        dps_termination = parse_dps_termination(xml_content)
        
        # Merge Dynamic Purchasing System Termination into the release JSON
        if dps_termination:
            existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
            new_lots = dps_termination["tender"]["lots"]
            
            for new_lot in new_lots:
                existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
                if existing_lot:
                    existing_lot.setdefault("techniques", {}).setdefault("dynamicPurchasingSystem", {}).update(new_lot["techniques"]["dynamicPurchasingSystem"])
                else:
                    existing_lots.append(new_lot)
    except Exception as e:
        print(f"Error parsing Dynamic Purchasing System Termination: {str(e)}")   

    # Parse the No Negotiation Necessary (BT-120)
    try:
        no_negotiation_necessary = parse_no_negotiation_necessary(xml_content)
        
        # Merge No Negotiation Necessary into the release JSON
        if no_negotiation_necessary:
            existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
            new_lots = no_negotiation_necessary["tender"]["lots"]
            
            for new_lot in new_lots:
                existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
                if existing_lot:
                    existing_lot.setdefault("secondStage", {}).update(new_lot["secondStage"])
                else:
                    existing_lots.append(new_lot)
    except Exception as e:
        print(f"Error parsing No Negotiation Necessary: {str(e)}")    

    # Parse the Electronic Auction Description (BT-122)
    try:
        electronic_auction_description = parse_electronic_auction_description(xml_content)
        
        # Merge Electronic Auction Description into the release JSON
        if electronic_auction_description:
            existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
            new_lots = electronic_auction_description["tender"]["lots"]
            
            for new_lot in new_lots:
                existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
                if existing_lot:
                    existing_lot.setdefault("techniques", {}).setdefault("electronicAuction", {}).update(new_lot["techniques"]["electronicAuction"])
                else:
                    existing_lots.append(new_lot)
    except Exception as e:
        print(f"Error parsing Electronic Auction Description: {str(e)}") 

    # Parse the Electronic Auction URL (BT-123)
    try:
        electronic_auction_url = parse_electronic_auction_url(xml_content)
        
        # Merge Electronic Auction URL into the release JSON
        if electronic_auction_url:
            existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
            new_lots = electronic_auction_url["tender"]["lots"]
            
            for new_lot in new_lots:
                existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
                if existing_lot:
                    existing_lot.setdefault("techniques", {}).setdefault("electronicAuction", {}).update(new_lot["techniques"]["electronicAuction"])
                else:
                    existing_lots.append(new_lot)
    except Exception as e:
        print(f"Error parsing Electronic Auction URL: {str(e)}")

    # Parse the Tool Atypical URL (BT-124)
    try:
        tool_atypical_url = parse_tool_atypical_url(xml_content)
        
        # Merge Tool Atypical URL into the release JSON
        if tool_atypical_url:
            # Handle lot-specific information
            if "lots" in tool_atypical_url["tender"]:
                existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
                new_lots = tool_atypical_url["tender"]["lots"]
                
                for new_lot in new_lots:
                    existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
                    if existing_lot:
                        existing_lot.setdefault("communication", {}).update(new_lot["communication"])
                    else:
                        existing_lots.append(new_lot)
            
            # Handle part-specific information
            if "communication" in tool_atypical_url["tender"]:
                release_json.setdefault("tender", {}).setdefault("communication", {}).update(tool_atypical_url["tender"]["communication"])

    except Exception as e:
        print(f"Error parsing Tool Atypical URL: {str(e)}")

    # Parse the Previous Planning Identifiers (BT-125 and BT-1251)
    try:
        previous_planning_identifiers = parse_previous_planning_identifiers(xml_content)
        
        # Merge Previous Planning Identifiers into the release JSON
        if previous_planning_identifiers:
            existing_related_processes = release_json.setdefault("relatedProcesses", [])
            new_related_processes = previous_planning_identifiers["relatedProcesses"]
            
            for new_process in new_related_processes:
                existing_process = next((p for p in existing_related_processes if p["id"] == new_process["id"]), None)
                if existing_process:
                    existing_process.update(new_process)
                else:
                    existing_related_processes.append(new_process)

    except Exception as e:
        print(f"Error parsing Previous Planning Identifiers: {str(e)}")


    # Parse the Direct Award Justification Previous Procedure Identifier (BT-1252)
    try:
        direct_award_justification = parse_direct_award_justification(xml_content)
        
        # Merge Direct Award Justification into the release JSON
        if direct_award_justification:
            existing_related_processes = release_json.setdefault("relatedProcesses", [])
            new_related_processes = direct_award_justification["relatedProcesses"]
            
            # Find the highest existing id
            max_id = max([int(p["id"]) for p in existing_related_processes]) if existing_related_processes else 0
            
            for new_process in new_related_processes:
                max_id += 1
                new_process["id"] = str(max_id)
                existing_related_processes.append(new_process)

    except Exception as e:
        print(f"Error parsing Direct Award Justification: {str(e)}")

    # Parse the Future Notice Date (BT-127)
    try:
        future_notice_date = parse_future_notice_date(xml_content)
        
        # Merge Future Notice Date into the release JSON
        if future_notice_date:
            release_json.setdefault("tender", {}).setdefault("communication", {}).update(future_notice_date["tender"]["communication"])

    except Exception as e:
        print(f"Error parsing Future Notice Date: {str(e)}")

    # Parse the Additional Information Deadline (BT-13)
    try:
        additional_info_deadline = parse_additional_info_deadline(xml_content)
        
        # Merge Additional Information Deadline into the release JSON
        if additional_info_deadline:
            if "lots" in additional_info_deadline["tender"]:
                existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
                new_lots = additional_info_deadline["tender"]["lots"]
                
                for new_lot in new_lots:
                    existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
                    if existing_lot:
                        existing_lot.setdefault("enquiryPeriod", {}).update(new_lot["enquiryPeriod"])
                    else:
                        existing_lots.append(new_lot)
            
            if "enquiryPeriod" in additional_info_deadline["tender"]:
                release_json.setdefault("tender", {}).setdefault("enquiryPeriod", {}).update(additional_info_deadline["tender"]["enquiryPeriod"])

    except Exception as e:
        print(f"Error parsing Additional Information Deadline: {str(e)}")

    # Parse the Tender Deadlines and Invitations (BT-130, BT-131, BT-1311)
    try:
        tender_deadlines_invitations = parse_tender_deadlines_invitations(xml_content)
        
        # Merge Tender Deadlines and Invitations into the release JSON
        if tender_deadlines_invitations and "lots" in tender_deadlines_invitations["tender"]:
            existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
            new_lots = tender_deadlines_invitations["tender"]["lots"]
            
            for new_lot in new_lots:
                existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
                if existing_lot:
                    for key, value in new_lot.items():
                        if key != "id":
                            if isinstance(value, dict):
                                existing_lot.setdefault(key, {}).update(value)
                            else:
                                existing_lot[key] = value
                else:
                    existing_lots.append(new_lot)

    except Exception as e:
        print(f"Error parsing Tender Deadlines and Invitations: {str(e)}")

    # Parse the Public Opening Date (BT-132)
    try:
        public_opening_date = parse_public_opening_date(xml_content)
        
        # Merge Public Opening Date into the release JSON
        if public_opening_date and "lots" in public_opening_date["tender"]:
            existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
            new_lots = public_opening_date["tender"]["lots"]
            
            for new_lot in new_lots:
                existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
                if existing_lot:
                    existing_lot.setdefault("awardPeriod", {}).update(new_lot["awardPeriod"])
                    existing_lot.setdefault("bidOpening", {}).update(new_lot["bidOpening"])
                else:
                    existing_lots.append(new_lot)

    except Exception as e:
        print(f"Error parsing Public Opening Date: {str(e)}")

    # Parse the Public Opening Place (BT-133)
    try:
        public_opening_place = parse_public_opening_place(xml_content)
        
        # Merge Public Opening Place into the release JSON
        if public_opening_place and "lots" in public_opening_place["tender"]:
            existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
            new_lots = public_opening_place["tender"]["lots"]
            
            for new_lot in new_lots:
                existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
                if existing_lot:
                    existing_lot.setdefault("bidOpening", {}).setdefault("location", {}).update(new_lot["bidOpening"]["location"])
                else:
                    existing_lots.append(new_lot)

    except Exception as e:
        print(f"Error parsing Public Opening Place: {str(e)}")

    # Parse the Public Opening Description (BT-134)
    try:
        public_opening_description = parse_public_opening_description(xml_content)
        
        # Merge Public Opening Description into the release JSON
        if public_opening_description and "lots" in public_opening_description["tender"]:
            existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
            new_lots = public_opening_description["tender"]["lots"]
            
            for new_lot in new_lots:
                existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
                if existing_lot:
                    existing_lot.setdefault("bidOpening", {}).update(new_lot["bidOpening"])
                else:
                    existing_lots.append(new_lot)

    except Exception as e:
        print(f"Error parsing Public Opening Description: {str(e)}")

    # Parse the Direct Award Justification Text (BT-135)
    try:
        direct_award_justification = parse_direct_award_justification_text(xml_content)
        
        # Merge Direct Award Justification Text into the release JSON
        if direct_award_justification:
            release_json.setdefault("tender", {}).update(direct_award_justification["tender"])

    except Exception as e:
        print(f"Error parsing Direct Award Justification Text: {str(e)}")

    # Parse the Procedure Accelerated Justification (BT-1351)
    try:
        accelerated_justification = parse_procedure_accelerated_justification(xml_content)
        
        # Merge Procedure Accelerated Justification into the release JSON
        if accelerated_justification:
            tender = release_json.setdefault("tender", {})
            procedure = tender.setdefault("procedure", {})
            procedure.update(accelerated_justification["tender"]["procedure"])

    except Exception as e:
        print(f"Error parsing Procedure Accelerated Justification: {str(e)}")

    # Parse the Direct Award Justification Code (BT-136)
    try:
        direct_award_justification_code = parse_direct_award_justification_code(xml_content)
        
        # Merge Direct Award Justification Code into the release JSON
        if direct_award_justification_code:
            tender = release_json.setdefault("tender", {})
            tender.setdefault("procurementMethodRationaleClassifications", []).extend(
                direct_award_justification_code["tender"]["procurementMethodRationaleClassifications"]
            )

    except Exception as e:
        print(f"Error parsing Direct Award Justification Code: {str(e)}")

    # Parse the Purpose Lot Identifier (BT-137)
    try:
        purpose_lot_identifier = parse_purpose_lot_identifier(xml_content)
        
        # Merge Purpose Lot Identifier into the release JSON
        if purpose_lot_identifier:
            tender = release_json.setdefault("tender", {})
            
            # Handle lots
            if "lots" in purpose_lot_identifier["tender"]:
                existing_lots = tender.setdefault("lots", [])
                new_lots = purpose_lot_identifier["tender"]["lots"]
                for new_lot in new_lots:
                    if not any(existing_lot["id"] == new_lot["id"] for existing_lot in existing_lots):
                        existing_lots.append(new_lot)
            
            # Handle lot groups
            if "lotGroups" in purpose_lot_identifier["tender"]:
                existing_lot_groups = tender.setdefault("lotGroups", [])
                new_lot_groups = purpose_lot_identifier["tender"]["lotGroups"]
                for new_lot_group in new_lot_groups:
                    if not any(existing_group["id"] == new_lot_group["id"] for existing_group in existing_lot_groups):
                        existing_lot_groups.append(new_lot_group)
            
            # Handle parts
            if "id" in purpose_lot_identifier["tender"]:
                tender["id"] = purpose_lot_identifier["tender"]["id"]

    except Exception as e:
        print(f"Error parsing Purpose Lot Identifier: {str(e)}")

    # Parse the Documents Restricted (BT-14)
    try:
        documents_restricted = parse_documents_restricted(xml_content)
        
        # Merge Documents Restricted into the release JSON
        if documents_restricted and "documents" in documents_restricted["tender"]:
            existing_documents = release_json.setdefault("tender", {}).setdefault("documents", [])
            new_documents = documents_restricted["tender"]["documents"]
            
            for new_doc in new_documents:
                existing_doc = next((doc for doc in existing_documents if doc["id"] == new_doc["id"]), None)
                if existing_doc:
                    existing_doc.update(new_doc)
                    if "relatedLots" in new_doc:
                        existing_doc.setdefault("relatedLots", []).extend(
                            lot for lot in new_doc["relatedLots"] if lot not in existing_doc.get("relatedLots", [])
                        )
                else:
                    existing_documents.append(new_doc)

    except Exception as e:
        print(f"Error parsing Documents Restricted: {str(e)}")

    # Parse the Change Reason Code and Description (BT-140 and BT-141(a))
    try:
        change_data = parse_change_reason_code_and_description(xml_content)
        
        # Merge Change Reason Code and Description into the release JSON
        if change_data:
            # Merge tender amendments
            if "amendments" in change_data["tender"]:
                existing_amendments = release_json.setdefault("tender", {}).setdefault("amendments", [])
                new_amendments = change_data["tender"]["amendments"]
                for new_amendment in new_amendments:
                    new_amendment["id"] = str(len(existing_amendments) + 1)
                    existing_amendments.append(new_amendment)

            # Merge award amendments
            if "awards" in change_data:
                existing_awards = release_json.setdefault("awards", [])
                for new_award in change_data["awards"]:
                    existing_award = next((a for a in existing_awards if a["id"] == new_award["id"]), None)
                    if existing_award:
                        existing_award.setdefault("amendments", []).extend(new_award["amendments"])
                        for amendment in existing_award["amendments"]:
                            amendment["id"] = str(len(existing_award["amendments"]))
                    else:
                        for amendment in new_award["amendments"]:
                            amendment["id"] = str(len(new_award["amendments"]))
                        existing_awards.append(new_award)

    except Exception as e:
        print(f"Error parsing Change Reason Code and Description: {str(e)}")

    # Parse the Winner Chosen (BT-142)
    try:
        winner_chosen = parse_winner_chosen(xml_content)
        
        # Merge Winner Chosen into the release JSON
        if winner_chosen:
            # Merge lots
            if "lots" in winner_chosen["tender"]:
                existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
                for new_lot in winner_chosen["tender"]["lots"]:
                    existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
                    if existing_lot:
                        existing_lot.update(new_lot)
                    else:
                        existing_lots.append(new_lot)

            # Merge awards
            if "awards" in winner_chosen:
                existing_awards = release_json.setdefault("awards", [])
                for new_award in winner_chosen["awards"]:
                    existing_award = next((award for award in existing_awards if award["id"] == new_award["id"]), None)
                    if existing_award:
                        existing_award.update(new_award)
                    else:
                        existing_awards.append(new_award)

    except Exception as e:
        print(f"Error parsing Winner Chosen: {str(e)}")

    # Parse the Not Awarded Reason (BT-144)
    try:
        not_awarded_reason = parse_not_awarded_reason(xml_content)
        
        # Merge Not Awarded Reason into the release JSON
        if not_awarded_reason and "awards" in not_awarded_reason:
            existing_awards = release_json.setdefault("awards", [])
            for new_award in not_awarded_reason["awards"]:
                existing_award = next((award for award in existing_awards if award["id"] == new_award["id"]), None)
                if existing_award:
                    existing_award.update(new_award)
                else:
                    existing_awards.append(new_award)

    except Exception as e:
        print(f"Error parsing Not Awarded Reason: {str(e)}")

    # Parse the Contract Conclusion Date (BT-145)
    try:
        contract_conclusion_date = parse_contract_conclusion_date(xml_content)
        
        # Merge Contract Conclusion Date into the release JSON
        if contract_conclusion_date and "contracts" in contract_conclusion_date:
            existing_contracts = release_json.setdefault("contracts", [])
            for new_contract in contract_conclusion_date["contracts"]:
                existing_contract = next((contract for contract in existing_contracts if contract["id"] == new_contract["id"]), None)
                if existing_contract:
                    existing_contract.update(new_contract)
                else:
                    existing_contracts.append(new_contract)

    except Exception as e:
        print(f"Error parsing Contract Conclusion Date: {str(e)}")

    # Parse the Winner Decision Date (BT-1451)
    try:
        winner_decision_date = parse_winner_decision_date(xml_content)
        
        # Merge Winner Decision Date into the release JSON
        if winner_decision_date and "awards" in winner_decision_date:
            existing_awards = release_json.setdefault("awards", [])
            for new_award in winner_decision_date["awards"]:
                existing_award = next((award for award in existing_awards if award["id"] == new_award["id"]), None)
                if existing_award:
                    if "date" not in existing_award or new_award["date"] < existing_award["date"]:
                        existing_award["date"] = new_award["date"]
                    existing_award.setdefault("relatedLots", []).extend(
                        lot for lot in new_award["relatedLots"] if lot not in existing_award.get("relatedLots", [])
                    )
                else:
                    existing_awards.append(new_award)

    except Exception as e:
        print(f"Error parsing Winner Decision Date: {str(e)}")

    # Parse the Documents URL (BT-15)
    try:
        documents_url = parse_documents_url(xml_content)
        
        # Merge Documents URL into the release JSON
        if documents_url and "documents" in documents_url["tender"]:
            existing_documents = release_json.setdefault("tender", {}).setdefault("documents", [])
            for new_doc in documents_url["tender"]["documents"]:
                existing_doc = next((doc for doc in existing_documents if doc["id"] == new_doc["id"]), None)
                if existing_doc:
                    existing_doc.update(new_doc)
                    if "relatedLots" in new_doc:
                        existing_doc.setdefault("relatedLots", []).extend(
                            lot for lot in new_doc["relatedLots"] if lot not in existing_doc.get("relatedLots", [])
                        )
                else:
                    existing_documents.append(new_doc)

    except Exception as e:
        print(f"Error parsing Documents URL: {str(e)}")

    # Parse the Contract Identifier (BT-150)
    try:
        contract_identifier = parse_contract_identifier(xml_content)
        
        # Merge Contract Identifier into the release JSON
        if contract_identifier and "contracts" in contract_identifier:
            existing_contracts = release_json.setdefault("contracts", [])
            for new_contract in contract_identifier["contracts"]:
                existing_contract = next((contract for contract in existing_contracts if contract["id"] == new_contract["id"]), None)
                if existing_contract:
                    existing_contract.setdefault("identifiers", []).extend(new_contract["identifiers"])
                    if "awardID" in new_contract:
                        existing_contract["awardID"] = new_contract["awardID"]
                    elif "awardIDs" in new_contract:
                        existing_contract["awardIDs"] = new_contract["awardIDs"]
                else:
                    existing_contracts.append(new_contract)

    except Exception as e:
        print(f"Error parsing Contract Identifier: {str(e)}")

    # Parse the Contract URL (BT-151)
    try:
        contract_url = parse_contract_url(xml_content)
        
        # Merge Contract URL into the release JSON
        if contract_url and "contracts" in contract_url:
            existing_contracts = release_json.setdefault("contracts", [])
            for new_contract in contract_url["contracts"]:
                existing_contract = next((contract for contract in existing_contracts if contract["id"] == new_contract["id"]), None)
                if existing_contract:
                    if "documents" in new_contract:
                        existing_documents = existing_contract.setdefault("documents", [])
                        for new_document in new_contract["documents"]:
                            new_document["id"] = str(len(existing_documents) + 1)
                            existing_documents.append(new_document)
                    if "awardID" in new_contract:
                        existing_contract["awardID"] = new_contract["awardID"]
                    elif "awardIDs" in new_contract:
                        existing_contract["awardIDs"] = new_contract["awardIDs"]
                else:
                    if "documents" in new_contract and new_contract["documents"]:
                        new_contract["documents"][0]["id"] = "1"
                    existing_contracts.append(new_contract)

    except Exception as e:
        print(f"Error parsing Contract URL: {str(e)}")

    # Parse the Organisation Part Name (BT-16)
    try:
        organisation_part_name = parse_organisation_part_name(xml_content)
        
        # Merge Organisation Part Name into the release JSON
        if organisation_part_name and "parties" in organisation_part_name:
            existing_parties = release_json.setdefault("parties", [])
            for new_party in organisation_part_name["parties"]:
                existing_party = next((party for party in existing_parties if party["id"] == new_party["id"]), None)
                if existing_party:
                    existing_party["name"] = new_party["name"]
                    if "identifier" in new_party:
                        existing_party["identifier"] = new_party["identifier"]
                else:
                    existing_parties.append(new_party)

    except Exception as e:
        print(f"Error parsing Organisation Part Name: {str(e)}")

    # Parse the Concession Revenue Buyer (BT-160)
    try:
        concession_revenue_buyer = parse_concession_revenue_buyer(xml_content)
        
        # Merge Concession Revenue Buyer into the release JSON
        if concession_revenue_buyer and "contracts" in concession_revenue_buyer:
            existing_contracts = release_json.setdefault("contracts", [])
            for new_contract in concession_revenue_buyer["contracts"]:
                existing_contract = next((contract for contract in existing_contracts if contract["id"] == new_contract["id"]), None)
                if existing_contract:
                    existing_implementation = existing_contract.setdefault("implementation", {})
                    existing_charges = existing_implementation.setdefault("charges", [])
                    existing_charges.extend(new_contract["implementation"]["charges"])
                    if "awardID" in new_contract:
                        existing_contract["awardID"] = new_contract["awardID"]
                    elif "awardIDs" in new_contract:
                        existing_contract["awardIDs"] = new_contract["awardIDs"]
                else:
                    existing_contracts.append(new_contract)

    except Exception as e:
        print(f"Error parsing Concession Revenue Buyer: {str(e)}")

    # Parse the Concession Revenue User (BT-162)
    try:
        concession_revenue_user = parse_concession_revenue_user(xml_content)
        
        # Merge Concession Revenue User into the release JSON
        if concession_revenue_user and "contracts" in concession_revenue_user:
            existing_contracts = release_json.setdefault("contracts", [])
            for new_contract in concession_revenue_user["contracts"]:
                existing_contract = next((contract for contract in existing_contracts if contract["id"] == new_contract["id"]), None)
                if existing_contract:
                    existing_implementation = existing_contract.setdefault("implementation", {})
                    existing_charges = existing_implementation.setdefault("charges", [])
                    existing_charges.extend(new_contract["implementation"]["charges"])
                    if "awardID" in new_contract:
                        existing_contract["awardID"] = new_contract["awardID"]
                    elif "awardIDs" in new_contract:
                        existing_contract["awardIDs"] = new_contract["awardIDs"]
                else:
                    existing_contracts.append(new_contract)

    except Exception as e:
        print(f"Error parsing Concession Revenue User: {str(e)}")

    # Parse the Concession Value Description (BT-163)
    try:
        concession_value_description = parse_concession_value_description(xml_content)
        
        # Merge Concession Value Description into the release JSON
        if concession_value_description and "awards" in concession_value_description:
            existing_awards = release_json.setdefault("awards", [])
            for new_award in concession_value_description["awards"]:
                existing_award = next((award for award in existing_awards if award["id"] == new_award["id"]), None)
                if existing_award:
                    existing_award["valueCalculationMethod"] = new_award["valueCalculationMethod"]
                    existing_award.setdefault("relatedLots", []).extend(
                        lot for lot in new_award["relatedLots"] if lot not in existing_award.get("relatedLots", [])
                    )
                else:
                    existing_awards.append(new_award)

    except Exception as e:
        print(f"Error parsing Concession Value Description: {str(e)}")

    # Parse the Winner Size (BT-165)
    try:
        winner_size = parse_winner_size(xml_content)
        
        # Merge Winner Size into the release JSON
        if winner_size and "parties" in winner_size:
            existing_parties = release_json.setdefault("parties", [])
            for new_party in winner_size["parties"]:
                existing_party = next((party for party in existing_parties if party["id"] == new_party["id"]), None)
                if existing_party:
                    existing_party.setdefault("details", {}).update(new_party["details"])
                else:
                    existing_parties.append(new_party)

    except Exception as e:
        print(f"Error parsing Winner Size: {str(e)}")

    # Parse the SubmissionElectronic (BT-17)
    try:
        submission_electronic = parse_submission_electronic(xml_content)
        
        # Merge SubmissionElectronic into the release JSON
        if submission_electronic and "tender" in submission_electronic and "lots" in submission_electronic["tender"]:
            existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
            for new_lot in submission_electronic["tender"]["lots"]:
                existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
                if existing_lot:
                    existing_lot.setdefault("submissionTerms", {}).update(new_lot["submissionTerms"])
                else:
                    existing_lots.append(new_lot)

    except Exception as e:
        print(f"Error parsing SubmissionElectronic: {str(e)}")

    # Parse the Tender Rank (BT-171)
    try:
        tender_rank = parse_tender_rank(xml_content)
        
        # Merge Tender Rank into the release JSON
        if tender_rank and "bids" in tender_rank and "details" in tender_rank["bids"]:
            existing_bids = release_json.setdefault("bids", {}).setdefault("details", [])
            for new_bid in tender_rank["bids"]["details"]:
                existing_bid = next((bid for bid in existing_bids if bid["id"] == new_bid["id"]), None)
                if existing_bid:
                    existing_bid.update(new_bid)
                    existing_bid.setdefault("relatedLots", []).extend(
                        lot for lot in new_bid["relatedLots"] if lot not in existing_bid.get("relatedLots", [])
                    )
                else:
                    existing_bids.append(new_bid)

    except Exception as e:
        print(f"Error parsing Tender Rank: {str(e)}")

    # Parse the Tender Ranked (BT-1711)
    try:
        tender_ranked = parse_tender_ranked(xml_content)
        
        # Merge Tender Ranked into the release JSON
        if tender_ranked and "bids" in tender_ranked and "details" in tender_ranked["bids"]:
            existing_bids = release_json.setdefault("bids", {}).setdefault("details", [])
            for new_bid in tender_ranked["bids"]["details"]:
                existing_bid = next((bid for bid in existing_bids if bid["id"] == new_bid["id"]), None)
                if existing_bid:
                    existing_bid.update(new_bid)
                    existing_bid.setdefault("relatedLots", []).extend(
                        lot for lot in new_bid["relatedLots"] if lot not in existing_bid.get("relatedLots", [])
                    )
                else:
                    existing_bids.append(new_bid)

    except Exception as e:
        print(f"Error parsing Tender Ranked: {str(e)}")

    # Parse the Submission URL (BT-18)
    try:
        submission_url = parse_submission_url(xml_content)
        
        # Merge Submission URL into the release JSON
        if submission_url and "tender" in submission_url and "lots" in submission_url["tender"]:
            existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
            for new_lot in submission_url["tender"]["lots"]:
                existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
                if existing_lot:
                    existing_lot["submissionMethodDetails"] = new_lot["submissionMethodDetails"]
                else:
                    existing_lots.append(new_lot)

    except Exception as e:
        print(f"Error parsing Submission URL: {str(e)}")

    # Parse the Submission Nonelectronic Justification (BT-19)
    try:
        submission_nonelectronic_justification = parse_submission_nonelectronic_justification(xml_content)
        
        # Merge Submission Nonelectronic Justification into the release JSON
        if submission_nonelectronic_justification and "tender" in submission_nonelectronic_justification and "lots" in submission_nonelectronic_justification["tender"]:
            existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
            for new_lot in submission_nonelectronic_justification["tender"]["lots"]:
                existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
                if existing_lot:
                    existing_lot.setdefault("submissionTerms", {}).setdefault("nonElectronicSubmission", {}).update(new_lot["submissionTerms"]["nonElectronicSubmission"])
                else:
                    existing_lots.append(new_lot)

    except Exception as e:
        print(f"Error parsing Submission Nonelectronic Justification: {str(e)}")

    # Parse the Country Origin (BT-191)
    try:
        country_origin = parse_country_origin(xml_content)
        
        # Merge Country Origin into the release JSON
        if country_origin and "bids" in country_origin and "details" in country_origin["bids"]:
            existing_bids = release_json.setdefault("bids", {}).setdefault("details", [])
            for new_bid in country_origin["bids"]["details"]:
                existing_bid = next((bid for bid in existing_bids if bid["id"] == new_bid["id"]), None)
                if existing_bid:
                    existing_bid.setdefault("countriesOfOrigin", []).extend(
                        country for country in new_bid["countriesOfOrigin"] if country not in existing_bid.get("countriesOfOrigin", [])
                    )
                    existing_bid.setdefault("relatedLots", []).extend(
                        lot for lot in new_bid["relatedLots"] if lot not in existing_bid.get("relatedLots", [])
                    )
                else:
                    existing_bids.append(new_bid)

    except Exception as e:
        print(f"Error parsing Country Origin: {str(e)}")

    # Parse the Tender Variant (BT-193)
    try:
        tender_variant = parse_tender_variant(xml_content)
        
        # Merge Tender Variant into the release JSON
        if tender_variant and "bids" in tender_variant and "details" in tender_variant["bids"]:
            existing_bids = release_json.setdefault("bids", {}).setdefault("details", [])
            for new_bid in tender_variant["bids"]["details"]:
                existing_bid = next((bid for bid in existing_bids if bid["id"] == new_bid["id"]), None)
                if existing_bid:
                    existing_bid.update(new_bid)
                    existing_bid.setdefault("relatedLots", []).extend(
                        lot for lot in new_bid["relatedLots"] if lot not in existing_bid.get("relatedLots", [])
                    )
                else:
                    existing_bids.append(new_bid)

    except Exception as e:
        print(f"Error parsing Tender Variant: {str(e)}")


    # Parse the Unpublished Identifier (BT-195)
    try:
        unpublished_identifier = parse_unpublished_identifier(xml_content)
        
        # Merge Unpublished Identifier into the release JSON
        if unpublished_identifier and "withheldInformation" in unpublished_identifier:
            release_json.setdefault("withheldInformation", []).extend(unpublished_identifier["withheldInformation"])

    except Exception as e:
        print(f"Error parsing Unpublished Identifier: {str(e)}")

    # Parse the lot, lot group, part, and procedure titles (BT-21)
    titles = parse_lot_lotgroup_part_and_procedure_title(xml_content)
    # Merge lot, lot group, part, and procedure titles into the release JSON
    if titles and "tender" in titles:
        # Merge lots
        if "lots" in titles["tender"]:
            existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
            for new_lot in titles["tender"]["lots"]:
                existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
                if existing_lot:
                    existing_lot["title"] = new_lot["title"]
                else:
                    existing_lots.append(new_lot)
        
        # Merge lot groups
        if "lotGroups" in titles["tender"]:
            existing_lotgroups = release_json.setdefault("tender", {}).setdefault("lotGroups", [])
            for new_lotgroup in titles["tender"]["lotGroups"]:
                existing_lotgroup = next((lotgroup for lotgroup in existing_lotgroups if lotgroup["id"] == new_lotgroup["id"]), None)
                if existing_lotgroup:
                    existing_lotgroup["title"] = new_lotgroup["title"]
                else:
                    existing_lotgroups.append(new_lotgroup)
        
        # Merge tender title (Part or Procedure)
        if "title" in titles["tender"]:
            release_json.setdefault("tender", {})["title"] = titles["tender"]["title"]

    # Parse the internal identifiers (BT-22)
    internal_identifiers = parse_internal_identifiers(xml_content)
    # Merge internal identifiers into the release JSON
    if internal_identifiers and "tender" in internal_identifiers:
        # Merge lots
        if internal_identifiers["tender"]["lots"]:
            existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
            for new_lot in internal_identifiers["tender"]["lots"]:
                existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
                if existing_lot:
                    existing_lot.setdefault("identifiers", []).extend(new_lot["identifiers"])
                else:
                    existing_lots.append(new_lot)
    
    # Merge lot groups
    if internal_identifiers["tender"]["lotGroups"]:
        existing_lotgroups = release_json.setdefault("tender", {}).setdefault("lotGroups", [])
        for new_lotgroup in internal_identifiers["tender"]["lotGroups"]:
            existing_lotgroup = next((lotgroup for lotgroup in existing_lotgroups if lotgroup["id"] == new_lotgroup["id"]), None)
            if existing_lotgroup:
                existing_lotgroup.setdefault("identifiers", []).extend(new_lotgroup["identifiers"])
            else:
                existing_lotgroups.append(new_lotgroup)
    
    # Merge tender identifiers (Part and Procedure)
    if internal_identifiers["tender"]["identifiers"]:
        existing_identifiers = release_json.setdefault("tender", {}).setdefault("identifiers", [])
        for new_identifier in internal_identifiers["tender"]["identifiers"]:
            if new_identifier not in existing_identifiers:
                existing_identifiers.append(new_identifier)


    # Parse the main nature (BT-23)
    main_nature = parse_main_nature(xml_content)
    # Merge main nature into the release JSON
    if main_nature and "tender" in main_nature:
        # Merge lots
        if main_nature["tender"]["lots"]:
            existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
            for new_lot in main_nature["tender"]["lots"]:
                existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
                if existing_lot:
                    existing_lot["mainProcurementCategory"] = new_lot["mainProcurementCategory"]
                else:
                    existing_lots.append(new_lot)
    
    # Merge tender mainProcurementCategory (Part and Procedure)
    if "mainProcurementCategory" in main_nature["tender"]:
        release_json.setdefault("tender", {})["mainProcurementCategory"] = main_nature["tender"]["mainProcurementCategory"]

    # Write the JSON output to a file
    with open('output.json', 'w') as f:
        json.dump(release_json, f, indent=4)

    json_string = json.dumps(release_json, indent=2)
    print(json_string)
    
if __name__ == "__main__":
    # Path to the XML file
    xml_path = 'can_24_minimal.xml'
    # Prefix for OCID
    ocid_prefix = 'ocid_prefix_value'
    
    main(xml_path, ocid_prefix)