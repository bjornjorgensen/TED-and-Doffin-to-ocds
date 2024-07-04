#main.py
import json, io
import uuid
from datetime import datetime
from lxml import etree
import logging
from converters.Common_operations import NoticeProcessor
from converters.BT_01 import parse_legal_basis
from converters.BT_03 import parse_form_type, merge_form_type
from converters.BT_04 import parse_procedure_identifier
from converters.BT_05_notice import parse_notice_dispatch_date_time, merge_notice_dispatch_date_time
from converters.BT_06_Lot import parse_strategic_procurement, merge_strategic_procurement
from converters.BT_09 import parse_xml_to_json
from converters.BT_10 import parse_contract_xml
from converters.BT_11_Procedure_Buyer import parse_buyer_legal_type, merge_buyer_legal_type
from converters.BT_88 import parse_procedure_features
from converters.BT_105 import parse_procurement_procedure_type
from converters.BT_106 import parse_accelerated_procedure
from converters.BT_109_Lot import parse_framework_duration_justification, merge_framework_duration_justification
from converters.BT_111_Lot import parse_framework_buyer_categories, merge_framework_buyer_categories
from converters.BT_113_Lot import parse_framework_max_participants, merge_framework_max_participants
from converters.BT_115_GPA_Coverage import parse_gpa_coverage, merge_gpa_coverage
from converters.BT_13713 import parse_result_lot_identifier, merge_result_lot_identifier
from converters.BT_13714_Tender import parse_tender_lot_identifier, merge_tender_lot_identifier
from converters.BT_1375_Procedure import parse_group_lot_identifier, merge_group_lot_identifier
from converters.BT_119_LotResult import parse_dps_termination, merge_dps_termination
from converters.BT_120_Lot import parse_no_negotiation_necessary, merge_no_negotiation_necessary
from converters.BT_122_Lot import parse_electronic_auction_description, merge_electronic_auction_description
from converters.BT_123_Lot import parse_electronic_auction_url, merge_electronic_auction_url
from converters.BT_124_Tool_Atypical_URL import parse_tool_atypical_url, merge_tool_atypical_url
from converters.BT_125_Lot import parse_previous_planning_identifier_lot, merge_previous_planning_identifier_lot
from converters.BT_125_Part import parse_previous_planning_identifier_part, merge_previous_planning_identifier_part
from converters.BT_1252_Procedure import parse_direct_award_justification, merge_direct_award_justification
from converters.BT_127_notice import parse_future_notice_date, merge_future_notice_date
from converters.BT_13_Lot import parse_additional_info_deadline, merge_additional_info_deadline
from converters.BT_13_Part import parse_additional_info_deadline_part, merge_additional_info_deadline_part
from converters.BT_130_131_1311 import parse_tender_deadlines_invitations
from converters.BT_132 import parse_public_opening_date
from converters.BT_133_Lot import parse_public_opening_place, merge_public_opening_place
from converters.BT_134 import parse_public_opening_description
from converters.BT_135 import parse_direct_award_justification_text
from converters.BT_1351 import parse_procedure_accelerated_justification
from converters.BT_136 import parse_direct_award_justification_code
from converters.BT_137_Purpose_Lot_Identifier import parse_purpose_lot_identifier, merge_purpose_lot_identifier
from converters.BT_14 import parse_documents_restricted
from converters.BT_140 import parse_change_reason_code_and_description
from converters.BT_142 import parse_winner_chosen
from converters.BT_144 import parse_not_awarded_reason
from converters.BT_145_Contract import parse_contract_conclusion_date, merge_contract_conclusion_date
from converters.BT_1451_Contract import parse_winner_decision_date, merge_winner_decision_date
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
from converters.BT_19_Lot import parse_nonelectronic_submission_justification, merge_nonelectronic_submission_justification
from converters.BT_191 import parse_country_origin
from converters.BT_193 import parse_tender_variant
from converters.BT_195 import parse_unpublished_identifier
from converters.BT_21 import parse_title, merge_title
from converters.BT_22 import parse_internal_identifiers, merge_internal_identifiers
from converters.BT_23 import parse_main_nature, merge_main_nature
from converters.BT_24 import parse_description, merge_description
from converters.BT_25 import parse_quantity, merge_quantity
from converters.BT_26 import parse_classifications, merge_classifications
from converters.BT_27 import parse_estimated_value, merge_estimated_value
from converters.BT_271 import parse_framework_maximum_value, merge_framework_maximum_value
from converters.BT_300 import parse_additional_information, merge_additional_information
from converters.BT_31 import parse_lots_max_allowed, merge_lots_max_allowed
from converters.BT_3201 import parse_tender_identifier, merge_tender_identifier
from converters.BT_3202 import parse_contract_tender_id, merge_contract_tender_id
from converters.BT_33 import parse_lots_max_awarded, merge_lots_max_awarded
from converters.BT_330 import parse_procedure_group_identifier, merge_procedure_group_identifier
from converters.BT_36 import parse_duration_period, merge_duration_period
from converters.BT_40 import parse_selection_criteria_second_stage, merge_selection_criteria_second_stage
from converters.BT_41 import parse_following_contract, merge_following_contract
from converters.BT_42 import parse_jury_decision_binding, merge_jury_decision_binding
from converters.BT_44 import parse_prize_rank, merge_prize_rank
from converters.BT_45 import parse_rewards_other, merge_rewards_other
from converters.BT_46 import parse_jury_member_name, merge_jury_member_name
from converters.BT_47 import parse_participant_name, merge_participant_name
from converters.BT_50 import parse_minimum_candidates, merge_minimum_candidates
from converters.BT_500 import parse_organization_info, merge_organization_info
from converters.BT_5010 import parse_eu_funds_financing_identifier, merge_eu_funds_financing_identifier
from converters.BT_5011 import parse_contract_eu_funds_financing_identifier, merge_contract_eu_funds_financing_identifier
from converters.BT_502_503_505_506_507 import parse_organization_contact_info, merge_organization_contact_info
from converters.BT_5071 import parse_place_performance_country_subdivision, merge_place_performance_country_subdivision
from converters.BT_508 import parse_buyer_profile_url, merge_buyer_profile_url
from converters.BT_509 import parse_edelivery_gateway, merge_edelivery_gateway
from converters.BT_51 import parse_maximum_candidates_number, merge_maximum_candidates_number
from converters.BT_510 import parse_street_address, merge_street_address
from converters.BT_5101 import parse_place_performance_street, merge_place_performance_street
from converters.BT_512 import parse_organization_post_code, merge_organization_post_code
from converters.BT_5121 import parse_place_performance_post_code, merge_place_performance_post_code
from converters.BT_513 import parse_organization_city, merge_organization_city
from converters.BT_5131 import parse_place_performance_city, merge_place_performance_city
from converters.BT_514 import parse_organization_country_code, merge_organization_country_code
from converters.BT_5141 import parse_place_performance_country_code, merge_place_performance_country_code
from converters.BT_52 import parse_successive_reduction_indicator, merge_successive_reduction_indicator
from converters.BT_531 import parse_additional_nature, merge_additional_nature
from converters.BT_536 import parse_duration_start_date, merge_duration_start_date
from converters.BT_537 import parse_duration_end_date, merge_duration_end_date
from converters.BT_538 import parse_duration_other, merge_duration_other
from converters.BT_539_Lot import parse_award_criterion_type_lot, merge_award_criterion_type_lot
from converters.BT_539_LotsGroup import parse_award_criterion_type_lots_group, merge_award_criterion_type_lots_group
from converters.BT_54_Lot import parse_options_description_lot, merge_options_description_lot
from converters.BT_540_Lot import parse_award_criterion_description_lot, merge_award_criterion_description_lot
from converters.BT_540_LotsGroup import parse_award_criterion_description_lots_group, merge_award_criterion_description_lots_group
from converters.BT_541_Lot import parse_award_criterion_numbers_lot, merge_award_criterion_numbers_lot
from converters.BT_541_LotsGroup import parse_award_criterion_numbers_lots_group, merge_award_criterion_numbers_lots_group
from converters.BT_5421_Lot import parse_award_criterion_number_weight_lot, merge_award_criterion_number_weight_lot
from converters.BT_5421_LotsGroup import parse_award_criterion_number_weight_lots_group, merge_award_criterion_number_weight_lots_group
from converters.BT_5422_Lot import parse_award_criterion_number_fixed_lot, merge_award_criterion_number_fixed_lot
from converters.BT_5422_LotsGroup import parse_award_criterion_number_fixed_lots_group, merge_award_criterion_number_fixed_lots_group
from converters.BT_5423_Lot import parse_award_criterion_number_threshold_lot, merge_award_criterion_number_threshold_lot
from converters.BT_5423_LotsGroup import parse_award_criterion_number_threshold_lots_group, merge_award_criterion_number_threshold_lots_group
from converters.BT_543_Lot import parse_award_criteria_complicated_lot, merge_award_criteria_complicated_lot
from converters.BT_543_LotsGroup import parse_award_criteria_complicated_lots_group, merge_award_criteria_complicated_lots_group
from converters.BT_553_Tender import parse_subcontracting_value, merge_subcontracting_value
from converters.BT_554_Tender import parse_subcontracting_description, merge_subcontracting_description
from converters.BT_555_Tender import parse_subcontracting_percentage, merge_subcontracting_percentage
from converters.BT_57_Lot import parse_renewal_description_lot, merge_renewal_description_lot
from converters.BT_58_Lot import parse_renewal_maximum_lot, merge_renewal_maximum_lot
from converters.BT_60_Lot import parse_eu_funds_lot, merge_eu_funds_lot
from converters.BT_610_Procedure_Buyer import parse_activity_entity, merge_activity_entity
from converters.BT_6110_Contract import parse_contract_eu_funds_details, merge_contract_eu_funds_details
from converters.BT_6140_Lot import parse_lot_eu_funds_details, merge_lot_eu_funds_details
from converters.BT_615_Documents_Restricted_URL import parse_documents_restricted_url, merge_documents_restricted_url
from converters.BT_625_Lot_Unit import parse_lot_unit, merge_lot_unit
from converters.BT_63_Lot_Variants import parse_lot_variants, merge_lot_variants
from converters.BT_630_Lot_Deadline_Receipt_Expressions import parse_lot_deadline_receipt_expressions, merge_lot_deadline_receipt_expressions
from converters.BT_631_Lot_Dispatch_Invitation_Interest import parse_lot_dispatch_invitation_interest, merge_lot_dispatch_invitation_interest
from converters.BT_632_Tool_Name import parse_tool_name, merge_tool_name
from converters.BT_633_Organization_Natural_Person import parse_organization_natural_person, merge_organization_natural_person
from converters.BT_635_LotResult_Buyer_Review_Requests_Count import parse_buyer_review_requests_count, merge_buyer_review_requests_count
from converters.BT_636_LotResult_Buyer_Review_Requests_Irregularity_Type import parse_buyer_review_requests_irregularity_type, merge_buyer_review_requests_irregularity_type
from converters.BT_64_Lot_Subcontracting_Obligation_Minimum import parse_subcontracting_obligation_minimum, merge_subcontracting_obligation_minimum
from converters.BT_644_Lot_Prize_Value import parse_lot_prize_value, merge_lot_prize_value
from converters.BT_65_Lot_Subcontracting_Obligation import parse_subcontracting_obligation, merge_subcontracting_obligation
from converters.BT_651_Lot_Subcontracting_Tender_Indication import parse_subcontracting_tender_indication, merge_subcontracting_tender_indication
from converters.BT_660_LotResult_Framework_Reestimated_Value import parse_framework_reestimated_value, merge_framework_reestimated_value
from converters.BT_67_Procedure_Exclusion_Grounds import parse_exclusion_grounds, merge_exclusion_grounds
from converters.BT_70_Lot_Terms_Performance import parse_terms_performance, merge_terms_performance
from converters.BT_702a_Notice_Official_Language import parse_notice_official_language, merge_notice_official_language
from converters.BT_706_UBO_Winner_Owner_Nationality import parse_winner_owner_nationality, merge_winner_owner_nationality
from converters.BT_707_Documents_Restricted_Justification import parse_documents_restricted_justification, merge_documents_restricted_justification
from converters.BT_708_Documents_Official_Language import parse_documents_official_language, merge_documents_official_language
from converters.BT_709_LotResult_Framework_Maximum_Value import parse_framework_maximum_value, merge_framework_maximum_value
from converters.BT_71_Reserved_Participation import parse_reserved_participation, merge_reserved_participation
from converters.BT_710_LotResult_Tender_Value_Lowest import parse_tender_value_lowest, merge_tender_value_lowest
from converters.BT_711_LotResult_Tender_Value_Highest import parse_tender_value_highest, merge_tender_value_highest
from converters.BT_712_LotResult_Buyer_Review_Complainants import parse_buyer_review_complainants, merge_buyer_review_complainants
from converters.BT_717_Lot_Clean_Vehicles_Directive import parse_clean_vehicles_directive, merge_clean_vehicles_directive
from converters.BT_719_Notice_Change_Procurement_Documents_Date import parse_change_procurement_documents_date, merge_change_procurement_documents_date
from converters.BT_720_Tender import parse_tender_value, merge_tender_value
from converters.BT_721_Contract_Title import parse_contract_title, merge_contract_title
from converters.BT_722_Contract_EU_Funds_Programme import parse_contract_eu_funds_programme, merge_contract_eu_funds_programme
from converters.BT_7220_Lot_EU_Funds_Programme import parse_lot_eu_funds_programme, merge_lot_eu_funds_programme
from converters.BT_723_LotResult_Vehicle_Category import parse_vehicle_category, merge_vehicle_category
from converters.BT_726_Suitable_For_SMEs import parse_suitable_for_smes, merge_suitable_for_smes
from converters.BT_727_Place_Performance_Services_Other import parse_place_performance_services_other, merge_place_performance_services_other
from converters.BT_728_Place_Performance_Additional_Info import parse_place_performance_additional_info, merge_place_performance_additional_info
from converters.BT_729_Lot_Subcontracting_Obligation_Maximum import parse_subcontracting_obligation_maximum, merge_subcontracting_obligation_maximum
from converters.BT_732_Lot_Security_Clearance_Description import parse_security_clearance_description, merge_security_clearance_description
from converters.BT_733_Award_Criteria_Order_Justification import parse_award_criteria_order_justification, merge_award_criteria_order_justification
from converters.BT_734_Award_Criterion_Name import parse_award_criterion_name, merge_award_criterion_name
from converters.BT_735_CVD_Contract_Type import parse_cvd_contract_type, merge_cvd_contract_type
from converters.BT_736_Reserved_Execution import parse_reserved_execution, merge_reserved_execution
from converters.BT_737_Documents_Unofficial_Language import parse_documents_unofficial_language, merge_documents_unofficial_language
from converters.BT_738_Notice_Preferred_Publication_Date import parse_notice_preferred_publication_date, merge_notice_preferred_publication_date
from converters.BT_739_Organization_Contact_Fax import parse_organization_contact_fax, merge_organization_contact_fax
from converters.BT_740_Buyer_Contracting_Entity import parse_buyer_contracting_entity, merge_buyer_contracting_entity
from converters.BT_743_Electronic_Invoicing import parse_electronic_invoicing, merge_electronic_invoicing
from converters.BT_744_Submission_Electronic_Signature import parse_submission_electronic_signature, merge_submission_electronic_signature
from converters.BT_745_Submission_Nonelectronic_Description import parse_submission_nonelectronic_description, merge_submission_nonelectronic_description
from converters.BT_746_Winner_Listed import parse_winner_listed, merge_winner_listed
from converters.BT_747_Selection_Criteria_Type import parse_selection_criteria_type, merge_selection_criteria_type
from converters.BT_749_Selection_Criteria_Name import parse_selection_criteria_name, merge_selection_criteria_name
from converters.BT_75_Lot import parse_guarantee_required_description, merge_guarantee_required_description
from converters.BT_750_Lot import parse_selection_criteria_description, merge_selection_criteria_description
from converters.BT_752_Lot import parse_selection_criteria_numbers, merge_selection_criteria_numbers
from converters.BT_7531_Lot import parse_selection_criteria_weight, merge_selection_criteria_weight
from converters.BT_7532_Lot import parse_selection_criteria_threshold, merge_selection_criteria_threshold
from converters.BT_754_Lot import parse_accessibility, merge_accessibility
from converters.BT_755_Lot import parse_accessibility_justification, merge_accessibility_justification
from converters.BT_756_Procedure import parse_pin_competition_termination, merge_pin_competition_termination
from converters.BT_759_LotResult import parse_received_submissions_count, merge_received_submissions_count
from converters.BT_76_Lot import parse_tenderer_legal_form, merge_tenderer_legal_form
from converters.BT_760_LotResult import parse_received_submissions_type, merge_received_submissions_type
from converters.BT_762_notice import parse_change_reason_description, merge_change_reason_description
from converters.BT_763_Procedure import parse_lots_all_required, merge_lots_all_required
from converters.BT_764_Lot import parse_submission_electronic_catalogue, merge_submission_electronic_catalogue
from converters.BT_765_Framework_Agreement import parse_framework_agreement, merge_framework_agreement
from converters.BT_766_Dynamic_Purchasing_System import parse_dynamic_purchasing_system, merge_dynamic_purchasing_system
from converters.BT_767_Lot import parse_electronic_auction, merge_electronic_auction
from converters.BT_769_Lot import parse_multiple_tenders, merge_multiple_tenders
from converters.BT_77_Lot import parse_terms_financial, merge_terms_financial
from converters.BT_771_Lot import parse_late_tenderer_information, merge_late_tenderer_information
from converters.BT_772_Lot import parse_late_tenderer_info_description, merge_late_tenderer_info_description
from converters.BT_773_Tender import parse_subcontracting, merge_subcontracting
from converters.BT_774_Lot import parse_green_procurement, merge_green_procurement
from converters.BT_775_Lot import parse_social_procurement, merge_social_procurement
from converters.BT_776_Lot import parse_procurement_innovation, merge_procurement_innovation
from converters.BT_777_Lot import parse_strategic_procurement_description, merge_strategic_procurement_description
from converters.BT_78_Lot import parse_security_clearance_deadline, merge_security_clearance_deadline
from converters.BT_79_Lot import parse_performing_staff_qualification, merge_performing_staff_qualification
from converters.BT_801_Lot import parse_non_disclosure_agreement, merge_non_disclosure_agreement
from converters.BT_802_Lot import parse_non_disclosure_agreement_description, merge_non_disclosure_agreement_description
from converters.BT_805_Lot import parse_green_procurement_criteria, merge_green_procurement_criteria
from converters.BT_88_Procedure import parse_procedure_features, merge_procedure_features
from converters.BT_92_Lot import parse_electronic_ordering, merge_electronic_ordering
from converters.BT_93_Lot import parse_electronic_payment, merge_electronic_payment
from converters.BT_94_Lot import parse_recurrence, merge_recurrence
from converters.BT_95_Lot import parse_recurrence_description, merge_recurrence_description
from converters.BT_97_Lot import parse_submission_language, merge_submission_language
from converters.BT_98_Lot import parse_tender_validity_deadline, merge_tender_validity_deadline
from converters.BT_99_Lot import parse_review_deadline_description, merge_review_deadline_description
from converters.BT_198_BT_105 import parse_unpublished_access_date, merge_unpublished_access_date
from converters.OPP_020_021_022_023_Contract import parse_essential_assets, merge_essential_assets
from converters.OPP_031_Tender import parse_contract_conditions, merge_contract_conditions
from converters.OPP_032_Tender import parse_revenues_allocation, merge_revenues_allocation
from converters.OPP_034_Tender import parse_penalties_and_rewards, merge_penalties_and_rewards
from converters.OPP_040_Procedure import parse_main_nature_sub_type, merge_main_nature_sub_type
from converters.OPP_050_Organization import parse_buyers_group_lead_indicator, merge_buyers_group_lead_indicator
from converters.OPP_051_Organization import parse_awarding_cpb_buyer_indicator, merge_awarding_cpb_buyer_indicator
from converters.OPP_052_Organization import parse_acquiring_cpb_buyer_indicator, merge_acquiring_cpb_buyer_indicator
from converters.OPP_080_Tender import parse_kilometers_public_transport, merge_kilometers_public_transport
from converters.OPP_090_Procedure import parse_previous_notice_identifier, merge_previous_notice_identifier
from converters.OPT_030_Procedure_SProvider import parse_provided_service_type, merge_provided_service_type
from converters.OPP_071_Lot import parse_quality_target_code, merge_quality_target_code
from converters.OPP_072_Lot import parse_quality_target_description, merge_quality_target_description
from converters.OPP_100_Contract import parse_framework_notice_identifier, merge_framework_notice_identifier
from converters.OPP_110_111_FiscalLegis import parse_fiscal_legislation, merge_fiscal_legislation
from converters.OPP_112_120_EnvironLegis import parse_environmental_legislation, merge_environmental_legislation
from converters.OPP_113_130_EmployLegis import parse_employment_legislation, merge_employment_legislation
from converters.OPP_140_ProcurementDocs import parse_procurement_documents, merge_procurement_documents
from converters.OPT_155_156_LotResult import parse_vehicle_type_and_numeric, merge_vehicle_type_and_numeric
from converters.OPT_160_UBO import parse_ubo_first_name, merge_ubo_first_name
from converters.OPT_170_Tenderer import parse_tendering_party_leader, merge_tendering_party_leader
from converters.OPT_200_Organization_Company import parse_organization_technical_identifier, merge_organization_technical_identifier
from converters.OPT_201_Organization_TouchPoint import parse_touchpoint_technical_identifier, merge_touchpoint_technical_identifier
from converters.OPT_202_UBO import parse_beneficial_owner_identifier, merge_beneficial_owner_identifier
from converters.opt_300 import parse_opt_300, merge_opt_300
from converters.OPT_301_Lot_AddInfo import parse_additional_info_provider_identifier, merge_additional_info_provider_identifier
from converters.OPT_301_Lot_DocProvider import parse_document_provider_identifier, merge_document_provider_identifier
from converters.OPT_301_Lot_EmployLegis import parse_employment_legislation_document_reference, merge_employment_legislation_document_reference
from converters.OPT_301_Lot_EnvironLegis import parse_environmental_legislation_document_reference, merge_environmental_legislation_document_reference
from converters.OPT_301_Lot_ReviewOrg import parse_review_org_identifier, merge_review_org_identifier
from converters.OPT_301_Lot_Mediator import parse_mediator_identifier, merge_mediator_identifier
from converters.OPT_301_Lot_ReviewInfo import parse_review_info_identifier, merge_review_info_identifier
from converters.OPT_301_Lot_TenderEval import parse_tender_evaluator_identifier, merge_tender_evaluator_identifier
from converters.OPT_301_Lot_TenderReceipt import parse_tender_recipient_identifier, merge_tender_recipient_identifier
# add more OPT 301 her

