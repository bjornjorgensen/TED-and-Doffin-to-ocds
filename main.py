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
from converters.BT_09_Procedure import parse_cross_border_law, merge_cross_border_law
from converters.BT_10 import parse_contract_xml
from converters.BT_11_Procedure_Buyer import parse_buyer_legal_type, merge_buyer_legal_type
from converters.BT_88_Procedure import parse_procedure_features, merge_procedure_features
from converters.BT_105_Procedure import parse_procedure_type, merge_procedure_type
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
from converters.BT_136_Procedure import parse_direct_award_justification, merge_direct_award_justification
from converters.BT_137_Purpose_Lot_Identifier import parse_purpose_lot_identifier, merge_purpose_lot_identifier
from converters.BT_14_Lot import parse_lot_documents_restricted, merge_lot_documents_restricted
from converters.BT_14_Part import parse_part_documents_restricted, merge_part_documents_restricted
from converters.BT_140_notice import parse_change_reason_code, merge_change_reason_code
from converters.BT_142_LotResult import parse_winner_chosen, merge_winner_chosen
from converters.BT_144_LotResult import parse_not_awarded_reason, merge_not_awarded_reason
from converters.BT_145_Contract import parse_contract_conclusion_date, merge_contract_conclusion_date
from converters.BT_1451_Contract import parse_winner_decision_date, merge_winner_decision_date
from converters.BT_15_Lot_Part import parse_documents_url, merge_documents_url
from converters.BT_150 import parse_contract_identifier
from converters.BT_151_Contract import parse_contract_url, merge_contract_url
from converters.BT_16 import parse_organisation_part_name
from converters.BT_160 import parse_concession_revenue_buyer
from converters.BT_162 import parse_concession_revenue_user
from converters.BT_163_Tender import parse_concession_value_description, merge_concession_value_description
from converters.BT_165_Organization_Company import parse_winner_size, merge_winner_size
from converters.BT_17_Lot import parse_submission_electronic, merge_submission_electronic
from converters.BT_171_Tender import parse_tender_rank, merge_tender_rank
from converters.BT_1711_Tender import parse_tender_ranked, merge_tender_ranked
from converters.BT_18_Lot import parse_submission_url, merge_submission_url
from converters.BT_19_Lot import parse_nonelectronic_submission_justification, merge_nonelectronic_submission_justification
from converters.BT_191 import parse_country_origin
from converters.BT_193_Tender import parse_tender_variant, merge_tender_variant
from converters.BT_195 import parse_unpublished_identifier
from converters.BT_21_Lot import parse_lot_title, merge_lot_title
from converters.BT_21_LotsGroup import parse_lots_group_title, merge_lots_group_title
from converters.BT_21_Part import parse_part_title, merge_part_title
from converters.BT_21_Procedure import parse_procedure_title, merge_procedure_title
from converters.BT_22_Lot import parse_lot_internal_identifier, merge_lot_internal_identifier
from converters.BT_23 import parse_main_nature, merge_main_nature
from converters.BT_24 import parse_description, merge_description
from converters.BT_25 import parse_quantity, merge_quantity
from converters.BT_26a_lot import parse_classification_type, merge_classification_type
from converters.BT_26a_part import parse_classification_type_part, merge_classification_type_part
from converters.BT_26a_procedure import parse_classification_type_procedure, merge_classification_type_procedure
from converters.BT_26m_lot import parse_main_classification_type_lot, merge_main_classification_type_lot
from converters.BT_26m_part import parse_main_classification_type_part, merge_main_classification_type_part
from converters.BT_26m_procedure import parse_main_classification_type_procedure, merge_main_classification_type_procedure
from converters.BT_262_lot import parse_main_classification_code_lot, merge_main_classification_code_lot
from converters.BT_262_part import parse_main_classification_code_part, merge_main_classification_code_part
from converters.BT_262_procedure import parse_main_classification_code_procedure, merge_main_classification_code_procedure
from converters.BT_263_lot import parse_additional_classification_code_lot, merge_additional_classification_code_lot
from converters.BT_263_part import parse_additional_classification_code_part, merge_additional_classification_code_part
from converters.BT_263_procedure import parse_additional_classification_code_procedure, merge_additional_classification_code_procedure
from converters.BT_27_Lot import parse_bt_27_lot, merge_bt_27_lot
from converters.BT_27_LotsGroup import parse_bt_27_lots_group, merge_bt_27_lots_group
from converters.BT_27_Part import parse_bt_27_part, merge_bt_27_part
from converters.BT_27_Procedure import parse_bt_27_procedure, merge_bt_27_procedure
from converters.BT_271_Lot import parse_bt_271_lot, merge_bt_271_lot
from converters.BT_271_LotsGroup import parse_bt_271_lots_group, merge_bt_271_lots_group
from converters.BT_271_Procedure import parse_bt_271_procedure, merge_bt_271_procedure
from converters.BT_300 import parse_additional_information, merge_additional_information
from converters.BT_31 import parse_lots_max_allowed, merge_lots_max_allowed
from converters.BT_3201 import parse_tender_identifier, merge_tender_identifier
from converters.BT_3202 import parse_contract_tender_id, merge_contract_tender_id
from converters.BT_33 import parse_lots_max_awarded, merge_lots_max_awarded
from converters.BT_330 import parse_procedure_group_identifier, merge_procedure_group_identifier
from converters.BT_36_Lot import parse_lot_duration, merge_lot_duration
from converters.BT_36_Part import parse_part_duration, merge_part_duration
from converters.BT_40_Lot import parse_lot_selection_criteria_second_stage, merge_lot_selection_criteria_second_stage
from converters.BT_41_Lot import parse_lot_following_contract, merge_lot_following_contract
from converters.BT_42_Lot import parse_lot_jury_decision_binding, merge_lot_jury_decision_binding
from converters.BT_44 import parse_prize_rank, merge_prize_rank
from converters.BT_45 import parse_rewards_other, merge_rewards_other
from converters.BT_46 import parse_jury_member_name, merge_jury_member_name
from converters.BT_47 import parse_participant_name, merge_participant_name
from converters.BT_50 import parse_minimum_candidates, merge_minimum_candidates
from converters.BT_500_Organization_Company import parse_organization_name, merge_organization_name
from converters.BT_500_Organization_TouchPoint import parse_touchpoint_name, merge_touchpoint_name
from converters.BT_500_UBO import parse_ubo_name, merge_ubo_name
from converters.BT_501_Organization_Company import parse_organization_identifier, merge_organization_identifier
from converters.BT_5010_Lot import parse_eu_funds_financing_identifier, merge_eu_funds_financing_identifier
from converters.BT_5011_Contract import parse_contract_eu_funds_financing_identifier, merge_contract_eu_funds_financing_identifier
from converters.BT_502_Organization_Company import parse_organization_contact_point, merge_organization_contact_point
from converters.BT_502_Organization_TouchPoint import parse_touchpoint_contact_point, merge_touchpoint_contact_point
from converters.BT_503_Organization_Company import parse_organization_contact_telephone, merge_organization_contact_telephone
from converters.BT_503_Organization_TouchPoint import parse_touchpoint_contact_telephone, merge_touchpoint_contact_telephone
from converters.BT_503_UBO import parse_ubo_telephone, merge_ubo_telephone
from converters.BT_505_Organization_Company import parse_organization_website, merge_organization_website
from converters.BT_505_Organization_TouchPoint import parse_touchpoint_website, merge_touchpoint_website
from converters.BT_506_Organization_Company import parse_organization_contact_email, merge_organization_contact_email
from converters.BT_506_Organization_TouchPoint import parse_touchpoint_contact_email, merge_touchpoint_contact_email
from converters.BT_506_UBO import parse_ubo_email, merge_ubo_email
from converters.BT_507_Organization_Company import parse_organization_country_subdivision, merge_organization_country_subdivision
from converters.BT_507_Organization_TouchPoint import parse_touchpoint_country_subdivision, merge_touchpoint_country_subdivision
from converters.BT_507_UBO import parse_ubo_country_subdivision, merge_ubo_country_subdivision
from converters.BT_5071 import parse_place_performance_country_subdivision, merge_place_performance_country_subdivision
from converters.BT_508 import parse_buyer_profile_url, merge_buyer_profile_url
from converters.BT_509 import parse_edelivery_gateway, merge_edelivery_gateway
from converters.BT_51 import parse_maximum_candidates_number, merge_maximum_candidates_number
from converters.BT_510a_Organization_Company import parse_organization_street, merge_organization_street
from converters.BT_510a_Organization_TouchPoint import parse_touchpoint_street, merge_touchpoint_street
from converters.BT_510a_UBO import parse_ubo_street, merge_ubo_street
from converters.BT_510b_Organization_Company import parse_organization_streetline1, merge_organization_streetline1
from converters.BT_510b_Organization_TouchPoint import parse_touchpoint_streetline1, merge_touchpoint_streetline1
from converters.BT_510b_UBO import parse_ubo_streetline1, merge_ubo_streetline1
from converters.BT_510c_Organization_Company import parse_organization_streetline2, merge_organization_streetline2
from converters.BT_510c_Organization_TouchPoint import parse_touchpoint_streetline2, merge_touchpoint_streetline2
from converters.BT_510c_UBO import parse_ubo_streetline2, merge_ubo_streetline2

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
from converters.BT_60_Lot import parse_eu_funds, merge_eu_funds
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
from converters.BT_746_Organization import parse_organization_listed, merge_organization_listed
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
from converters.BT_92_Lot import parse_electronic_ordering, merge_electronic_ordering
from converters.BT_93_Lot import parse_electronic_payment, merge_electronic_payment
from converters.BT_94_Lot import parse_recurrence, merge_recurrence
from converters.BT_95_Lot import parse_recurrence_description, merge_recurrence_description
from converters.BT_97_Lot import parse_submission_language, merge_submission_language
from converters.BT_98_Lot import parse_tender_validity_deadline, merge_tender_validity_deadline
from converters.BT_99_Lot import parse_review_deadline_description, merge_review_deadline_description
from converters.BT_198_BT_105 import parse_unpublished_access_date, merge_unpublished_access_date
from converters.OPP_020_Contract import map_extended_duration_indicator, merge_extended_duration_indicator
from converters.OPP_021_Contract import map_essential_assets, merge_essential_assets
from converters.OPP_022_Contract import map_asset_significance, merge_asset_significance
from converters.OPP_023_Contract import map_asset_predominance, merge_asset_predominance
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
from converters.OPT_300_Contract_Signatory import parse_contract_signatory, merge_contract_signatory
from converters.OPT_300_Procedure_SProvider import parse_procedure_sprovider, merge_procedure_sprovider
from converters.OPT_301_Lot_AddInfo import parse_additional_info_provider_identifier, merge_additional_info_provider_identifier
from converters.OPT_301_Lot_DocProvider import parse_document_provider_identifier, merge_document_provider_identifier
from converters.OPT_301_Lot_EmployLegis import parse_employment_legislation_document_reference, merge_employment_legislation_document_reference
from converters.OPT_301_Lot_EnvironLegis import parse_environmental_legislation_document_reference, merge_environmental_legislation_document_reference
from converters.OPT_301_Lot_ReviewOrg import parse_review_org_identifier, merge_review_org_identifier
from converters.OPT_301_Lot_Mediator import parse_mediator_identifier, merge_mediator_identifier
from converters.OPT_301_Lot_ReviewInfo import parse_review_info_identifier, merge_review_info_identifier
from converters.OPT_301_Lot_TenderEval import parse_tender_evaluator_identifier, merge_tender_evaluator_identifier
from converters.OPT_301_Lot_TenderReceipt import parse_tender_recipient_identifier, merge_tender_recipient_identifier
from converters.OPT_301_LotResult_Financing import parse_lotresult_financing, merge_lotresult_financing
from converters.OPT_301_LotResult_Paying import parse_lotresult_paying, merge_lotresult_paying
from converters.OPT_301_Part_AddInfo import parse_part_addinfo, merge_part_addinfo
from converters.OPT_301_Part_DocProvider import parse_part_docprovider, merge_part_docprovider
from converters.OPT_301_Part_EmployLegis import parse_part_employlegis, merge_part_employlegis
from converters.OPT_301_Part_EnvironLegis import parse_part_environlegis, merge_part_environlegis
from converters.OPT_301_Part_FiscalLegis import parse_part_fiscallegis, merge_part_fiscallegis
from converters.OPT_301_Part_Mediator import parse_part_mediator, merge_part_mediator
from converters.OPT_301_Part_ReviewInfo import parse_part_reviewinfo, merge_part_reviewinfo
from converters.OPT_301_Part_ReviewOrg import parse_part_revieworg, merge_part_revieworg
from converters.OPT_301_Part_TenderEval import parse_part_tendereval, merge_part_tendereval
from converters.OPT_301_Part_TenderReceipt import parse_part_tenderreceipt, merge_part_tenderreceipt
from converters.OPT_301_Tenderer_MainCont import parse_tenderer_maincont, merge_tenderer_maincont