from converters.OPT_302_Organization import parse_beneficial_owner_reference, merge_beneficial_owner_reference
from converters.OPT_310_Tender import parse_tendering_party_id_reference, merge_tendering_party_id_reference
from converters.OPT_315_LotResult import parse_contract_identifier_reference, merge_contract_identifier_reference
from converters.OPT_316_Contract import parse_contract_technical_identifier, merge_contract_technical_identifier
from converters.OPT_320_LotResult import parse_tender_identifier_reference, merge_tender_identifier_reference



def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def remove_empty_elements(data):
    """
    Recursively remove empty lists, empty dicts, or None elements from a dictionary or list.
    """
    if isinstance(data, dict):
        return {
            key: remove_empty_elements(value)
            for key, value in data.items()
            if value and remove_empty_elements(value)
        }
    elif isinstance(data, list):
        return [
            remove_empty_elements(item)
            for item in data
            if item and remove_empty_elements(item)
        ]
    else:
        return data

def main(xml_path, ocid_prefix):
    # Read the XML content from the file
    with open(xml_path, 'rb') as xml_file:
        xml_content = xml_file.read()

    configure_logging()
    logger = logging.getLogger(__name__)
    logger.info(f"Starting XML to JSON conversion for file: {xml_path}")

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

    # Parse and merge BT-03 Form Type
    logger.info("Processing BT-03: Form Type")
    form_type_data = parse_form_type(xml_content)
    if form_type_data:
        merge_form_type(release_json, form_type_data)
    else:
        logger.warning("No Form Type data found")

    # Parse the procedure identifier
    procedure_identifier = parse_procedure_identifier(xml_content)
    
    # Merge procedure identifier into the release JSON
    if procedure_identifier:
        if procedure_identifier.get("tender"):
            release_json.setdefault("tender", {}).update(procedure_identifier["tender"])

    # Parse and merge BT-05-notice Notice Dispatch Date and Time
    logger.info("Processing BT-05-notice: Notice Dispatch Date and Time")
    dispatch_datetime_data = parse_notice_dispatch_date_time(xml_content)
    if dispatch_datetime_data:
        merge_notice_dispatch_date_time(release_json, dispatch_datetime_data)
    else:
        logger.warning("No Notice Dispatch Date and Time data found")

    # Parse and merge BT-06-Lot Strategic Procurement
    logger.info("Processing BT-06-Lot: Strategic Procurement")
    strategic_procurement_data = parse_strategic_procurement(xml_content)
    if strategic_procurement_data:
        merge_strategic_procurement(release_json, strategic_procurement_data)
    else:
        logger.warning("No Strategic Procurement data found")
    
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

    # Parse and merge BT-11-Procedure-Buyer Buyer Legal Type
    logger.info("Processing BT-11-Procedure-Buyer: Buyer Legal Type")
    buyer_legal_type_data = parse_buyer_legal_type(xml_content)
    if buyer_legal_type_data:
        merge_buyer_legal_type(release_json, buyer_legal_type_data)
    else:
        logger.warning("No Buyer Legal Type data found")

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

    # Parse and merge BT-109-Lot Framework Duration Justification
    logger.info("Processing BT-109-Lot: Framework Duration Justification")
    framework_duration_data = parse_framework_duration_justification(xml_content)
    if framework_duration_data:
        merge_framework_duration_justification(release_json, framework_duration_data)
    else:
        logger.warning("No Framework Duration Justification data found")

    # Parse and merge BT-111-Lot Framework Buyer Categories
    logger.info("Processing BT-111-Lot: Framework Buyer Categories")
    framework_buyer_categories_data = parse_framework_buyer_categories(xml_content)
    if framework_buyer_categories_data:
        merge_framework_buyer_categories(release_json, framework_buyer_categories_data)
    else:
        logger.warning("No Framework Buyer Categories data found")

    # Parse and merge BT-113-Lot Framework Maximum Participants Number
    logger.info("Processing BT-113-Lot: Framework Maximum Participants Number")
    max_participants_data = parse_framework_max_participants(xml_content)
    if max_participants_data:
        merge_framework_max_participants(release_json, max_participants_data)
    else:
        logger.warning("No Framework Maximum Participants data found")
        
    # Parse and merge BT-115 GPA Coverage
    logger.info("Processing BT-115: GPA Coverage")
    gpa_coverage_data = parse_gpa_coverage(xml_content)
    if gpa_coverage_data:
        merge_gpa_coverage(release_json, gpa_coverage_data)
    else:
        logger.warning("No GPA Coverage data found")

    # Parse the Result Lot Identifier (BT-13713)
    result_lot_identifier = parse_result_lot_identifier(xml_content)
    
    # Merge Result Lot Identifier into the release JSON
    if result_lot_identifier:
        merge_result_lot_identifier(release_json, result_lot_identifier)
    else:
        logger.warning("No Result Lot Identifier data found")
            
    # Parse and merge BT-13714-Tender Tender Lot Identifier
    logger.info("Processing BT-13714-Tender: Tender Lot Identifier")
    tender_lot_data = parse_tender_lot_identifier(xml_content)
    if tender_lot_data:
        merge_tender_lot_identifier(release_json, tender_lot_data)
    else:
        logger.warning("No Tender Lot Identifier data found")

    # Parse and merge BT-1375-Procedure Group Lot Identifier
    logger.info("Processing BT-1375-Procedure: Group Lot Identifier")
    group_lot_data = parse_group_lot_identifier(xml_content)
    if group_lot_data:
        merge_group_lot_identifier(release_json, group_lot_data)
    else:
        logger.warning("No Group Lot Identifier data found")

    # Parse and merge BT-119-LotResult DPS Termination
    logger.info("Processing BT-119-LotResult: DPS Termination")
    dps_termination_data = parse_dps_termination(xml_content)
    if dps_termination_data:
        merge_dps_termination(release_json, dps_termination_data)
    else:
        logger.warning("No DPS Termination data found")

    # Parse and merge BT-120-Lot No Negotiation Necessary
    logger.info("Processing BT-120-Lot: No Negotiation Necessary")
    no_negotiation_data = parse_no_negotiation_necessary(xml_content)
    if no_negotiation_data:
        merge_no_negotiation_necessary(release_json, no_negotiation_data)
    else:
        logger.warning("No No Negotiation Necessary data found")   

    # Parse and merge BT-122-Lot Electronic Auction Description
    logger.info("Processing BT-122-Lot: Electronic Auction Description")
    auction_description_data = parse_electronic_auction_description(xml_content)
    if auction_description_data:
        merge_electronic_auction_description(release_json, auction_description_data)
    else:
        logger.warning("No Electronic Auction Description data found")

    # Parse and merge BT-123-Lot Electronic Auction URL
    logger.info("Processing BT-123-Lot: Electronic Auction URL")
    auction_url_data = parse_electronic_auction_url(xml_content)
    if auction_url_data:
        merge_electronic_auction_url(release_json, auction_url_data)
    else:
        logger.warning("No Electronic Auction URL data found")

    # Parse and merge BT-124 Tool Atypical URL
    logger.info("Processing BT-124: Tool Atypical URL")
    atypical_url_data = parse_tool_atypical_url(xml_content)
    if atypical_url_data:
        merge_tool_atypical_url(release_json, atypical_url_data)
    else:
        logger.warning("No Tool Atypical URL data found")

    # Parse and merge BT-125(i)-Lot Previous Planning Identifier
    logger.info("Processing BT-125(i)-Lot: Previous Planning Identifier")
    previous_planning_lot_data = parse_previous_planning_identifier_lot(xml_content)
    if previous_planning_lot_data:
        merge_previous_planning_identifier_lot(release_json, previous_planning_lot_data)
    else:
        logger.warning("No Previous Planning Identifier (Lot) data found")

    # Parse and merge BT-125(i)-Part and BT-1251-Part Previous Planning Identifier
    logger.info("Processing BT-125(i)-Part and BT-1251-Part: Previous Planning Identifier")
    previous_planning_part_data = parse_previous_planning_identifier_part(xml_content)
    if previous_planning_part_data:
        #logger.info(f"Found {len(previous_planning_part_data['relatedProcesses'])} related processes for parts")
        #logger.info(f"Data before merge: {json.dumps(previous_planning_part_data, indent=2)}")
        merge_previous_planning_identifier_part(release_json, previous_planning_part_data)
        #logger.info(f"Data after merge: {json.dumps(release_json.get('relatedProcesses', []), indent=2)}")
    else:
        logger.warning("No Previous Planning Identifier (Part) data found")

    # Parse and merge BT-1252-Procedure Direct Award Justification
    logger.info("Processing BT-1252-Procedure: Direct Award Justification")
    direct_award_data = parse_direct_award_justification(xml_content)
    if direct_award_data:
        merge_direct_award_justification(release_json, direct_award_data)
    else:
        logger.warning("No Direct Award Justification data found")

    # Parse and merge BT-127 Future Notice Date
    logger.info("Processing BT-127: Future Notice Date")
    future_notice_date = parse_future_notice_date(xml_content)
    if future_notice_date:
        merge_future_notice_date(release_json, future_notice_date)
    else:
        logger.warning("No Future Notice Date found")

    # Parse and merge BT-13 Additional Information Deadline
    logger.info("Processing BT-13: Additional Information Deadline")
    lots_data = parse_additional_info_deadline(xml_content)
    if lots_data:
        merge_additional_info_deadline(release_json, lots_data)
    else:
        logger.warning("No Additional Information Deadline found")

    # Parse and merge BT-13 Additional Information Deadline (Part)
    logger.info("Processing BT-13: Additional Information Deadline (Part)")
    deadline_part = parse_additional_info_deadline_part(xml_content)
    if deadline_part:
        merge_additional_info_deadline_part(release_json, deadline_part)
    else:
        logger.warning("No Additional Information Deadline (Part) found")

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

    # Parse and merge BT-133-Lot Public Opening Place
    logger.info("Processing BT-133-Lot: Public Opening Place")
    public_opening_place_data = parse_public_opening_place(xml_content)
    if public_opening_place_data:
        merge_public_opening_place(release_json, public_opening_place_data)
    else:
        logger.warning("No Public Opening Place data found")

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

    # Parse and merge BT-137 Purpose Lot Identifier
    logger.info("Processing BT-137: Purpose Lot Identifier")
    purpose_lot_data = parse_purpose_lot_identifier(xml_content)
    if purpose_lot_data:
        merge_purpose_lot_identifier(release_json, purpose_lot_data)
    else:
        logger.warning("No Purpose Lot Identifier data found")

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

    # Parse and merge BT-145 Contract Conclusion Date
    logger.info("Processing BT-145: Contract Conclusion Date")
    contracts_data = parse_contract_conclusion_date(xml_content)
    if contracts_data:
        merge_contract_conclusion_date(release_json, contracts_data)
    else:
        logger.warning("No Contract Conclusion Date found")

    # Parse and merge BT-1451 Winner Decision Date
    logger.info("Processing BT-1451: Winner Decision Date")
    awards_data = parse_winner_decision_date(xml_content)
    if awards_data:
        merge_winner_decision_date(release_json, awards_data)
    else:
        logger.warning("No Winner Decision Date found")

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

    # Parse and merge BT-19-Lot Submission Nonelectronic Justification
    logger.info("Processing BT-19-Lot: Submission Nonelectronic Justification")
    justification_data = parse_nonelectronic_submission_justification(xml_content)
    if justification_data:
        merge_nonelectronic_submission_justification(release_json, justification_data)
    else:
        logger.warning("No Submission Nonelectronic Justification data found")

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
    title_data = parse_title(xml_content)
    if title_data:
        merge_title(release_json, title_data)

    # Parse and merge BT-22 Internal Identifiers
    logger.info("Processing BT-22: Internal Identifiers")
    internal_identifiers_data = parse_internal_identifiers(xml_content)
    merge_internal_identifiers(release_json, internal_identifiers_data)

    # Parse and merge BT-23 Main Nature
    logger.info("Processing BT-23: Main Nature")
    main_nature_data = parse_main_nature(xml_content)
    merge_main_nature(release_json, main_nature_data)

    # Parse and merge BT-24 Description
    logger.info("Processing BT-24: Description")
    description_data = parse_description(xml_content)
    merge_description(release_json, description_data)

    # Parse the quantity (BT-25)
    quantity_data = parse_quantity(xml_content)
    # Merge quantity into the release JSON
    merge_quantity(release_json, quantity_data)

    # Parse the classifications (BT-26)
    classification_data = parse_classifications(xml_content)
    # Merge classifications into the release JSON
    merge_classifications(release_json, classification_data)

    # Parse the estimated value (BT-27)
    estimated_value_data = parse_estimated_value(xml_content)
    # Merge estimated value into the release JSON
    merge_estimated_value(release_json, estimated_value_data)

    # Parse the framework maximum value (BT-271)
    framework_max_value_data = parse_framework_maximum_value(xml_content)
    # Merge framework maximum value into the release JSON
    merge_framework_maximum_value(release_json, framework_max_value_data)

    # Parse the additional information (BT-300)
    additional_info_data = parse_additional_information(xml_content)
    # Merge additional information into the release JSON
    merge_additional_information(release_json, additional_info_data)

    # Parse the lots max allowed (BT-31)
    lots_max_allowed_data = parse_lots_max_allowed(xml_content)
    # Merge lots max allowed into the release JSON
    merge_lots_max_allowed(release_json, lots_max_allowed_data)

    # Parse the tender identifier (BT-3201)
    tender_identifier_data = parse_tender_identifier(xml_content)
    # Merge tender identifier into the release JSON
    merge_tender_identifier(release_json, tender_identifier_data)

    # Parse the contract tender ID (BT-3202)
    contract_tender_id_data = parse_contract_tender_id(xml_content)
    # Merge contract tender ID into the release JSON
    merge_contract_tender_id(release_json, contract_tender_id_data)

    # Parse the lots max awarded (BT-33)
    lots_max_awarded_data = parse_lots_max_awarded(xml_content)
    # Merge lots max awarded into the release JSON
    merge_lots_max_awarded(release_json, lots_max_awarded_data)

    # Parse the procedure group identifier (BT-330)
    procedure_group_identifier_data = parse_procedure_group_identifier(xml_content)
    # Merge procedure group identifier into the release JSON
    merge_procedure_group_identifier(release_json, procedure_group_identifier_data)

    # Parse the duration period (BT-36)
    duration_period_data = parse_duration_period(xml_content)
    # Merge duration period into the release JSON
    merge_duration_period(release_json, duration_period_data)

    # Parse the selection criteria second stage (BT-40)
    selection_criteria_data = parse_selection_criteria_second_stage(xml_content)
    # Merge selection criteria second stage into the release JSON
    merge_selection_criteria_second_stage(release_json, selection_criteria_data)

    # Parse the following contract (BT-41)
    following_contract_data = parse_following_contract(xml_content)
    # Merge following contract into the release JSON
    merge_following_contract(release_json, following_contract_data)

    # Parse the jury decision binding (BT-42)
    jury_decision_binding_data = parse_jury_decision_binding(xml_content)
    # Merge jury decision binding into the release JSON
    merge_jury_decision_binding(release_json, jury_decision_binding_data)

    # Parse the prize rank (BT-44)
    prize_rank_data = parse_prize_rank(xml_content)
    # Merge prize rank into the release JSON
    merge_prize_rank(release_json, prize_rank_data)

    # Parse the rewards other (BT-45)
    rewards_other_data = parse_rewards_other(xml_content)
    # Merge rewards other into the release JSON
    merge_rewards_other(release_json, rewards_other_data)

    # Parse the jury member name (BT-46)
    jury_member_name_data = parse_jury_member_name(xml_content)
    # Merge jury member name into the release JSON
    merge_jury_member_name(release_json, jury_member_name_data)

    # Parse the participant name (BT-47)
    participant_name_data = parse_participant_name(xml_content)
    # Merge participant name into the release JSON
    merge_participant_name(release_json, participant_name_data)

    # Parse the minimum candidates (BT-50)
    minimum_candidates_data = parse_minimum_candidates(xml_content)
    # Merge minimum candidates into the release JSON
    merge_minimum_candidates(release_json, minimum_candidates_data)

   # Parse the organization info (BT-500 and BT-501)
    organization_info_data = parse_organization_info(xml_content)
    # Merge organization info into the release JSON
    merge_organization_info(release_json, organization_info_data)

    # Parse the EU funds financing identifier (BT-5010)
    eu_funds_data = parse_eu_funds_financing_identifier(xml_content)
    # Merge EU funds financing identifier into the release JSON
    merge_eu_funds_financing_identifier(release_json, eu_funds_data)

    # Parse the Contract EU funds financing identifier (BT-5011)
    contract_eu_funds_data = parse_contract_eu_funds_financing_identifier(xml_content)
    # Merge Contract EU funds financing identifier into the release JSON
    merge_contract_eu_funds_financing_identifier(release_json, contract_eu_funds_data)

    # Parse the organization contact info (BT-502, BT-503, BT-505, BT-506, and BT-507)
    contact_info_data = parse_organization_contact_info(xml_content)
    # Merge organization contact info into the release JSON
    merge_organization_contact_info(release_json, contact_info_data)
    
    # Parse the place performance country subdivision (BT-5071)
    place_performance_data = parse_place_performance_country_subdivision(xml_content)
    # Merge place performance country subdivision into the release JSON
    merge_place_performance_country_subdivision(release_json, place_performance_data)
    
    # Parse the buyer profile URL (BT-508)
    buyer_profile_data = parse_buyer_profile_url(xml_content)
    # Merge buyer profile URL into the release JSON
    merge_buyer_profile_url(release_json, buyer_profile_data)

    # Parse the eDelivery Gateway (BT-509)
    edelivery_gateway_data = parse_edelivery_gateway(xml_content)
    # Merge eDelivery Gateway into the release JSON
    merge_edelivery_gateway(release_json, edelivery_gateway_data)

    # Parse the maximum candidates number (BT-51)
    maximum_candidates_data = parse_maximum_candidates_number(xml_content)
    # Merge maximum candidates number into the release JSON
    merge_maximum_candidates_number(release_json, maximum_candidates_data)

    # Parse the street address (BT-510)
    street_address_data = parse_street_address(xml_content)
    # Merge street address into the release JSON
    merge_street_address(release_json, street_address_data)

    # Parse the place performance street (BT-5101)
    place_performance_street_data = parse_place_performance_street(xml_content)
    # Merge place performance street into the release JSON
    merge_place_performance_street(release_json, place_performance_street_data)

    # Parse the organization post code (BT-512)
    post_code_data = parse_organization_post_code(xml_content)
    # Merge organization post code into the release JSON
    merge_organization_post_code(release_json, post_code_data)

    # Parse the place performance post code (BT-5121)
    place_performance_post_code_data = parse_place_performance_post_code(xml_content)
    # Merge place performance post code into the release JSON
    merge_place_performance_post_code(release_json, place_performance_post_code_data)

    # Parse the organization city (BT-513)
    city_data = parse_organization_city(xml_content)
    # Merge organization city into the release JSON
    merge_organization_city(release_json, city_data)

    # Parse the place performance city (BT-5131)
    place_performance_city_data = parse_place_performance_city(xml_content)
    # Merge place performance city into the release JSON
    merge_place_performance_city(release_json, place_performance_city_data)

    # Parse the organization country code (BT-514)
    country_code_data = parse_organization_country_code(xml_content)
    # Merge organization country code into the release JSON
    merge_organization_country_code(release_json, country_code_data)

    # Parse the place performance country code (BT-5141)
    place_performance_country_code_data = parse_place_performance_country_code(xml_content)
    # Merge place performance country code into the release JSON
    merge_place_performance_country_code(release_json, place_performance_country_code_data)

    # Parse the successive reduction indicator (BT-52)
    successive_reduction_data = parse_successive_reduction_indicator(xml_content)
    # Merge successive reduction indicator into the release JSON
    merge_successive_reduction_indicator(release_json, successive_reduction_data)

    # Parse the additional nature (BT-531)
    additional_nature_data = parse_additional_nature(xml_content)
    # Merge additional nature into the release JSON
    merge_additional_nature(release_json, additional_nature_data)

    # Parse and merge the duration start date for Lot (BT-536-Lot)
    duration_start_date_lot_data = parse_duration_start_date(xml_content, scheme_name="Lot")
    merge_duration_start_date(release_json, duration_start_date_lot_data, scheme_name="Lot")

    # Parse and merge the duration start date for Part (BT-536-Part)
    duration_start_date_part_data = parse_duration_start_date(xml_content, scheme_name="Part")
    merge_duration_start_date(release_json, duration_start_date_part_data, scheme_name="Part")

    # Parse and merge the duration end date for Lot (BT-537-Lot)
    duration_end_date_lot_data = parse_duration_end_date(xml_content, scheme_name="Lot")
    merge_duration_end_date(release_json, duration_end_date_lot_data, scheme_name="Lot")

    # Parse and merge the duration end date for Part (BT-537-Part)
    duration_end_date_part_data = parse_duration_end_date(xml_content, scheme_name="Part")
    merge_duration_end_date(release_json, duration_end_date_part_data, scheme_name="Part")

    # Parse and merge the duration other for Lot (BT-538-Lot)
    duration_other_lot_data = parse_duration_other(xml_content, scheme_name="Lot")
    merge_duration_other(release_json, duration_other_lot_data, scheme_name="Lot")

    # Parse and merge the duration other for Part (BT-538-Part)
    duration_other_part_data = parse_duration_other(xml_content, scheme_name="Part")
    merge_duration_other(release_json, duration_other_part_data, scheme_name="Part")

    # Parse and merge BT-539-Lot
    lot_criterion_data = parse_award_criterion_type_lot(xml_content)
    merge_award_criterion_type_lot(release_json, lot_criterion_data)

    # Parse and merge BT-539-LotsGroup
    lots_group_criterion_data = parse_award_criterion_type_lots_group(xml_content)
    merge_award_criterion_type_lots_group(release_json, lots_group_criterion_data)

    # Parse and merge BT-54-Lot
    options_description_data = parse_options_description_lot(xml_content)
    merge_options_description_lot(release_json, options_description_data)

    # Parse and merge BT-540-Lot
    lot_criterion_description_data = parse_award_criterion_description_lot(xml_content)
    merge_award_criterion_description_lot(release_json, lot_criterion_description_data)

    # Parse and merge BT-540-LotsGroup
    lots_group_criterion_description_data = parse_award_criterion_description_lots_group(xml_content)
    merge_award_criterion_description_lots_group(release_json, lots_group_criterion_description_data)

    # Parse and merge BT-541-Lot
    lot_criterion_numbers_data = parse_award_criterion_numbers_lot(xml_content)
    merge_award_criterion_numbers_lot(release_json, lot_criterion_numbers_data)

    # Parse and merge BT-541-LotsGroup
    lots_group_criterion_numbers_data = parse_award_criterion_numbers_lots_group(xml_content)
    merge_award_criterion_numbers_lots_group(release_json, lots_group_criterion_numbers_data)

    # Parse and merge BT-5421-Lot
    lot_criterion_weight_data = parse_award_criterion_number_weight_lot(xml_content)
    merge_award_criterion_number_weight_lot(release_json, lot_criterion_weight_data)

    # Parse and merge BT-5421-LotsGroup
    lots_group_criterion_weight_data = parse_award_criterion_number_weight_lots_group(xml_content)
    merge_award_criterion_number_weight_lots_group(release_json, lots_group_criterion_weight_data)

    # Parse and merge BT-5422-Lot
    lot_criterion_fixed_data = parse_award_criterion_number_fixed_lot(xml_content)
    merge_award_criterion_number_fixed_lot(release_json, lot_criterion_fixed_data)

    # Parse and merge BT-5422-LotsGroup
    lots_group_criterion_fixed_data = parse_award_criterion_number_fixed_lots_group(xml_content)
    merge_award_criterion_number_fixed_lots_group(release_json, lots_group_criterion_fixed_data)

    # Parse and merge BT-5423-Lot
    lot_criterion_threshold_data = parse_award_criterion_number_threshold_lot(xml_content)
    merge_award_criterion_number_threshold_lot(release_json, lot_criterion_threshold_data)

    # Parse and merge BT-5423-LotsGroup
    lots_group_criterion_threshold_data = parse_award_criterion_number_threshold_lots_group(xml_content)
    merge_award_criterion_number_threshold_lots_group(release_json, lots_group_criterion_threshold_data)

    # Parse and merge BT-543-Lot
    lot_criteria_complicated_data = parse_award_criteria_complicated_lot(xml_content)
    merge_award_criteria_complicated_lot(release_json, lot_criteria_complicated_data)

    # Parse and merge BT-543-LotsGroup
    lots_group_criteria_complicated_data = parse_award_criteria_complicated_lots_group(xml_content)
    merge_award_criteria_complicated_lots_group(release_json, lots_group_criteria_complicated_data)

    # Parse and merge BT-553-Tender
    subcontracting_value_data = parse_subcontracting_value(xml_content)
    merge_subcontracting_value(release_json, subcontracting_value_data)

    # Parse and merge BT-554-Tender
    subcontracting_description_data = parse_subcontracting_description(xml_content)
    merge_subcontracting_description(release_json, subcontracting_description_data)

    # Parse and merge BT-555-Tender
    subcontracting_percentage_data = parse_subcontracting_percentage(xml_content)
    merge_subcontracting_percentage(release_json, subcontracting_percentage_data)

    # Parse and merge BT-57-Lot
    renewal_description_data = parse_renewal_description_lot(xml_content)
    merge_renewal_description_lot(release_json, renewal_description_data)

    # Parse and merge BT-58-Lot
    renewal_maximum_data = parse_renewal_maximum_lot(xml_content)
    merge_renewal_maximum_lot(release_json, renewal_maximum_data)

    # Parse and merge BT-60-Lot
    eu_funded_data = parse_eu_funds_lot(xml_content)
    merge_eu_funds_lot(release_json, eu_funded_data)

    # Parse and merge BT-610-Procedure-Buyer
    activity_entity_data = parse_activity_entity(xml_content)
    merge_activity_entity(release_json, activity_entity_data)

    # Parse and merge BT-6110-Contract
    logger.info("Processing BT-6110-Contract: Contract EU Funds Details")
    contract_eu_funds_data = parse_contract_eu_funds_details(xml_content)
    if contract_eu_funds_data:
        merge_contract_eu_funds_details(release_json, contract_eu_funds_data)
    else:
        logger.warning("No Contract EU Funds data found")

    # Parse and merge BT-6140-Lot
    lot_eu_funds_data = parse_lot_eu_funds_details(xml_content)
    merge_lot_eu_funds_details(release_json, lot_eu_funds_data)

    # Parse and merge BT-615 Documents Restricted URL
    documents_restricted_url_data = parse_documents_restricted_url(xml_content)
    merge_documents_restricted_url(release_json, documents_restricted_url_data)

    # Parse and merge BT-625-Lot Unit
    lot_unit_data = parse_lot_unit(xml_content)
    merge_lot_unit(release_json, lot_unit_data)

    # Parse and merge BT-63-Lot Variants
    lot_variants_data = parse_lot_variants(xml_content)
    merge_lot_variants(release_json, lot_variants_data)

    # Parse and merge BT-630-Lot Deadline Receipt Expressions
    lot_deadline_receipt_expressions_data = parse_lot_deadline_receipt_expressions(xml_content)
    merge_lot_deadline_receipt_expressions(release_json, lot_deadline_receipt_expressions_data)

    # Parse and merge BT-631-Lot Dispatch Invitation Interest
    lot_dispatch_invitation_interest_data = parse_lot_dispatch_invitation_interest(xml_content)
    merge_lot_dispatch_invitation_interest(release_json, lot_dispatch_invitation_interest_data)

    # Parse and merge BT-632 Tool Name
    tool_name_data = parse_tool_name(xml_content)
    merge_tool_name(release_json, tool_name_data)

    # Parse and merge BT-633-Organization Natural Person
    organization_natural_person_data = parse_organization_natural_person(xml_content)
    merge_organization_natural_person(release_json, organization_natural_person_data)

    # Parse and merge BT-635-LotResult Buyer Review Requests Count
    buyer_review_requests_count_data = parse_buyer_review_requests_count(xml_content)
    merge_buyer_review_requests_count(release_json, buyer_review_requests_count_data)

    # Parse and merge BT-636-LotResult Buyer Review Requests Irregularity Type
    buyer_review_requests_irregularity_type_data = parse_buyer_review_requests_irregularity_type(xml_content)
    merge_buyer_review_requests_irregularity_type(release_json, buyer_review_requests_irregularity_type_data)

    # Parse and merge BT-64-Lot Subcontracting Obligation Minimum
    subcontracting_obligation_minimum_data = parse_subcontracting_obligation_minimum(xml_content)
    merge_subcontracting_obligation_minimum(release_json, subcontracting_obligation_minimum_data)

    # Parse and merge BT-644-Lot Prize Value
    lot_prize_value_data = parse_lot_prize_value(xml_content)
    merge_lot_prize_value(release_json, lot_prize_value_data)

    # Parse and merge BT-65-Lot Subcontracting Obligation
    subcontracting_obligation_data = parse_subcontracting_obligation(xml_content)
    merge_subcontracting_obligation(release_json, subcontracting_obligation_data)

    # Parse and merge BT-651-Lot Subcontracting Tender Indication
    subcontracting_tender_indication_data = parse_subcontracting_tender_indication(xml_content)
    merge_subcontracting_tender_indication(release_json, subcontracting_tender_indication_data)

    # Parse and merge BT-660-LotResult Framework Re-estimated Value
    framework_reestimated_value_data = parse_framework_reestimated_value(xml_content)
    merge_framework_reestimated_value(release_json, framework_reestimated_value_data)

    # Parse and merge BT-67-Procedure Exclusion Grounds
    exclusion_grounds_data = parse_exclusion_grounds(xml_content)
    merge_exclusion_grounds(release_json, exclusion_grounds_data)

    # Parse and merge BT-70-Lot Terms Performance
    terms_performance_data = parse_terms_performance(xml_content)
    merge_terms_performance(release_json, terms_performance_data)

    # Parse and merge BT-702(a)-notice Notice Official Language
    notice_official_language = parse_notice_official_language(xml_content)
    merge_notice_official_language(release_json, notice_official_language)

    # Parse and merge BT-706-UBO Winner Owner Nationality
    winner_owner_nationality_data = parse_winner_owner_nationality(xml_content)
    merge_winner_owner_nationality(release_json, winner_owner_nationality_data)

    # Parse and merge BT-707 Documents Restricted Justification
    documents_restricted_justification_data = parse_documents_restricted_justification(xml_content)
    merge_documents_restricted_justification(release_json, documents_restricted_justification_data)

    # Parse and merge BT-708 Documents Official Language
    documents_official_language_data = parse_documents_official_language(xml_content)
    merge_documents_official_language(release_json, documents_official_language_data)

    # Parse and merge BT-709-LotResult Framework Maximum Value
    framework_maximum_value_data = parse_framework_maximum_value(xml_content)
    merge_framework_maximum_value(release_json, framework_maximum_value_data)

    # Parse and merge BT-71 Reserved Participation
    reserved_participation_data = parse_reserved_participation(xml_content)
    merge_reserved_participation(release_json, reserved_participation_data)

    # Parse and merge BT-710-LotResult Tender Value Lowest
    tender_value_lowest_data = parse_tender_value_lowest(xml_content)
    merge_tender_value_lowest(release_json, tender_value_lowest_data)

    # Parse and merge BT-711-LotResult Tender Value Highest
    tender_value_highest_data = parse_tender_value_highest(xml_content)
    merge_tender_value_highest(release_json, tender_value_highest_data)

    # Parse and merge BT-712-LotResult Buyer Review Complainants
    buyer_review_complainants_data = parse_buyer_review_complainants(xml_content)
    merge_buyer_review_complainants(release_json, buyer_review_complainants_data)

    # Parse and merge BT-717-Lot Clean Vehicles Directive
    clean_vehicles_directive_data = parse_clean_vehicles_directive(xml_content)
    merge_clean_vehicles_directive(release_json, clean_vehicles_directive_data)

    # Parse and merge BT-719-notice Change Procurement Documents Date
    change_procurement_documents_date_data = parse_change_procurement_documents_date(xml_content)
    merge_change_procurement_documents_date(release_json, change_procurement_documents_date_data)

    # Parse and merge BT-720-Tender Tender Value
    logger.info("Processing BT-720-Tender: Tender Value")
    tender_value_data = parse_tender_value(xml_content)
    if tender_value_data:
        merge_tender_value(release_json, tender_value_data)
    else:
        logger.warning("No Tender Value data found")

    # Parse and merge BT-721-Contract Title
    contract_title_data = parse_contract_title(xml_content)
    merge_contract_title(release_json, contract_title_data)

    # Parse and merge BT-722-Contract EU Funds Programme
    logger.info("Processing BT-722-Contract: EU Funds Programme")
    contract_eu_funds_data = parse_contract_eu_funds_programme(xml_content)
    if contract_eu_funds_data:
        merge_contract_eu_funds_programme(release_json, contract_eu_funds_data)
    else:
        logger.warning("No Contract EU Funds Programme data found")

    # Parse and merge BT-7220-Lot EU Funds Programme
    lot_eu_funds_programme_data = parse_lot_eu_funds_programme(xml_content)
    merge_lot_eu_funds_programme(release_json, lot_eu_funds_programme_data)

    # Parse and merge BT-723-LotResult Vehicle Category
    vehicle_category_data = parse_vehicle_category(xml_content)
    merge_vehicle_category(release_json, vehicle_category_data)

    # Parse and merge BT-726 Suitable For SMEs
    suitable_for_smes_data = parse_suitable_for_smes(xml_content)
    merge_suitable_for_smes(release_json, suitable_for_smes_data)

    # Parse and merge BT-727 Place Performance Services Other
    place_performance_services_other_data = parse_place_performance_services_other(xml_content)
    merge_place_performance_services_other(release_json, place_performance_services_other_data)

    # Parse and merge BT-728 Place Performance Additional Information
    place_performance_additional_info_data = parse_place_performance_additional_info(xml_content)
    merge_place_performance_additional_info(release_json, place_performance_additional_info_data)

    # Parse and merge BT-729-Lot Subcontracting Obligation Maximum
    subcontracting_obligation_maximum_data = parse_subcontracting_obligation_maximum(xml_content)
    merge_subcontracting_obligation_maximum(release_json, subcontracting_obligation_maximum_data)

    # Parse and merge BT-732-Lot Security Clearance Description
    security_clearance_description_data = parse_security_clearance_description(xml_content)
    merge_security_clearance_description(release_json, security_clearance_description_data)

    # Parse and merge BT-733 Award Criteria Order Justification
    award_criteria_order_justification_data = parse_award_criteria_order_justification(xml_content)
    merge_award_criteria_order_justification(release_json, award_criteria_order_justification_data)

    # Parse and merge BT-734 Award Criterion Name
    award_criterion_name_data = parse_award_criterion_name(xml_content)
    merge_award_criterion_name(release_json, award_criterion_name_data)

    # Parse and merge BT-735 CVD Contract Type
    logger.info("Processing BT-735: CVD Contract Type")
    cvd_contract_type_data = parse_cvd_contract_type(xml_content)
    if cvd_contract_type_data:
        merge_cvd_contract_type(release_json, cvd_contract_type_data)
    else:
        logger.warning("No CVD Contract Type data found")

    # Parse and merge BT-736 Reserved Execution
    reserved_execution_data = parse_reserved_execution(xml_content)
    merge_reserved_execution(release_json, reserved_execution_data)

    # Parse and merge BT-737 Documents Unofficial Language
    documents_unofficial_language_data = parse_documents_unofficial_language(xml_content)
    merge_documents_unofficial_language(release_json, documents_unofficial_language_data)

    # Parse and merge BT-738 Notice Preferred Publication Date
    preferred_publication_date = parse_notice_preferred_publication_date(xml_content)
    merge_notice_preferred_publication_date(release_json, preferred_publication_date)

    # Parse and merge BT-739 Organization Contact Fax
    organization_contact_fax_data = parse_organization_contact_fax(xml_content)
    merge_organization_contact_fax(release_json, organization_contact_fax_data)

    # Parse and merge BT-740 Buyer Contracting Entity
    buyer_contracting_entity_data = parse_buyer_contracting_entity(xml_content)
    merge_buyer_contracting_entity(release_json, buyer_contracting_entity_data)

    # Parse and merge BT-743 Electronic Invoicing
    electronic_invoicing_data = parse_electronic_invoicing(xml_content)
    merge_electronic_invoicing(release_json, electronic_invoicing_data)

    # Parse and merge BT-744 Submission Electronic Signature
    submission_electronic_signature_data = parse_submission_electronic_signature(xml_content)
    merge_submission_electronic_signature(release_json, submission_electronic_signature_data)

    # Parse and merge BT-745 Submission Nonelectronic Description
    submission_nonelectronic_description_data = parse_submission_nonelectronic_description(xml_content)
    merge_submission_nonelectronic_description(release_json, submission_nonelectronic_description_data)

    # Parse and merge BT-746 Winner Listed
    winner_listed_data = parse_winner_listed(xml_content)
    merge_winner_listed(release_json, winner_listed_data)

    # Parse and merge BT-747 Selection Criteria Type
    selection_criteria_type_data = parse_selection_criteria_type(xml_content)
    merge_selection_criteria_type(release_json, selection_criteria_type_data)

    # Parse and merge BT-749 Selection Criteria Name
    selection_criteria_name_data = parse_selection_criteria_name(xml_content)
    merge_selection_criteria_name(release_json, selection_criteria_name_data)
    
    # Parse and merge BT-75-Lot Guarantee Required Description
    guarantee_required_description_data = parse_guarantee_required_description(xml_content)
    merge_guarantee_required_description(release_json, guarantee_required_description_data)

    # Parse and merge BT-750-Lot Selection Criteria Description
    selection_criteria_description_data = parse_selection_criteria_description(xml_content)
    merge_selection_criteria_description(release_json, selection_criteria_description_data)
    
    # Parse and merge BT-752-Lot Selection Criteria Second Stage Invite Threshold/Weight Number
    selection_criteria_numbers_data = parse_selection_criteria_numbers(xml_content)
    merge_selection_criteria_numbers(release_json, selection_criteria_numbers_data)

    # Parse and merge BT-7531-Lot Selection Criteria Second Stage Invite Number Weight
    selection_criteria_weight_data = parse_selection_criteria_weight(xml_content)
    merge_selection_criteria_weight(release_json, selection_criteria_weight_data)

    # Parse and merge BT-7532-Lot Selection Criteria Second Stage Invite Number Threshold
    selection_criteria_threshold_data = parse_selection_criteria_threshold(xml_content)
    merge_selection_criteria_threshold(release_json, selection_criteria_threshold_data)

    # Parse and merge BT-754-Lot Accessibility
    accessibility_data = parse_accessibility(xml_content)
    merge_accessibility(release_json, accessibility_data)

    # Parse and merge BT-755-Lot Accessibility Justification
    accessibility_justification_data = parse_accessibility_justification(xml_content)
    merge_accessibility_justification(release_json, accessibility_justification_data)

    # Parse and merge BT-756-Procedure PIN Competition Termination
    is_terminated = parse_pin_competition_termination(xml_content)
    merge_pin_competition_termination(release_json, is_terminated)

    # Parse and merge BT-759 Received Submissions Count
    logger.info("Processing BT-759: Received Submissions Count")
    statistics_data = parse_received_submissions_count(xml_content)
    if statistics_data:
        merge_received_submissions_count(release_json, statistics_data)
    else:
        logger.warning("No Received Submissions Count found")

    # Parse and merge BT-76-Lot Tenderer Legal Form Description
    legal_form_data = parse_tenderer_legal_form(xml_content)
    merge_tenderer_legal_form(release_json, legal_form_data)

    # Parse and merge BT-760-LotResult Received Submissions Type
    submissions_type_data = parse_received_submissions_type(xml_content)
    merge_received_submissions_type(release_json, submissions_type_data)

    # Parse and merge BT-762-notice Change Reason Description
    change_reasons = parse_change_reason_description(xml_content)
    merge_change_reason_description(release_json, change_reasons)

    # Parse and merge BT-763-Procedure Lots All Required
    is_all_required = parse_lots_all_required(xml_content)
    merge_lots_all_required(release_json, is_all_required)

    # Parse and merge BT-764-Lot Submission Electronic Catalogue
    ecatalog_data = parse_submission_electronic_catalogue(xml_content)
    merge_submission_electronic_catalogue(release_json, ecatalog_data)

    # Parse and merge BT-765 Framework Agreement
    fa_data = parse_framework_agreement(xml_content)
    merge_framework_agreement(release_json, fa_data)

    # Parse and merge BT-766 Dynamic Purchasing System
    dps_data = parse_dynamic_purchasing_system(xml_content)
    merge_dynamic_purchasing_system(release_json, dps_data)

    # Parse and merge BT-767-Lot Electronic Auction
    auction_data = parse_electronic_auction(xml_content)
    merge_electronic_auction(release_json, auction_data)

    # Parse and merge BT-769-Lot Multiple Tenders
    multiple_tenders_data = parse_multiple_tenders(xml_content)
    merge_multiple_tenders(release_json, multiple_tenders_data)

    # Parse and merge BT-77-Lot Terms Financial
    financial_terms_data = parse_terms_financial(xml_content)
    merge_terms_financial(release_json, financial_terms_data)

    # Parse and merge BT-771-Lot Late Tenderer Information
    late_info_data = parse_late_tenderer_information(xml_content)
    merge_late_tenderer_information(release_json, late_info_data)

    # Parse and merge BT-772-Lot Late Tenderer Information Description
    late_info_description_data = parse_late_tenderer_info_description(xml_content)
    merge_late_tenderer_info_description(release_json, late_info_description_data)

    # Parse and merge BT-773-Tender Subcontracting
    subcontracting_data = parse_subcontracting(xml_content)
    merge_subcontracting(release_json, subcontracting_data)
    
    # Parse and merge BT-774-Lot Green Procurement
    green_procurement_data = parse_green_procurement(xml_content)
    merge_green_procurement(release_json, green_procurement_data)

    # Parse and merge BT-775-Lot Social Procurement
    social_procurement_data = parse_social_procurement(xml_content)
    merge_social_procurement(release_json, social_procurement_data)

    # Parse and merge BT-776-Lot Procurement of Innovation
    procurement_innovation_data = parse_procurement_innovation(xml_content)
    merge_procurement_innovation(release_json, procurement_innovation_data)

    # Parse and merge BT-777-Lot Strategic Procurement Description
    strategic_procurement_data = parse_strategic_procurement_description(xml_content)
    merge_strategic_procurement_description(release_json, strategic_procurement_data)

    # Parse and merge BT-78-Lot Security Clearance Deadline
    security_clearance_data = parse_security_clearance_deadline(xml_content)
    merge_security_clearance_deadline(release_json, security_clearance_data)

    # Parse and merge BT-79-Lot Performing Staff Qualification
    staff_qualification_data = parse_performing_staff_qualification(xml_content)
    merge_performing_staff_qualification(release_json, staff_qualification_data)
    
    # Parse and merge BT-801-Lot Non Disclosure Agreement
    logger.info("Processing BT-801-Lot: Non Disclosure Agreement")
    nda_data = parse_non_disclosure_agreement(xml_content)
    if nda_data:
        merge_non_disclosure_agreement(release_json, nda_data)
    else:
        logger.warning("No Non Disclosure Agreement data found")

    # Parse and merge BT-802-Lot Non Disclosure Agreement Description
    logger.info("Processing BT-802-Lot: Non Disclosure Agreement Description")
    nda_description_data = parse_non_disclosure_agreement_description(xml_content)
    merge_non_disclosure_agreement_description(release_json, nda_description_data)

    # Parse and merge BT-805-Lot Green Procurement Criteria
    logger.info("Processing BT-805-Lot: Green Procurement Criteria")
    gpp_data = parse_green_procurement_criteria(xml_content)
    merge_green_procurement_criteria(release_json, gpp_data)

    # Parse and merge BT-88-Procedure Procedure Features
    logger.info("Processing BT-88-Procedure: Procedure Features")
    procedure_features_data = parse_procedure_features(xml_content)
    merge_procedure_features(release_json, procedure_features_data)

    # Parse and merge BT-92-Lot Electronic Ordering
    logger.info("Processing BT-92-Lot: Electronic Ordering")
    electronic_ordering_data = parse_electronic_ordering(xml_content)
    merge_electronic_ordering(release_json, electronic_ordering_data)

    # Parse and merge BT-93-Lot Electronic Payment
    logger.info("Processing BT-93-Lot: Electronic Payment")
    electronic_payment_data = parse_electronic_payment(xml_content)
    merge_electronic_payment(release_json, electronic_payment_data)

    # Parse and merge BT-94-Lot Recurrence
    logger.info("Processing BT-94-Lot: Recurrence")
    recurrence_data = parse_recurrence(xml_content)
    merge_recurrence(release_json, recurrence_data)

    # Parse and merge BT-95-Lot Recurrence Description
    logger.info("Processing BT-95-Lot: Recurrence Description")
    recurrence_description_data = parse_recurrence_description(xml_content)
    merge_recurrence_description(release_json, recurrence_description_data)

    # Parse and merge BT-97-Lot Submission Language
    logger.info("Processing BT-97-Lot: Submission Language")
    submission_language_data = parse_submission_language(xml_content)
    merge_submission_language(release_json, submission_language_data)

    # Parse and merge BT-98-Lot Tender Validity Deadline
    logger.info("Processing BT-98-Lot: Tender Validity Deadline")
    validity_deadline_data = parse_tender_validity_deadline(xml_content)
    merge_tender_validity_deadline(release_json, validity_deadline_data)

    # Parse and merge BT-99-Lot Review Deadline Description
    logger.info("Processing BT-99-Lot: Review Deadline Description")
    review_deadline_data = parse_review_deadline_description(xml_content)
    merge_review_deadline_description(release_json, review_deadline_data)

     # Parse and merge BT-198(BT-105) Unpublished Access Date
    logger.info("Processing BT-198(BT-105): Unpublished Access Date")
    access_date = parse_unpublished_access_date(xml_content)
    if access_date:
        merge_unpublished_access_date(release_json, access_date)
    else:
        logger.warning("No Unpublished Access Date found")

    # Parse and merge OPP-020-021-022-023-Contract Essential Assets
    logger.info("Processing OPP-020-021-022-023-Contract: Essential Assets")
    essential_assets_data = parse_essential_assets(xml_content)
    if essential_assets_data:
        merge_essential_assets(release_json, essential_assets_data)
    else:
        logger.warning("No Essential Assets data found")

    # Parse and merge OPP-031-Tender Contract Conditions
    logger.info("Processing OPP-031-Tender: Contract Conditions")
    contract_conditions_data = parse_contract_conditions(xml_content)
    if contract_conditions_data:
        merge_contract_conditions(release_json, contract_conditions_data)
    else:
        logger.warning("No Contract Conditions data found")

    # Parse and merge OPP-032-Tender Revenues Allocation
    logger.info("Processing OPP-032-Tender: Revenues Allocation")
    revenues_allocation_data = parse_revenues_allocation(xml_content)
    if revenues_allocation_data:
        merge_revenues_allocation(release_json, revenues_allocation_data)
    else:
        logger.warning("No Revenues Allocation data found")

    # Parse and merge OPP-034-Tender Penalties and Rewards
    logger.info("Processing OPP-034-Tender: Penalties and Rewards")
    penalties_and_rewards_data = parse_penalties_and_rewards(xml_content)
    if penalties_and_rewards_data:
        merge_penalties_and_rewards(release_json, penalties_and_rewards_data)
    else:
        logger.warning("No Penalties and Rewards data found")

    # Parse and merge OPP-040-Procedure Main Nature - Sub Type
    logger.info("Processing OPP-040-Procedure: Main Nature - Sub Type")
    main_nature_sub_type_data = parse_main_nature_sub_type(xml_content)
    if main_nature_sub_type_data:
        merge_main_nature_sub_type(release_json, main_nature_sub_type_data)
    else:
        logger.warning("No Main Nature - Sub Type data found")

    # Parse and merge OPP-050-Organization Buyers Group Lead Indicator
    logger.info("Processing OPP-050-Organization: Buyers Group Lead Indicator")
    buyers_group_lead_data = parse_buyers_group_lead_indicator(xml_content)
    if buyers_group_lead_data:
        merge_buyers_group_lead_indicator(release_json, buyers_group_lead_data)
    else:
        logger.warning("No Buyers Group Lead Indicator data found")

    # Parse and merge OPP-051-Organization Awarding CPB Buyer Indicator
    logger.info("Processing OPP-051-Organization: Awarding CPB Buyer Indicator")
    awarding_cpb_buyer_data = parse_awarding_cpb_buyer_indicator(xml_content)
    if awarding_cpb_buyer_data:
        merge_awarding_cpb_buyer_indicator(release_json, awarding_cpb_buyer_data)
    else:
        logger.warning("No Awarding CPB Buyer Indicator data found")

    # Parse and merge OPP-052-Organization Acquiring CPB Buyer Indicator
    logger.info("Processing OPP-052-Organization: Acquiring CPB Buyer Indicator")
    acquiring_cpb_buyer_data = parse_acquiring_cpb_buyer_indicator(xml_content)
    if acquiring_cpb_buyer_data:
        merge_acquiring_cpb_buyer_indicator(release_json, acquiring_cpb_buyer_data)
    else:
        logger.warning("No Acquiring CPB Buyer Indicator data found")

    # Parse and merge OPP-080-Tender Kilometers Public Transport
    logger.info("Processing OPP-080-Tender: Kilometers Public Transport")
    kilometers_data = parse_kilometers_public_transport(xml_content)
    if kilometers_data:
        merge_kilometers_public_transport(release_json, kilometers_data)
    else:
        logger.warning("No Kilometers Public Transport data found")

    # Processing OPP-090-Procedure: Previous Notice Identifier
    logger.info("Processing OPP-090-Procedure: Previous Notice Identifier")
    logger.info(f"relatedProcesses before OPP-090: {json.dumps(release_json.get('relatedProcesses', []), indent=2)}")
    previous_notice_data = parse_previous_notice_identifier(xml_content)
    if previous_notice_data:
        logger.info(f"Parsed previous notice data: {json.dumps(previous_notice_data, indent=2)}")
        merge_previous_notice_identifier(release_json, previous_notice_data)
    else:
        logger.warning("No Previous Notice Identifier data found")
    logger.info(f"relatedProcesses after OPP-090: {json.dumps(release_json.get('relatedProcesses', []), indent=2)}")

    # Parse and merge OPT-030-Procedure-SProvider Provided Service Type
    logger.info("Processing OPT-030-Procedure-SProvider: Provided Service Type")
    service_type_data = parse_provided_service_type(xml_content)
    if service_type_data:
        merge_provided_service_type(release_json, service_type_data)
    else:
        logger.warning("No Provided Service Type data found")

    # Parse and merge Quality Target Code (OPP-071-Lot)
    logger.info("Processing OPP-071-Lot: Quality Target Code")
    quality_target_data = parse_quality_target_code(xml_content)
    if quality_target_data:
        merge_quality_target_code(release_json, quality_target_data)
    else:
        logger.warning("No Quality Target Code data found")

    # Parse and merge Quality Target Description (OPP-072-Lot)
    logger.info("Processing OPP-072-Lot: Quality Target Description")
    quality_target_description_data = parse_quality_target_description(xml_content)
    if quality_target_description_data:
        merge_quality_target_description(release_json, quality_target_description_data)
    else:
        logger.warning("No Quality Target Description data found")

    # Parse and merge Framework Notice Identifier (OPP-100-Contract)
    logger.info("Processing OPP-100-Contract: Framework Notice Identifier")
    framework_notice_data = parse_framework_notice_identifier(xml_content)
    if framework_notice_data:
        merge_framework_notice_identifier(release_json, framework_notice_data)
    else:
        logger.warning("No Framework Notice Identifier data found")

    # Parse and merge Fiscal Legislation data (OPP-110 and OPP-111)
    logger.info("Processing OPP-110 and OPP-111: Fiscal Legislation")
    fiscal_legislation_data = parse_fiscal_legislation(xml_content)
    if fiscal_legislation_data:
        merge_fiscal_legislation(release_json, fiscal_legislation_data)
    else:
        logger.warning("No Fiscal Legislation data found")

    # Parse and merge Environmental Legislation data (OPP-112 and OPP-120)
    logger.info("Processing OPP-112 and OPP-120: Environmental Legislation")
    environmental_legislation_data = parse_environmental_legislation(xml_content)
    if environmental_legislation_data:
        merge_environmental_legislation(release_json, environmental_legislation_data)
    else:
        logger.warning("No Environmental Legislation data found")

    # Parse and merge Employment Legislation data (OPP-113 and OPP-130)
    logger.info("Processing OPP-113 and OPP-130: Employment Legislation")
    employment_legislation_data = parse_employment_legislation(xml_content)
    if employment_legislation_data:
        merge_employment_legislation(release_json, employment_legislation_data)
    else:
        logger.warning("No Employment Legislation data found")

    # Parse and merge Procurement Documents data (OPP-140)
    logger.info("Processing OPP-140: Procurement Documents")
    procurement_docs_data = parse_procurement_documents(xml_content)
    if procurement_docs_data:
        merge_procurement_documents(release_json, procurement_docs_data)
    else:
        logger.warning("No Procurement Documents data found")

    # Parse and merge OPT-155-LotResult Vehicle Type and OPT-156-LotResult Vehicle Numeric
    logger.info("Processing OPT-155-LotResult and OPT-156-LotResult: Vehicle Type and Numeric")
    vehicle_data = parse_vehicle_type_and_numeric(xml_content)
    if vehicle_data:
        merge_vehicle_type_and_numeric(release_json, vehicle_data)
    else:
        logger.warning("No Vehicle Type and Numeric data found")

    # Parse and merge OPT-160-UBO First Name
    logger.info("Processing OPT-160-UBO: First Name")
    ubo_first_name_data = parse_ubo_first_name(xml_content)
    if ubo_first_name_data:
        merge_ubo_first_name(release_json, ubo_first_name_data)
    else:
        logger.warning("No UBO First Name data found")

    # Parse and merge OPT-170-Tenderer Tendering Party Leader
    logger.info("Processing OPT-170-Tenderer: Tendering Party Leader")
    tenderer_leader_data = parse_tendering_party_leader(xml_content)
    if tenderer_leader_data:
        merge_tendering_party_leader(release_json, tenderer_leader_data)
    else:
        logger.warning("No Tendering Party Leader data found")

    # Parse and merge OPT-200-Organization-Company Organization Technical Identifier
    logger.info("Processing OPT-200-Organization-Company: Organization Technical Identifier")
    org_technical_id_data = parse_organization_technical_identifier(xml_content)
    if org_technical_id_data:
        merge_organization_technical_identifier(release_json, org_technical_id_data)
    else:
        logger.warning("No Organization Technical Identifier data found")

    # Parse and merge OPT-201-Organization-TouchPoint TouchPoint Technical Identifier
    logger.info("Processing OPT-201-Organization-TouchPoint: TouchPoint Technical Identifier")
    touchpoint_technical_id_data = parse_touchpoint_technical_identifier(xml_content)
    if touchpoint_technical_id_data:
        merge_touchpoint_technical_identifier(release_json, touchpoint_technical_id_data)
    else:
        logger.warning("No TouchPoint Technical Identifier data found")

    #logger.info("Initial release_json state:")
    #logger.info(json.dumps(release_json, indent=2))
    
    logger.info("Processing OPT-202-UBO: Beneficial Owner Technical Identifier")
    beneficial_owner_id_data = parse_beneficial_owner_identifier(xml_content)
    if beneficial_owner_id_data:
      #  logger.info(f"Beneficial owner data found: {beneficial_owner_id_data}")
        merge_beneficial_owner_identifier(release_json, beneficial_owner_id_data)
     #   logger.info("After merging beneficial owner data:")
     #   logger.info(json.dumps(release_json, indent=2))
    else:
        logger.warning("No Beneficial Owner Technical Identifier data found")

    # Parse and merge OPT-300 Contract Signatory, Procedure Buyer, and Service Provider
    logger.info("Processing OPT-300: Contract Signatory, Procedure Buyer, and Service Provider")
    parsed_opt_300_data = parse_opt_300(xml_content)
    if parsed_opt_300_data:
        merge_opt_300(release_json, parsed_opt_300_data)
        logger.info("Merged OPT-300 data into release JSON")
    else:
        logger.warning("No OPT-300 data found for Contract Signatory, Procedure Buyer, or Service Provider")

    # Parse and merge OPT-301-Lot-AddInfo Additional Info Provider Technical Identifier Reference
    logger.info("Processing OPT-301-Lot-AddInfo: Additional Info Provider Technical Identifier Reference")
    additional_info_provider_data = parse_additional_info_provider_identifier(xml_content)
    if additional_info_provider_data:
        merge_additional_info_provider_identifier(release_json, additional_info_provider_data)
    else:
        logger.warning("No Additional Info Provider Technical Identifier Reference data found")

    # Parse and merge OPT-301-Lot-DocProvider Document Provider Technical Identifier Reference
    logger.info("Processing OPT-301-Lot-DocProvider: Document Provider Technical Identifier Reference")
    document_provider_data = parse_document_provider_identifier(xml_content)
    if document_provider_data:
        merge_document_provider_identifier(release_json, document_provider_data)
    else:
        logger.warning("No Document Provider Technical Identifier Reference data found")

    # Parse and merge OPT-301-Lot-EmployLegis Employment Legislation Organization Technical Identifier Reference
    logger.info("Processing OPT-301-Lot-EmployLegis: Employment Legislation Organization Technical Identifier Reference")
    employment_legislation_data = parse_employment_legislation_document_reference(xml_content)
    if employment_legislation_data:
        merge_employment_legislation_document_reference(release_json, employment_legislation_data)
    else:
        logger.warning("No Employment Legislation Organization Technical Identifier Reference data found")

    # Parse and merge OPT-301-Lot-EnvironLegis Environmental Legislation Organization Technical Identifier Reference
    logger.info("Processing OPT-301-Lot-EnvironLegis: Environmental Legislation Organization Technical Identifier Reference")
    environmental_legislation_data = parse_environmental_legislation_document_reference(xml_content)
    if environmental_legislation_data:
        merge_environmental_legislation_document_reference(release_json, environmental_legislation_data)
    else:
        logger.warning("No Environmental Legislation Organization Technical Identifier Reference data found")

    # Parse and merge OPT-301-Lot-ReviewOrg Review Organization Technical Identifier Reference
    logger.info("Processing OPT-301-Lot-ReviewOrg: Review Organization Technical Identifier Reference")
    review_org_data = parse_review_org_identifier(xml_content)
    if review_org_data:
        merge_review_org_identifier(release_json, review_org_data)
    else:
        logger.warning("No Review Organization Technical Identifier Reference data found")

    # Parse and merge OPT-301-Lot-Mediator Mediator Technical Identifier Reference
    logger.info("Processing OPT-301-Lot-Mediator: Mediator Technical Identifier Reference")
    mediator_data = parse_mediator_identifier(xml_content)
    if mediator_data:
        merge_mediator_identifier(release_json, mediator_data)
    else:
        logger.warning("No Mediator Technical Identifier Reference data found")

    # Parse and merge OPT-301-Lot-ReviewInfo Review Info Provider Technical Identifier Reference
    logger.info("Processing OPT-301-Lot-ReviewInfo: Review Info Provider Technical Identifier Reference")
    review_info_data = parse_review_info_identifier(xml_content)
    if review_info_data:
        merge_review_info_identifier(release_json, review_info_data)
    else:
        logger.warning("No Review Info Provider Technical Identifier Reference data found")

    # Parse and merge OPT-301-Lot-TenderReceipt Tender Recipient Technical Identifier Reference
    logger.info("Processing OPT-301-Lot-TenderReceipt: Tender Recipient Technical Identifier Reference")
    recipient_data = parse_tender_recipient_identifier(xml_content)
    if recipient_data:
        merge_tender_recipient_identifier(release_json, recipient_data)
    else:
        logger.warning("No Tender Recipient Technical Identifier Reference data found")

# add more OPT-301 her





    # Parse and merge OPT-302-Organization Beneficial Owner Reference
    logger.info("Processing OPT-302-Organization: Beneficial Owner Reference")
    bo_reference_data = parse_beneficial_owner_reference(xml_content)
    if bo_reference_data:
        merge_beneficial_owner_reference(release_json, bo_reference_data)
    else:
        logger.warning("No Beneficial Owner Reference data found")

    # Parse and merge OPT-310-Tender Tendering Party ID Reference
    logger.info("Processing OPT-310-Tender: Tendering Party ID Reference")
    tendering_party_data = parse_tendering_party_id_reference(xml_content)
    if tendering_party_data:
        merge_tendering_party_id_reference(release_json, tendering_party_data)
    else:
        logger.warning("No Tendering Party ID Reference data found")

    # Parse and merge OPT-315-LotResult Contract Identifier Reference
    logger.info("Processing OPT-315-LotResult: Contract Identifier Reference")
    contract_id_data = parse_contract_identifier_reference(xml_content)
    if contract_id_data:
        merge_contract_identifier_reference(release_json, contract_id_data)
    else:
        logger.warning("No Contract Identifier Reference data found")

    # Parse and merge OPT-316-Contract Contract Technical Identifier
    logger.info("Processing OPT-316-Contract: Contract Technical Identifier")
    contract_tech_id_data = parse_contract_technical_identifier(xml_content)
    if contract_tech_id_data:
        merge_contract_technical_identifier(release_json, contract_tech_id_data)
    else:
        logger.warning("No Contract Technical Identifier data found")

    # Parse and merge OPT-320-LotResult Tender Identifier Reference
    logger.info("Processing OPT-320-LotResult: Tender Identifier Reference")
    tender_id_data = parse_tender_identifier_reference(xml_content)
    if tender_id_data:
        merge_tender_identifier_reference(release_json, tender_id_data)
    else:
        logger.warning("No Tender Identifier Reference data found")
        
        
    # Remove empty elements from release_json
    release_json = remove_empty_elements(release_json)

    #logger.info(f"Final release_json: {json.dumps(release_json, indent=2)}")
    
    # Write the JSON output to a file
    with io.open('output.json', 'w', encoding='utf-8') as f:
        json.dump(release_json, f, ensure_ascii=False, indent=4)

    # Print the JSON string
    json_string = json.dumps(release_json, ensure_ascii=False, indent=2)
    logger.info("XML to JSON conversion completed")
    print(json_string)

if __name__ == "__main__":
    # Path to the XML file
    xml_path = 'can_24_minimal.xml'
    # Prefix for OCID
    ocid_prefix = 'ocid_prefix_value'
    
    main(xml_path, ocid_prefix)