# add more OPT 301 her

from converters.OPT_302_Organization import parse_beneficial_owner_reference, merge_beneficial_owner_reference
from converters.OPT_310_Tender import parse_tendering_party_id_reference, merge_tendering_party_id_reference
from converters.OPT_315_LotResult import parse_contract_identifier_reference, merge_contract_identifier_reference
from converters.OPT_316_Contract import parse_contract_technical_identifier, merge_contract_technical_identifier
from converters.OPT_320_LotResult import parse_tender_identifier_reference, merge_tender_identifier_reference



def configure_logging():
    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # Create file handler and set level to info
    file_handler = logging.FileHandler('app.log', mode='w')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(file_handler)

def remove_empty_elements(data):
    """
    Recursively remove empty lists, empty dicts, or None elements from a dictionary or list.
    Preserves False boolean values and zero numeric values.
    """
    if isinstance(data, dict):
        return {
            key: remove_empty_elements(value)
            for key, value in data.items()
            if value is not None and (value or isinstance(value, (bool, int, float)))
        }
    elif isinstance(data, list):
        return [
            remove_empty_elements(item)
            for item in data
            if item is not None and (item or isinstance(item, (bool, int, float)))
        ]
    else:
        return data

# Additional step to remove keys with empty dictionaries
def remove_empty_dicts(data):
    if isinstance(data, dict):
        return {
            key: remove_empty_dicts(value)
            for key, value in data.items()
            if value or isinstance(value, (bool, int, float))
        }
    elif isinstance(data, list):
        return [remove_empty_dicts(item) for item in data if item or isinstance(item, (bool, int, float))]
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
    
    # Parse and merge BT-09-Procedure Cross Border Law
    logger.info("Processing BT-09-Procedure: Cross Border Law")
    cross_border_law_data = parse_cross_border_law(xml_content)
    if cross_border_law_data:
        merge_cross_border_law(release_json, cross_border_law_data)
    else:
        logger.warning("No Cross Border Law data found")
    
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

    # Parse and merge BT-88-Procedure Procedure Features
    logger.info("Processing BT-88-Procedure: Procedure Features")
    procedure_features_data = parse_procedure_features(xml_content)
    if procedure_features_data:
        merge_procedure_features(release_json, procedure_features_data)
    else:
        logger.warning("No Procedure Features data found")
    
    # Parse and merge BT-105-Procedure
    try:
        procedure_type_data = parse_procedure_type(xml_content)
        if procedure_type_data:
            merge_procedure_type(release_json, procedure_type_data)
        else:
            logger.info("No procedure type data found")
    except Exception as e:
        logger.error(f"Error processing procedure type data: {str(e)}")

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
    try:
        tender_lot_identifier_data = parse_tender_lot_identifier(xml_content)
        if tender_lot_identifier_data:
            merge_tender_lot_identifier(release_json, tender_lot_identifier_data)
        else:
            logger.info("No Tender Lot Identifier data found")
    except Exception as e:
        logger.error(f"Error processing Tender Lot Identifier data: {str(e)}")

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

    # Parse and merge BT-136-Procedure
    try:
        direct_award_justification_data = parse_direct_award_justification(xml_content)
        if direct_award_justification_data:
            merge_direct_award_justification(release_json, direct_award_justification_data)
        else:
            logger.info("No direct award justification data found")
    except Exception as e:
        logger.error(f"Error processing direct award justification data: {str(e)}")

    # Parse and merge BT-137 Purpose Lot Identifier
    logger.info("Processing BT-137: Purpose Lot Identifier")
    purpose_lot_data = parse_purpose_lot_identifier(xml_content)
    if purpose_lot_data:
        merge_purpose_lot_identifier(release_json, purpose_lot_data)
    else:
        logger.warning("No Purpose Lot Identifier data found")

    # Parse and merge BT-14-Lot
    try:
        lot_documents_restricted_data = parse_lot_documents_restricted(xml_content)
        if lot_documents_restricted_data:
            merge_lot_documents_restricted(release_json, lot_documents_restricted_data)
        else:
            logger.info("No lot documents restricted data found")
    except Exception as e:
        logger.error(f"Error processing lot documents restricted data: {str(e)}")

    # Parse and merge BT-14-Part
    try:
        part_documents_restricted_data = parse_part_documents_restricted(xml_content)
        if part_documents_restricted_data:
            merge_part_documents_restricted(release_json, part_documents_restricted_data)
        else:
            logger.info("No part documents restricted data found")
    except Exception as e:
        logger.error(f"Error processing part documents restricted data: {str(e)}")

    # Parse and merge BT-140-notice
    try:
        change_reason_code_data = parse_change_reason_code(xml_content)
        if change_reason_code_data:
            merge_change_reason_code(release_json, change_reason_code_data)
        else:
            logger.info("No change reason code data found")
    except Exception as e:
        logger.error(f"Error processing change reason code data: {str(e)}")
    
    # Parse and merge BT-142-LotResult
    try:
        winner_chosen_data = parse_winner_chosen(xml_content)
        if winner_chosen_data:
            merge_winner_chosen(release_json, winner_chosen_data)
        else:
            logger.info("No winner chosen data found")
    except Exception as e:
        logger.error(f"Error processing winner chosen data: {str(e)}")

    # Parse and merge BT-144-LotResult
    try:
        not_awarded_reason_data = parse_not_awarded_reason(xml_content)
        if not_awarded_reason_data:
            merge_not_awarded_reason(release_json, not_awarded_reason_data)
        else:
            logger.info("No not awarded reason data found")
    except Exception as e:
        logger.error(f"Error processing not awarded reason data: {str(e)}")

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

    # Parse and merge BT-15-Lot-Part
    try:
        documents_url_data = parse_documents_url(xml_content)
        if documents_url_data:
            merge_documents_url(release_json, documents_url_data)
        else:
            logger.info("No documents URL data found")
    except Exception as e:
        logger.error(f"Error processing documents URL data: {str(e)}")

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

    # Parse and merge BT-151-Contract
    try:
        contract_url_data = parse_contract_url(xml_content)
        if contract_url_data:
            merge_contract_url(release_json, contract_url_data)
        else:
            logger.info("No contract URL data found")
    except Exception as e:
        logger.error(f"Error processing contract URL data: {str(e)}")

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

    # Parse and merge BT-163-Tender
    try:
        concession_value_description_data = parse_concession_value_description(xml_content)
        if concession_value_description_data:
            merge_concession_value_description(release_json, concession_value_description_data)
        else:
            logger.info("No concession value description data found")
    except Exception as e:
        logger.error(f"Error processing concession value description data: {str(e)}")

    # Parse and merge BT-165-Organization-Company Winner Size
    logger.info("Processing BT-165-Organization-Company: Winner Size")
    winner_size_data = parse_winner_size(xml_content)
    if winner_size_data:
        merge_winner_size(release_json, winner_size_data)
    else:
        logger.warning("No Winner Size data found")

    # Parse and merge BT-17-Lot SubmissionElectronic
    logger.info("Processing BT-17-Lot: SubmissionElectronic")
    submission_electronic_data = parse_submission_electronic(xml_content)
    if submission_electronic_data:
        merge_submission_electronic(release_json, submission_electronic_data)
    else:
        logger.warning("No Submission Electronic data found")

    # Parse and merge BT-171-Tender Tender Rank
    logger.info("Processing BT-171-Tender: Tender Rank")
    tender_rank_data = parse_tender_rank(xml_content)
    if tender_rank_data:
        merge_tender_rank(release_json, tender_rank_data)
    else:
        logger.warning("No Tender Rank data found")

    # Parse and merge BT-1711-Tender Tender Ranked
    logger.info("Processing BT-1711-Tender: Tender Ranked")
    tender_ranked_data = parse_tender_ranked(xml_content)
    if tender_ranked_data:
        merge_tender_ranked(release_json, tender_ranked_data)
    else:
        logger.warning("No Tender Ranked data found")

    # Parse the Submission URL (BT-18)
    try:
        submission_url_data = parse_submission_url(xml_content)
        if submission_url_data:
            merge_submission_url(release_json, submission_url_data)
        else:
            logger.info("No Submission URL data found")
    except Exception as e:
        logger.error(f"Error processing Submission URL data: {str(e)}")

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
        tender_variant_data = parse_tender_variant(xml_content)
        if tender_variant_data:
            merge_tender_variant(release_json, tender_variant_data)
        else:
            logger.info("No Tender Variant data found")
    except Exception as e:
        logger.error(f"Error processing Tender Variant data: {str(e)}")


    # Parse the Unpublished Identifier (BT-195)
    try:
        unpublished_identifier = parse_unpublished_identifier(xml_content)
        
        # Merge Unpublished Identifier into the release JSON
        if unpublished_identifier and "withheldInformation" in unpublished_identifier:
            release_json.setdefault("withheldInformation", []).extend(unpublished_identifier["withheldInformation"])

    except Exception as e:
        print(f"Error parsing Unpublished Identifier: {str(e)}")

    # Parse and merge BT-21-Lot
    try:
        lot_title_data = parse_lot_title(xml_content)
        if lot_title_data:
            merge_lot_title(release_json, lot_title_data)
        else:
            logger.info("No Lot Title data found")
    except Exception as e:
        logger.error(f"Error processing Lot Title data: {str(e)}")

    # Parse and merge BT-21-LotsGroup
    try:
        lots_group_title_data = parse_lots_group_title(xml_content)
        if lots_group_title_data:
            merge_lots_group_title(release_json, lots_group_title_data)
        else:
            logger.info("No Lots Group Title data found")
    except Exception as e:
        logger.error(f"Error processing Lots Group Title data: {str(e)}")

    # Parse and merge BT-21-Part
    try:
        part_title_data = parse_part_title(xml_content)
        if part_title_data:
            merge_part_title(release_json, part_title_data)
        else:
            logger.info("No Part Title data found")
    except Exception as e:
        logger.error(f"Error processing Part Title data: {str(e)}")

    # Parse and merge BT-21-Procedure
    try:
        procedure_title_data = parse_procedure_title(xml_content)
        if procedure_title_data:
            merge_procedure_title(release_json, procedure_title_data)
        else:
            logger.info("No Procedure Title data found")
    except Exception as e:
        logger.error(f"Error processing Procedure Title data: {str(e)}")

    # Parse and merge BT-22-Lot
    try:
        lot_internal_identifier_data = parse_lot_internal_identifier(xml_content)
        if lot_internal_identifier_data:
            merge_lot_internal_identifier(release_json, lot_internal_identifier_data)
        else:
            logger.info("No Lot Internal Identifier data found")
    except Exception as e:
        logger.error(f"Error processing Lot Internal Identifier data: {str(e)}")

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

    # Parse the classifications (BT-26 lot)
    try:
        classification_type_data = parse_classification_type(xml_content)
        if classification_type_data["tender"]["items"]:
            merge_classification_type(release_json, classification_type_data)
            logger.info("Merged Classification Type data")
        else:
            logger.info("No Classification Type data found")
    except Exception as e:
        logger.error(f"Error processing Classification Type data: {str(e)}")

    # Parse and merge Classification Type for BT-26 Part
    try:
        classification_type_data = parse_classification_type_part(xml_content)
        if classification_type_data["tender"]["items"]:
            merge_classification_type_part(release_json, classification_type_data)
            logger.info("Merged Classification Type data for Part")
        else:
            logger.info("No Classification Type data found for Part")
    except Exception as e:
        logger.error(f"Error processing Classification Type data for Part: {str(e)}")

    # Parse and merge Classification Type for BT-26 Procedure
    try:
        classification_type_data = parse_classification_type_procedure(xml_content)
        if classification_type_data["tender"]["items"]:
            merge_classification_type_procedure(release_json, classification_type_data)
            logger.info("Merged Classification Type data for Procedure")
        else:
            logger.info("No Classification Type data found for Procedure")
    except Exception as e:
        logger.error(f"Error processing Classification Type data for Procedure: {str(e)}")

    # Parse and merge Main Classification Type for BT_26m_lot Lot
    try:
        main_classification_type_data = parse_main_classification_type_lot(xml_content)
        if main_classification_type_data["tender"]["items"]:
            merge_main_classification_type_lot(release_json, main_classification_type_data)
            logger.info("Merged Main Classification Type data for Lot")
        else:
            logger.info("No Main Classification Type data found for Lot")
    except Exception as e:
        logger.error(f"Error processing Main Classification Type data for Lot: {str(e)}")

    # Parse and merge Main Classification Type for BT_26m_part
    try:
        main_classification_type_data = parse_main_classification_type_part(xml_content)
        if main_classification_type_data["tender"]["items"]:
            merge_main_classification_type_part(release_json, main_classification_type_data)
            logger.info("Merged Main Classification Type data for Part")
        else:
            logger.info("No Main Classification Type data found for Part")
    except Exception as e:
        logger.error(f"Error processing Main Classification Type data for Part: {str(e)}")

    # Parse and merge Main Classification Type for BT_26m_procedure
    try:
        main_classification_type_data = parse_main_classification_type_procedure(xml_content)
        if main_classification_type_data["tender"]["items"]:
            merge_main_classification_type_procedure(release_json, main_classification_type_data)
            logger.info("Merged Main Classification Type data for Procedure")
        else:
            logger.info("No Main Classification Type data found for Procedure")
    except Exception as e:
        logger.error(f"Error processing Main Classification Type data for Procedure: {str(e)}")

    # Parse and merge Main Classification Code for Lot BT_262_lot
    try:
        main_classification_code_data = parse_main_classification_code_lot(xml_content)
        if main_classification_code_data["tender"]["items"]:
            merge_main_classification_code_lot(release_json, main_classification_code_data)
            logger.info("Merged Main Classification Code data for Lot")
        else:
            logger.info("No Main Classification Code data found for Lot")
    except Exception as e:
        logger.error(f"Error processing Main Classification Code data for Lot: {str(e)}")

    # Parse and merge Main Classification Code for Part BT_262_part
    try:
        main_classification_code_data = parse_main_classification_code_part(xml_content)
        if main_classification_code_data["tender"]["items"]:
            merge_main_classification_code_part(release_json, main_classification_code_data)
            logger.info("Merged Main Classification Code data for Part")
        else:
            logger.info("No Main Classification Code data found for Part")
    except Exception as e:
        logger.error(f"Error processing Main Classification Code data for Part: {str(e)}")

    # Parse and merge Main Classification Code for Procedure BT_262_procedure
    try:
        main_classification_code_data = parse_main_classification_code_procedure(xml_content)
        if main_classification_code_data["tender"]["items"]:
            merge_main_classification_code_procedure(release_json, main_classification_code_data)
            logger.info("Merged Main Classification Code data for Procedure")
        else:
            logger.info("No Main Classification Code data found for Procedure")
    except Exception as e:
        logger.error(f"Error processing Main Classification Code data for Procedure: {str(e)}")

    # Parse and merge Additional Classification Code for Lot BT_263_lot
    try:
        additional_classification_code_data = parse_additional_classification_code_lot(xml_content)
        if additional_classification_code_data["tender"]["items"]:
            merge_additional_classification_code_lot(release_json, additional_classification_code_data)
            logger.info("Merged Additional Classification Code data for Lot")
        else:
            logger.info("No Additional Classification Code data found for Lot")
    except Exception as e:
        logger.error(f"Error processing Additional Classification Code data for Lot: {str(e)}")

    # Parse and merge Additional Classification Code for Part BT_263_part
    try:
        additional_classification_code_part_data = parse_additional_classification_code_part(xml_content)
        if additional_classification_code_part_data["tender"]["items"]:
            merge_additional_classification_code_part(release_json, additional_classification_code_part_data)
            logger.info("Merged Additional Classification Code data for Part")
        else:
            logger.info("No Additional Classification Code data found for Part")
    except Exception as e:
        logger.error(f"Error processing Additional Classification Code data for Part: {str(e)}")

    # Parse and merge Additional Classification Code for Procedure BT_263_procedure
    try:
        additional_classification_code_procedure_data = parse_additional_classification_code_procedure(xml_content)
        if additional_classification_code_procedure_data["tender"]["items"]:
            merge_additional_classification_code_procedure(release_json, additional_classification_code_procedure_data)
            logger.info("Merged Additional Classification Code data for Procedure")
        else:
            logger.info("No Additional Classification Code data found for Procedure")
    except Exception as e:
        logger.error(f"Error processing Additional Classification Code data for Procedure: {str(e)}")

    # Parse and merge BT-27-Lot Estimated Value
    try:
        bt_27_lot_data = parse_bt_27_lot(xml_content)
        if bt_27_lot_data["tender"]["lots"]:
            merge_bt_27_lot(release_json, bt_27_lot_data)
            logger.info("Merged BT-27-Lot Estimated Value data")
        else:
            logger.info("No BT-27-Lot Estimated Value data found")
    except Exception as e:
        logger.error(f"Error processing BT-27-Lot Estimated Value data: {str(e)}")

    # Parse and merge BT-27-LotsGroup Estimated Value
    try:
        bt_27_lots_group_data = parse_bt_27_lots_group(xml_content)
        if bt_27_lots_group_data["tender"]["lotGroups"]:
            merge_bt_27_lots_group(release_json, bt_27_lots_group_data)
            logger.info("Merged BT-27-LotsGroup Estimated Value data")
        else:
            logger.info("No BT-27-LotsGroup Estimated Value data found")
    except Exception as e:
        logger.error(f"Error processing BT-27-LotsGroup Estimated Value data: {str(e)}")

    # Parse and merge BT-27-Part Estimated Value
    try:
        bt_27_part_data = parse_bt_27_part(xml_content)
        if bt_27_part_data["tender"].get("value"):
            merge_bt_27_part(release_json, bt_27_part_data)
            logger.info("Merged BT-27-Part Estimated Value data")
        else:
            logger.info("No BT-27-Part Estimated Value data found")
    except Exception as e:
        logger.error(f"Error processing BT-27-Part Estimated Value data: {str(e)}")

    # Parse and merge BT-27-Procedure Estimated Value
    try:
        bt_27_procedure_data = parse_bt_27_procedure(xml_content)
        if bt_27_procedure_data["tender"].get("value"):
            merge_bt_27_procedure(release_json, bt_27_procedure_data)
            logger.info("Merged BT-27-Procedure Estimated Value data")
        else:
            logger.info("No BT-27-Procedure Estimated Value data found")
    except Exception as e:
        logger.error(f"Error processing BT-27-Procedure Estimated Value data: {str(e)}")

    # Parse and merge BT-271-Lot Framework Maximum Value
    try:
        bt_271_lot_data = parse_bt_271_lot(xml_content)
        if bt_271_lot_data["tender"]["lots"]:
            merge_bt_271_lot(release_json, bt_271_lot_data)
            logger.info("Merged BT-271-Lot Framework Maximum Value data")
        else:
            logger.info("No BT-271-Lot Framework Maximum Value data found")
    except Exception as e:
        logger.error(f"Error processing BT-271-Lot Framework Maximum Value data: {str(e)}")

    # Parse and merge BT-271-LotsGroup Framework Maximum Value
    try:
        bt_271_lots_group_data = parse_bt_271_lots_group(xml_content)
        if bt_271_lots_group_data["tender"]["lotGroups"]:
            merge_bt_271_lots_group(release_json, bt_271_lots_group_data)
            logger.info("Merged BT-271-LotsGroup Framework Maximum Value data")
        else:
            logger.info("No BT-271-LotsGroup Framework Maximum Value data found")
    except Exception as e:
        logger.error(f"Error processing BT-271-LotsGroup Framework Maximum Value data: {str(e)}")

    # Parse and merge BT-271-Procedure Framework Maximum Value
    try:
        bt_271_procedure_data = parse_bt_271_procedure(xml_content)
        if bt_271_procedure_data["tender"].get("techniques"):
            merge_bt_271_procedure(release_json, bt_271_procedure_data)
            logger.info("Merged BT-271-Procedure Framework Maximum Value data")
        else:
            logger.info("No BT-271-Procedure Framework Maximum Value data found")
    except Exception as e:
        logger.error(f"Error processing BT-271-Procedure Framework Maximum Value data: {str(e)}")

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

    # Parse and merge BT-36-Lot
    try:
        lot_duration_data = parse_lot_duration(xml_content)
        if lot_duration_data:
            merge_lot_duration(release_json, lot_duration_data)
        else:
            logger.info("No lot duration data found")
    except Exception as e:
        logger.error(f"Error processing lot duration data: {str(e)}")

    # Parse and merge BT-36-Part
    try:
        part_duration_data = parse_part_duration(xml_content)
        if part_duration_data:
            merge_part_duration(release_json, part_duration_data)
        else:
            logger.info("No part duration data found")
    except Exception as e:
        logger.error(f"Error processing part duration data: {str(e)}")

    # Parse and merge BT-40-Lot
    try:
        lot_selection_criteria_data = parse_lot_selection_criteria_second_stage(xml_content)
        if lot_selection_criteria_data:
            merge_lot_selection_criteria_second_stage(release_json, lot_selection_criteria_data)
        else:
            logger.info("No lot selection criteria second stage data found")
    except Exception as e:
        logger.error(f"Error processing lot selection criteria second stage data: {str(e)}")

    # Parse and merge BT-41-Lot
    try:
        lot_following_contract_data = parse_lot_following_contract(xml_content)
        if lot_following_contract_data:
            merge_lot_following_contract(release_json, lot_following_contract_data)
        else:
            logger.info("No lot following contract data found")
    except Exception as e:
        logger.error(f"Error processing lot following contract data: {str(e)}")

    # Parse and merge BT-42-Lot
    try:
        lot_jury_decision_binding_data = parse_lot_jury_decision_binding(xml_content)
        if lot_jury_decision_binding_data:
            merge_lot_jury_decision_binding(release_json, lot_jury_decision_binding_data)
        else:
            logger.info("No lot jury decision binding data found")
    except Exception as e:
        logger.error(f"Error processing lot jury decision binding data: {str(e)}")

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

   # Parse the organization info BT-500 
    try:
        organization_name_data = parse_organization_name(xml_content)
        if organization_name_data:
            merge_organization_name(release_json, organization_name_data)
        else:
            logger.info("No Organization Name data found")
    except Exception as e:
        logger.error(f"Error processing Organization Name data: {str(e)}")

    # Parse the organization info BT_500_Organization_TouchPoint
    try:
        touchpoint_name_data = parse_touchpoint_name(xml_content)
        if touchpoint_name_data:
            merge_touchpoint_name(release_json, touchpoint_name_data)
        else:
            logger.info("No TouchPoint Name data found")
    except Exception as e:
        logger.error(f"Error processing TouchPoint Name data: {str(e)}")

    # Parse and merge BT_500 Ultimate Beneficial Owner (UBO) Name data
    try:
        ubo_name_data = parse_ubo_name(xml_content)
        if ubo_name_data:
            merge_ubo_name(release_json, ubo_name_data)
        else:
            logger.info("No UBO Name data found")
    except Exception as e:
        logger.error(f"Error processing UBO Name data: {str(e)}")

    # Parse and merge BT-501 Organization Identifier data
    try:
        organization_identifier_data = parse_organization_identifier(xml_content)
        if organization_identifier_data:
            merge_organization_identifier(release_json, organization_identifier_data)
        else:
            logger.info("No Organization Identifier data found")
    except Exception as e:
        logger.error(f"Error processing Organization Identifier data: {str(e)}")

    # Parse and merge BT-5010-Lot EU Funds Financing Identifier
    try:
        eu_funds_financing_identifier_data = parse_eu_funds_financing_identifier(xml_content)
        if eu_funds_financing_identifier_data:
            merge_eu_funds_financing_identifier(release_json, eu_funds_financing_identifier_data)
        else:
            logger.info("No EU Funds Financing Identifier data found")
    except Exception as e:
        logger.error(f"Error processing EU Funds Financing Identifier data: {str(e)}")

    # Parse and merge BT-5011-Contract EU Funds Financing Identifier
    try:
        contract_eu_funds_financing_identifier_data = parse_contract_eu_funds_financing_identifier(xml_content)
        if contract_eu_funds_financing_identifier_data:
            merge_contract_eu_funds_financing_identifier(release_json, contract_eu_funds_financing_identifier_data)
        else:
            logger.info("No Contract EU Funds Financing Identifier data found")
    except Exception as e:
        logger.error(f"Error processing Contract EU Funds Financing Identifier data: {str(e)}")

    # Parse and merge BT-502-Organization-Company
    try:
        organization_contact_point_data = parse_organization_contact_point(xml_content)
        if organization_contact_point_data:
            merge_organization_contact_point(release_json, organization_contact_point_data)
        else:
            logger.info("No Organization Contact Point data found")
    except Exception as e:
        logger.error(f"Error processing Organization Contact Point data: {str(e)}")
    
    # Parse and merge BT-502-Organization-TouchPoint
    try:
        touchpoint_contact_point_data = parse_touchpoint_contact_point(xml_content)
        if touchpoint_contact_point_data:
            merge_touchpoint_contact_point(release_json, touchpoint_contact_point_data)
        else:
            logger.info("No TouchPoint Contact Point data found")
    except Exception as e:
        logger.error(f"Error processing TouchPoint Contact Point data: {str(e)}")

    # Parse and merge BT-503-Organization-Company
    try:
        organization_contact_telephone_data = parse_organization_contact_telephone(xml_content)
        if organization_contact_telephone_data:
            merge_organization_contact_telephone(release_json, organization_contact_telephone_data)
        else:
            logger.info("No Organization Contact Telephone data found")
    except Exception as e:
        logger.error(f"Error processing Organization Contact Telephone data: {str(e)}")

    # Parse and merge BT-503-Organization-TouchPoint
    try:
        touchpoint_contact_telephone_data = parse_touchpoint_contact_telephone(xml_content)
        if touchpoint_contact_telephone_data:
            merge_touchpoint_contact_telephone(release_json, touchpoint_contact_telephone_data)
        else:
            logger.info("No TouchPoint Contact Telephone data found")
    except Exception as e:
        logger.error(f"Error processing TouchPoint Contact Telephone data: {str(e)}")

    # Parse and merge BT-503-UBO
    try:
        ubo_telephone_data = parse_ubo_telephone(xml_content)
        if ubo_telephone_data:
            merge_ubo_telephone(release_json, ubo_telephone_data)
        else:
            logger.info("No UBO Telephone data found")
    except Exception as e:
        logger.error(f"Error processing UBO Telephone data: {str(e)}")

    # Parse and merge BT-505-Organization-Company
    try:
        organization_website_data = parse_organization_website(xml_content)
        if organization_website_data:
            merge_organization_website(release_json, organization_website_data)
        else:
            logger.info("No Organization Website data found")
    except Exception as e:
        logger.error(f"Error processing Organization Website data: {str(e)}")

    # Parse and merge BT-505-Organization-TouchPoint
    try:
        touchpoint_website_data = parse_touchpoint_website(xml_content)
        if touchpoint_website_data:
            merge_touchpoint_website(release_json, touchpoint_website_data)
        else:
            logger.info("No TouchPoint Website data found")
    except Exception as e:
        logger.error(f"Error processing TouchPoint Website data: {str(e)}")

    # Parse and merge BT-506-Organization-Company
    try:
        organization_contact_email_data = parse_organization_contact_email(xml_content)
        if organization_contact_email_data:
            merge_organization_contact_email(release_json, organization_contact_email_data)
        else:
            logger.info("No Organization Contact Email data found")
    except Exception as e:
        logger.error(f"Error processing Organization Contact Email data: {str(e)}")

    # Parse and merge BT-506-Organization-TouchPoint
    try:
        touchpoint_contact_email_data = parse_touchpoint_contact_email(xml_content)
        if touchpoint_contact_email_data:
            merge_touchpoint_contact_email(release_json, touchpoint_contact_email_data)
        else:
            logger.info("No TouchPoint Contact Email data found")
    except Exception as e:
        logger.error(f"Error processing TouchPoint Contact Email data: {str(e)}")

    # Parse and merge BT-506-UBO
    try:
        ubo_email_data = parse_ubo_email(xml_content)
        if ubo_email_data:
            merge_ubo_email(release_json, ubo_email_data)
        else:
            logger.info("No UBO Email data found")
    except Exception as e:
        logger.error(f"Error processing UBO Email data: {str(e)}")
    
    # Parse and merge BT-507-Organization-Company
    try:
        organization_country_subdivision_data = parse_organization_country_subdivision(xml_content)
        if organization_country_subdivision_data:
            merge_organization_country_subdivision(release_json, organization_country_subdivision_data)
        else:
            logger.info("No organization country subdivision data found")
    except Exception as e:
        logger.error(f"Error processing organization country subdivision data: {str(e)}")

    # Parse and merge BT-507-Organization-TouchPoint
    try:
        touchpoint_country_subdivision_data = parse_touchpoint_country_subdivision(xml_content)
        if touchpoint_country_subdivision_data:
            merge_touchpoint_country_subdivision(release_json, touchpoint_country_subdivision_data)
        else:
            logger.info("No touchpoint country subdivision data found")
    except Exception as e:
        logger.error(f"Error processing touchpoint country subdivision data: {str(e)}")

    # Parse and merge BT-507-UBO
    try:
        ubo_country_subdivision_data = parse_ubo_country_subdivision(xml_content)
        if ubo_country_subdivision_data:
            merge_ubo_country_subdivision(release_json, ubo_country_subdivision_data)
        else:
            logger.info("No UBO country subdivision data found")
    except Exception as e:
        logger.error(f"Error processing UBO country subdivision data: {str(e)}")

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

    # Parse and merge BT-510(a)-Organization-Company
    try:
        organization_street_data = parse_organization_street(xml_content)
        if organization_street_data:
            merge_organization_street(release_json, organization_street_data)
        else:
            logger.info("No Organization Street data found")
    except Exception as e:
        logger.error(f"Error processing Organization Street data: {str(e)}")

    # Parse and merge BT-510(a)-Organization-TouchPoint
    try:
        touchpoint_street_data = parse_touchpoint_street(xml_content)
        if touchpoint_street_data:
            merge_touchpoint_street(release_json, touchpoint_street_data)
        else:
            logger.info("No TouchPoint Street data found")
    except Exception as e:
        logger.error(f"Error processing TouchPoint Street data: {str(e)}")

    # Parse and merge BT-510(a)-UBO
    try:
        ubo_street_data = parse_ubo_street(xml_content)
        if ubo_street_data:
            merge_ubo_street(release_json, ubo_street_data)
        else:
            logger.info("No UBO Street data found")
    except Exception as e:
        logger.error(f"Error processing UBO Street data: {str(e)}")

    # Parse and merge BT-510(b)-Organization-Company
    try:
        organization_streetline1_data = parse_organization_streetline1(xml_content)
        if organization_streetline1_data:
            merge_organization_streetline1(release_json, organization_streetline1_data)
        else:
            logger.info("No Organization Streetline 1 data found")
    except Exception as e:
        logger.error(f"Error processing Organization Streetline 1 data: {str(e)}")

    # Parse and merge BT-510(b)-Organization-TouchPoint
    try:
        touchpoint_streetline1_data = parse_touchpoint_streetline1(xml_content)
        if touchpoint_streetline1_data:
            merge_touchpoint_streetline1(release_json, touchpoint_streetline1_data)
        else:
            logger.info("No TouchPoint Streetline 1 data found")
    except Exception as e:
        logger.error(f"Error processing TouchPoint Streetline 1 data: {str(e)}")

    # Parse and merge BT-510(b)-UBO
    try:
        ubo_streetline1_data = parse_ubo_streetline1(xml_content)
        if ubo_streetline1_data:
            merge_ubo_streetline1(release_json, ubo_streetline1_data)
        else:
            logger.info("No UBO Streetline 1 data found")
    except Exception as e:
        logger.error(f"Error processing UBO Streetline 1 data: {str(e)}")

    # Parse and merge BT-510(c)-Organization-Company
    try:
        organization_streetline2_data = parse_organization_streetline2(xml_content)
        if organization_streetline2_data:
            merge_organization_streetline2(release_json, organization_streetline2_data)
        else:
            logger.info("No Organization Streetline 2 data found")
    except Exception as e:
        logger.error(f"Error processing Organization Streetline 2 data: {str(e)}")

    # Parse and merge BT-510(c)-Organization-TouchPoint
    try:
        touchpoint_streetline2_data = parse_touchpoint_streetline2(xml_content)
        if touchpoint_streetline2_data:
            merge_touchpoint_streetline2(release_json, touchpoint_streetline2_data)
        else:
            logger.info("No TouchPoint Streetline 2 data found")
    except Exception as e:
        logger.error(f"Error processing TouchPoint Streetline 2 data: {str(e)}")

    # Parse and merge BT-510(c)-UBO
    try:
        ubo_streetline2_data = parse_ubo_streetline2(xml_content)
        if ubo_streetline2_data:
            merge_ubo_streetline2(release_json, ubo_streetline2_data)
        else:
            logger.info("No UBO Streetline 2 data found")
    except Exception as e:
        logger.error(f"Error processing UBO Streetline 2 data: {str(e)}")
        
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

    # Parse and merge BT-60-Lot EU Funds
    try:
        eu_funds_data = parse_eu_funds(xml_content)
        if eu_funds_data:
            merge_eu_funds(release_json, eu_funds_data)
        else:
            logger.info("No EU Funds data found")
    except Exception as e:
        logger.error(f"Error processing EU Funds data: {str(e)}")

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

   # Parse and merge BT-746-Organization
    try:
        organization_listed_data = parse_organization_listed(xml_content)
        if organization_listed_data:
            logger.debug(f"Organization listed data before merge: {organization_listed_data}")
            merge_organization_listed(release_json, organization_listed_data)
            logger.debug(f"Release JSON after merge: {release_json}")
        else:
            logger.info("No Organization Listed data found")
    except Exception as e:
        logger.error(f"Error processing Organization Listed data: {str(e)}")

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
    try:
        change_reason_description_data = parse_change_reason_description(xml_content)
        if change_reason_description_data:
            merge_change_reason_description(release_json, change_reason_description_data)
        else:
            logger.info("No Change Reason Description data found")
    except Exception as e:
        logger.error(f"Error processing Change Reason Description data: {str(e)}")

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

    # Parse and merge OPP-020 ExtendedDurationIndicator
    try:
        extended_duration_data = map_extended_duration_indicator(xml_content)
        if extended_duration_data["tender"]["lots"]:
            merge_extended_duration_indicator(release_json, extended_duration_data)
            logger.info("Merged ExtendedDurationIndicator data")
        else:
            logger.info("No ExtendedDurationIndicator data found")
    except Exception as e:
        logger.error(f"Error processing ExtendedDurationIndicator data: {str(e)}")    

    # Parse and merge OPP-021_Contract Essential Assets
    try:
        essential_assets_data = map_essential_assets(xml_content)
        if essential_assets_data["tender"]["lots"]:
            merge_essential_assets(release_json, essential_assets_data)
            logger.info("Merged Essential Assets data")
        else:
            logger.info("No Essential Assets data found")
    except Exception as e:
        logger.error(f"Error processing Essential Assets data: {str(e)}")

    # Parse and merge OPP_022_Contract Asset Significance
    try:
        asset_significance_data = map_asset_significance(xml_content)
        if asset_significance_data["tender"]["lots"]:
            merge_asset_significance(release_json, asset_significance_data)
            logger.info("Merged Asset Significance data")
        else:
            logger.info("No Asset Significance data found")
    except Exception as e:
        logger.error(f"Error processing Asset Significance data: {str(e)}")

    # Parse and merge OPP_023_Contract Asset Predominance
    try:
        asset_predominance_data = map_asset_predominance(xml_content)
        if asset_predominance_data["tender"]["lots"]:
            merge_asset_predominance(release_json, asset_predominance_data)
            logger.info("Merged Asset Predominance data")
        else:
            logger.info("No Asset Predominance data found")
    except Exception as e:
        logger.error(f"Error processing Asset Predominance data: {str(e)}")

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
    previous_notice_data = parse_previous_notice_identifier(xml_content)
    if previous_notice_data:
        merge_previous_notice_identifier(release_json, previous_notice_data)
    else:
        logger.warning("No Previous Notice Identifier data found")

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
    touchpoint_data = parse_touchpoint_technical_identifier(xml_content)
    if touchpoint_data:
        merge_touchpoint_technical_identifier(release_json, touchpoint_data)
    else:
        logger.warning("No TouchPoint Technical Identifier data found")
    
    logger.info("Processing OPT-202-UBO: Beneficial Owner Technical Identifier")
    beneficial_owner_id_data = parse_beneficial_owner_identifier(xml_content)
    if beneficial_owner_id_data:
      #  logger.info(f"Beneficial owner data found: {beneficial_owner_id_data}")
        merge_beneficial_owner_identifier(release_json, beneficial_owner_id_data)
     #   logger.info("After merging beneficial owner data:")
     #   logger.info(json.dumps(release_json, indent=2))
    else:
        logger.warning("No Beneficial Owner Technical Identifier data found")

    # Parse and merge OPT-300 Contract Signatory
    signatory_data = parse_contract_signatory(xml_content)
    if signatory_data:
        merge_contract_signatory(release_json, signatory_data)
    else:
        logger.warning("No Contract Signatory data found")

    # Parse and merge OPT-300 sprovider
    sprovider_data = parse_procedure_sprovider(xml_content)
    if sprovider_data:
        merge_procedure_sprovider(release_json, sprovider_data)
    else:
        logger.warning("No Procedure Service Provider data found")

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

    # Parse and merge OPT_301_Lot_TenderEval
    try:
        tender_evaluator_data = parse_tender_evaluator_identifier(xml_content)
        if tender_evaluator_data:
            merge_tender_evaluator_identifier(release_json, tender_evaluator_data)
        else:
            logger.info("No Tender Evaluator Identifier data found")
    except Exception as e:
        logger.error(f"Error processing Tender Evaluator Identifier data: {str(e)}")

    # Parse and merge OPT-301-Lot-TenderReceipt Tender Recipient Technical Identifier Reference
    logger.info("Processing OPT-301-Lot-TenderReceipt: Tender Recipient Technical Identifier Reference")
    recipient_data = parse_tender_recipient_identifier(xml_content)
    if recipient_data:
        merge_tender_recipient_identifier(release_json, recipient_data)
    else:
        logger.warning("No Tender Recipient Technical Identifier Reference data found")

    # Parse and merge OPT-301 LotResult_Financing
    financing_data = parse_lotresult_financing(xml_content)
    if financing_data:
        merge_lotresult_financing(release_json, financing_data)
    else:
        logger.warning("No LotResult Financing data found")

    # Parse and merge OPT-301 LotResult_Paying
    paying_data = parse_lotresult_paying(xml_content)
    if paying_data:
        merge_lotresult_paying(release_json, paying_data)
    else:
        logger.warning("No LotResult Paying data found")

    # Parse and merge OPT-301 Part_AddInfo
    addinfo_data = parse_part_addinfo(xml_content)
    if addinfo_data:
        merge_part_addinfo(release_json, addinfo_data)
    else:
        logger.warning("No Part Additional Info data found")

    # Parse and merge OPT_301_Part_DocProvider
    docprovider_data = parse_part_docprovider(xml_content)
    if docprovider_data:
        merge_part_docprovider(release_json, docprovider_data)
    else:
        logger.warning("No Part Document Provider data found")

    # Parse and merge OPT_301_Part_EmployLegis
    employlegis_data = parse_part_employlegis(xml_content)
    if employlegis_data:
        merge_part_employlegis(release_json, employlegis_data)
    else:
        logger.warning("No Part Employment Legislation data found")
    
    # Parse and merge OPT_301_Part_EnvironLegis
    environlegis_data = parse_part_environlegis(xml_content)
    if environlegis_data:
        merge_part_environlegis(release_json, environlegis_data)
    else:
        logger.warning("No Part Environmental Legislation data found")

    # Parse and merge OPT_301_Part_FiscalLegis
    fiscallegis_data = parse_part_fiscallegis(xml_content)
    if fiscallegis_data:
        merge_part_fiscallegis(release_json, fiscallegis_data)
    else:
        logger.warning("No Part Fiscal Legislation data found")

    # Parse and merge OPT_301_Part_Mediator
    mediator_data = parse_part_mediator(xml_content)
    if mediator_data:
        merge_part_mediator(release_json, mediator_data)
    else:
        logger.warning("No Part Mediator data found")

    # Parse and merge OPT_301_Part_ReviewInfo
    reviewinfo_data = parse_part_reviewinfo(xml_content)
    if reviewinfo_data:
        merge_part_reviewinfo(release_json, reviewinfo_data)
    else:
        logger.warning("No Part Review Info data found")

    # Parse and merge OPT_301_Part_ReviewOrg
    revieworg_data = parse_part_revieworg(xml_content)
    if revieworg_data:
        merge_part_revieworg(release_json, revieworg_data)
    else:
        logger.warning("No Part Review Organization data found")

    # Parse and merge OPT_301_Part_TenderEval
    tendereval_data = parse_part_tendereval(xml_content)
    if tendereval_data:
        merge_part_tendereval(release_json, tendereval_data)
    else:
        logger.warning("No Part Tender Evaluator data found")

    # Parse and merge OPT_301_Part_TenderReceipt
    tenderreceipt_data = parse_part_tenderreceipt(xml_content)
    if tenderreceipt_data:
        merge_part_tenderreceipt(release_json, tenderreceipt_data)
    else:
        logger.warning("No Part Tender Recipient data found")

    # Parse and merge OPT_301_Tenderer_MainCont
    maincont_data = parse_tenderer_maincont(xml_content)
    if maincont_data:
        merge_tenderer_maincont(release_json, maincont_data)
    else:
        logger.warning("No Tenderer Main Contractor data found")
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
    release_json = remove_empty_dicts(release_json)

    #logger.info(f"Final release_json: {json.dumps(release_json, indent=2)}")
    
    # Write the JSON output to a file
    with io.open('output.json', 'w', encoding='utf-8') as f:
        json.dump(release_json, f, ensure_ascii=False)

    logger.info("XML to JSON conversion completed")

    # Print the JSON string to console
    json_string = json.dumps(release_json, ensure_ascii=False)
    

    return release_json

if __name__ == "__main__":
    # Path to the XML file
    xml_path = 'xmlfile/can_24_minimal.xml'
    # Prefix for OCID
    ocid_prefix = 'ocid_prefix_value'
    
    main(xml_path, ocid_prefix)