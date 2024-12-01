import logging
from collections.abc import Callable, Sequence
from typing import Any

from ted_and_doffin_to_ocds.converters.bt_01_procedure import (
    merge_procedure_legal_basis,
    parse_procedure_legal_basis,
)
from ted_and_doffin_to_ocds.converters.bt_03 import merge_form_type, parse_form_type
from ted_and_doffin_to_ocds.converters.bt_04_procedure import (
    merge_procedure_identifier,
    parse_procedure_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_05_notice import (
    merge_notice_dispatch_date_time,
    parse_notice_dispatch_date_time,
)
from ted_and_doffin_to_ocds.converters.bt_06_lot import (
    merge_strategic_procurement,
    parse_strategic_procurement,
)
from ted_and_doffin_to_ocds.converters.bt_09_procedure import (
    merge_cross_border_law,
    parse_cross_border_law,
)
from ted_and_doffin_to_ocds.converters.bt_10 import (
    merge_authority_activity,
    parse_authority_activity,
)
from ted_and_doffin_to_ocds.converters.bt_11_procedure_buyer import (
    merge_buyer_legal_type,
    parse_buyer_legal_type,
)
from ted_and_doffin_to_ocds.converters.bt_13_lot import (
    merge_additional_info_deadline,
    parse_additional_info_deadline,
)
from ted_and_doffin_to_ocds.converters.bt_13_part import (
    merge_additional_info_deadline_part,
    parse_additional_info_deadline_part,
)
from ted_and_doffin_to_ocds.converters.bt_14_lot import (
    merge_lot_documents_restricted,
    parse_lot_documents_restricted,
)
from ted_and_doffin_to_ocds.converters.bt_14_part import (
    merge_part_documents_restricted,
    parse_part_documents_restricted,
)
from ted_and_doffin_to_ocds.converters.bt_15_lot_part import (
    merge_documents_url,
    parse_documents_url,
)
from ted_and_doffin_to_ocds.converters.bt_16_organization_company import (
    merge_organization_part_name,
    parse_organization_part_name,
)
from ted_and_doffin_to_ocds.converters.bt_16_organization_touchpoint import (
    merge_organization_touchpoint_part_name,
    parse_organization_touchpoint_part_name,
)
from ted_and_doffin_to_ocds.converters.bt_17_lot import (
    merge_submission_electronic,
    parse_submission_electronic,
)
from ted_and_doffin_to_ocds.converters.bt_18_lot import (
    merge_submission_url,
    parse_submission_url,
)
from ted_and_doffin_to_ocds.converters.bt_19_lot import (
    merge_submission_nonelectronic_justification,
    parse_submission_nonelectronic_justification,
)
from ted_and_doffin_to_ocds.converters.bt_21_lot import merge_lot_title, parse_lot_title
from ted_and_doffin_to_ocds.converters.bt_21_lotsgroup import (
    merge_lots_group_title,
    parse_lots_group_title,
)
from ted_and_doffin_to_ocds.converters.bt_21_part import (
    merge_part_title,
    parse_part_title,
)
from ted_and_doffin_to_ocds.converters.bt_21_procedure import (
    merge_procedure_title,
    parse_procedure_title,
)
from ted_and_doffin_to_ocds.converters.bt_22_lot import (
    merge_lot_internal_identifier,
    parse_lot_internal_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_23_lot import (
    merge_main_nature,
    parse_main_nature,
)
from ted_and_doffin_to_ocds.converters.bt_23_part import (
    merge_main_nature_part,
    parse_main_nature_part,
)
from ted_and_doffin_to_ocds.converters.bt_23_procedure import (
    merge_main_nature_procedure,
    parse_main_nature_procedure,
)
from ted_and_doffin_to_ocds.converters.bt_24_lot import (
    merge_lot_description,
    parse_lot_description,
)
from ted_and_doffin_to_ocds.converters.bt_24_lotsgroup import (
    merge_lots_group_description,
    parse_lots_group_description,
)
from ted_and_doffin_to_ocds.converters.bt_24_part import (
    merge_part_description,
    parse_part_description,
)
from ted_and_doffin_to_ocds.converters.bt_24_procedure import (
    merge_procedure_description,
    parse_procedure_description,
)
from ted_and_doffin_to_ocds.converters.bt_25_lot import (
    merge_lot_quantity,
    parse_lot_quantity,
)
from ted_and_doffin_to_ocds.converters.bt_26a_lot import (
    merge_classification_type,
    parse_classification_type,
)
from ted_and_doffin_to_ocds.converters.bt_26a_part import (
    merge_classification_type_part,
    parse_classification_type_part,
)
from ted_and_doffin_to_ocds.converters.bt_26a_procedure import (
    merge_classification_type_procedure,
    parse_classification_type_procedure,
)
from ted_and_doffin_to_ocds.converters.bt_26m_lot import (
    merge_main_classification_type_lot,
    parse_main_classification_type_lot,
)
from ted_and_doffin_to_ocds.converters.bt_26m_part import (
    merge_main_classification_type_part,
    parse_main_classification_type_part,
)
from ted_and_doffin_to_ocds.converters.bt_26m_procedure import (
    merge_main_classification_type_procedure,
    parse_main_classification_type_procedure,
)
from ted_and_doffin_to_ocds.converters.bt_27_lot import (
    merge_lot_estimated_value,
    parse_lot_estimated_value,
)
from ted_and_doffin_to_ocds.converters.bt_27_lotsgroup import (
    merge_bt_27_lots_group,
    parse_bt_27_lots_group,
)
from ted_and_doffin_to_ocds.converters.bt_27_part import (
    merge_bt_27_part,
    parse_bt_27_part,
)
from ted_and_doffin_to_ocds.converters.bt_27_procedure import (
    merge_bt_27_procedure,
    parse_bt_27_procedure,
)
from ted_and_doffin_to_ocds.converters.bt_31_procedure import (
    merge_max_lots_allowed,
    parse_max_lots_allowed,
)
from ted_and_doffin_to_ocds.converters.bt_33_procedure import (
    merge_max_lots_awarded,
    parse_max_lots_awarded,
)
from ted_and_doffin_to_ocds.converters.bt_36_lot import (
    merge_lot_duration,
    parse_lot_duration,
)
from ted_and_doffin_to_ocds.converters.bt_36_part import (
    merge_part_duration,
    parse_part_duration,
)
from ted_and_doffin_to_ocds.converters.bt_40_lot import (
    merge_lot_selection_criteria_second_stage,
    parse_lot_selection_criteria_second_stage,
)
from ted_and_doffin_to_ocds.converters.bt_41_lot import (
    merge_lot_following_contract,
    parse_lot_following_contract,
)
from ted_and_doffin_to_ocds.converters.bt_42_lot import (
    merge_lot_jury_decision_binding,
    parse_lot_jury_decision_binding,
)
from ted_and_doffin_to_ocds.converters.bt_44_lot import (
    merge_prize_rank,
    parse_prize_rank,
)
from ted_and_doffin_to_ocds.converters.bt_45_lot import (
    merge_lot_rewards_other,
    parse_lot_rewards_other,
)
from ted_and_doffin_to_ocds.converters.bt_46_lot import (
    merge_jury_member_name,
    parse_jury_member_name,
)
from ted_and_doffin_to_ocds.converters.bt_47_lot import (
    merge_participant_name,
    parse_participant_name,
)
from ted_and_doffin_to_ocds.converters.bt_50_lot import (
    merge_minimum_candidates,
    parse_minimum_candidates,
)
from ted_and_doffin_to_ocds.converters.bt_51_lot import (
    merge_lot_maximum_candidates,
    parse_lot_maximum_candidates,
)
from ted_and_doffin_to_ocds.converters.bt_52_lot import (
    merge_successive_reduction_indicator,
    parse_successive_reduction_indicator,
)
from ted_and_doffin_to_ocds.converters.bt_54_lot import (
    merge_options_description,
    parse_options_description,
)
from ted_and_doffin_to_ocds.converters.bt_57_lot import (
    merge_renewal_description,
    parse_renewal_description,
)
from ted_and_doffin_to_ocds.converters.bt_58_lot import (
    merge_renewal_maximum,
    parse_renewal_maximum,
)
from ted_and_doffin_to_ocds.converters.bt_60_lot import merge_eu_funds, parse_eu_funds
from ted_and_doffin_to_ocds.converters.bt_63_lot import merge_variants, parse_variants
from ted_and_doffin_to_ocds.converters.bt_64_lot import (
    merge_subcontracting_obligation_minimum,
    parse_subcontracting_obligation_minimum,
)
from ted_and_doffin_to_ocds.converters.bt_65_lot_subcontracting_obligation import (
    merge_subcontracting_obligation,
    parse_subcontracting_obligation,
)
from ted_and_doffin_to_ocds.converters.bt_67_exclusion_grounds import (
    merge_exclusion_grounds,
    parse_exclusion_grounds,
)
from ted_and_doffin_to_ocds.converters.bt_70_lot import (
    merge_lot_performance_terms,
    parse_lot_performance_terms,
)
from ted_and_doffin_to_ocds.converters.bt_71_lot import (
    merge_reserved_participation,
    parse_reserved_participation,
)
from ted_and_doffin_to_ocds.converters.bt_71_part import (
    merge_reserved_participation_part,
    parse_reserved_participation_part,
)

# from ted_and_doffin_to_ocds.converters.bt_749_lot import parse_selection_criteria_name, merge_selection_criteria_name
from ted_and_doffin_to_ocds.converters.bt_75_lot import (
    merge_guarantee_required_description,
    parse_guarantee_required_description,
)
from ted_and_doffin_to_ocds.converters.bt_76_lot import (
    merge_tenderer_legal_form,
    parse_tenderer_legal_form,
)
from ted_and_doffin_to_ocds.converters.bt_77_lot import (
    merge_financial_terms,
    parse_financial_terms,
)
from ted_and_doffin_to_ocds.converters.bt_78_lot import (
    merge_security_clearance_deadline,
    parse_security_clearance_deadline,
)
from ted_and_doffin_to_ocds.converters.bt_79_lot import (
    merge_performing_staff_qualification,
    parse_performing_staff_qualification,
)
from ted_and_doffin_to_ocds.converters.bt_88_procedure import (
    merge_procedure_features,
    parse_procedure_features,
)
from ted_and_doffin_to_ocds.converters.bt_92_lot import (
    merge_electronic_ordering,
    parse_electronic_ordering,
)
from ted_and_doffin_to_ocds.converters.bt_93_lot import (
    merge_electronic_payment,
    parse_electronic_payment,
)
from ted_and_doffin_to_ocds.converters.bt_94_lot import (
    merge_recurrence,
    parse_recurrence,
)
from ted_and_doffin_to_ocds.converters.bt_95_lot import (
    merge_recurrence_description,
    parse_recurrence_description,
)
from ted_and_doffin_to_ocds.converters.bt_97_lot import (
    merge_submission_language,
    parse_submission_language,
)
from ted_and_doffin_to_ocds.converters.bt_98_lot import (
    merge_tender_validity_deadline,
    parse_tender_validity_deadline,
)
from ted_and_doffin_to_ocds.converters.bt_99_lot import (
    merge_review_deadline_description,
    parse_review_deadline_description,
)
from ted_and_doffin_to_ocds.converters.bt_105_procedure import (
    merge_procedure_type,
    parse_procedure_type,
)
from ted_and_doffin_to_ocds.converters.bt_106_procedure import (
    merge_procedure_accelerated,
    parse_procedure_accelerated,
)
from ted_and_doffin_to_ocds.converters.bt_109_lot import (
    merge_framework_duration_justification,
    parse_framework_duration_justification,
)
from ted_and_doffin_to_ocds.converters.bt_111_lot import (
    merge_framework_buyer_categories,
    parse_framework_buyer_categories,
)
from ted_and_doffin_to_ocds.converters.bt_113_lot import (
    merge_framework_max_participants,
    parse_framework_max_participants,
)
from ted_and_doffin_to_ocds.converters.bt_115_gpa_coverage import (
    merge_gpa_coverage,
    parse_gpa_coverage,
)
from ted_and_doffin_to_ocds.converters.bt_119_lotresult import (
    merge_dps_termination,
    parse_dps_termination,
)
from ted_and_doffin_to_ocds.converters.bt_120_lot import (
    merge_no_negotiation_necessary,
    parse_no_negotiation_necessary,
)
from ted_and_doffin_to_ocds.converters.bt_122_lot import (
    merge_electronic_auction_description,
    parse_electronic_auction_description,
)
from ted_and_doffin_to_ocds.converters.bt_123_lot import (
    merge_electronic_auction_url,
    parse_electronic_auction_url,
)
from ted_and_doffin_to_ocds.converters.bt_124_tool_atypical_url import (
    merge_tool_atypical_url,
    parse_tool_atypical_url,
)
from ted_and_doffin_to_ocds.converters.bt_125_lot import (
    merge_previous_planning_identifier_lot,
    parse_previous_planning_identifier_lot,
)
from ted_and_doffin_to_ocds.converters.bt_125_part import (
    merge_previous_planning_identifier_part,
    parse_previous_planning_identifier_part,
)
from ted_and_doffin_to_ocds.converters.bt_127_notice import (
    merge_future_notice_date,
    parse_future_notice_date,
)
from ted_and_doffin_to_ocds.converters.bt_130_lot import (
    merge_dispatch_invitation_tender,
    parse_dispatch_invitation_tender,
)
from ted_and_doffin_to_ocds.converters.bt_131_lot import (
    merge_deadline_receipt_tenders,
    parse_deadline_receipt_tenders,
)
from ted_and_doffin_to_ocds.converters.bt_132_lot import (
    merge_lot_public_opening_date,
    parse_lot_public_opening_date,
)
from ted_and_doffin_to_ocds.converters.bt_133_lot import (
    merge_lot_bid_opening_location,
    parse_lot_bid_opening_location,
)
from ted_and_doffin_to_ocds.converters.bt_134_lot import (
    merge_lot_public_opening_description,
    parse_lot_public_opening_description,
)
from ted_and_doffin_to_ocds.converters.bt_135_procedure import (
    merge_direct_award_justification_rationale,
    parse_direct_award_justification_rationale,
)
from ted_and_doffin_to_ocds.converters.bt_136_procedure import (
    merge_direct_award_justification_code,
    parse_direct_award_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_137_lot import (
    merge_purpose_lot_identifier,
    parse_purpose_lot_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_137_lotsgroup import (
    merge_lots_group_identifier,
    parse_lots_group_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_137_part import (
    merge_part_identifier,
    parse_part_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_140_notice import (
    merge_change_reason_code,
    parse_change_reason_code,
)
from ted_and_doffin_to_ocds.converters.bt_142_lotresult import (
    merge_winner_chosen,
    parse_winner_chosen,
)
from ted_and_doffin_to_ocds.converters.bt_144_lotresult import (
    merge_not_awarded_reason,
    parse_not_awarded_reason,
)
from ted_and_doffin_to_ocds.converters.bt_145_contract import (
    merge_contract_conclusion_date,
    parse_contract_conclusion_date,
)
from ted_and_doffin_to_ocds.converters.bt_150_contract import (
    merge_contract_identifier,
    parse_contract_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_151_contract import (
    merge_contract_url,
    parse_contract_url,
)
from ted_and_doffin_to_ocds.converters.bt_160_tender import (
    merge_concession_revenue_buyer,
    parse_concession_revenue_buyer,
)
from ted_and_doffin_to_ocds.converters.bt_162_tender import (
    merge_concession_revenue_user,
    parse_concession_revenue_user,
)
from ted_and_doffin_to_ocds.converters.bt_163_tender import (
    merge_concession_value_description,
    parse_concession_value_description,
)
from ted_and_doffin_to_ocds.converters.bt_165_organization_company import (
    merge_winner_size,
    parse_winner_size,
)
from ted_and_doffin_to_ocds.converters.bt_171_tender import (
    merge_tender_rank,
    parse_tender_rank,
)
from ted_and_doffin_to_ocds.converters.bt_191_tender import (
    merge_country_origin,
    parse_country_origin,
)
from ted_and_doffin_to_ocds.converters.bt_193_tender import (
    merge_tender_variant,
    parse_tender_variant,
)

# BT_195
from ted_and_doffin_to_ocds.converters.bt_195_bt_09_procedure import (
    bt_195_merge_unpublished_identifier_bt_09_procedure,
    bt_195_parse_unpublished_identifier_bt_09_procedure,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_88_procedure import (
    merge_bt195_bt88_procedure_unpublished_identifier,
    parse_bt195_bt88_procedure_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_105_procedure import (
    merge_bt195_bt105_unpublished_identifier,
    parse_bt195_bt105_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_106_procedure import (
    merge_bt195_bt106_unpublished_identifier,
    parse_bt195_bt106_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_135_procedure import (
    merge_bt195_bt135_unpublished_identifier,
    parse_bt195_bt135_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_136_procedure import (
    merge_bt195_bt136_unpublished_identifier,
    parse_bt195_bt136_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_142_lotresult import (
    merge_bt195_bt142_unpublished_identifier,
    parse_bt195_bt142_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_144_lotresult import (
    merge_bt195_bt144_unpublished_identifier,
    parse_bt195_bt144_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_160_tender import (
    merge_bt195_bt160_unpublished_identifier,
    parse_bt195_bt160_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_162_tender import (
    merge_bt195_bt162_unpublished_identifier,
    parse_bt195_bt162_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_163_tender import (
    merge_bt195_bt163_unpublished_identifier,
    parse_bt195_bt163_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_171_tender import (
    merge_bt195_bt171_unpublished_identifier,
    parse_bt195_bt171_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_191_tender import (
    merge_bt195_bt191_unpublished_identifier,
    parse_bt195_bt191_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_193_tender import (
    merge_bt195_bt193_unpublished_identifier,
    parse_bt195_bt193_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_539_lot import (
    merge_bt195_bt539_unpublished_identifier,
    parse_bt195_bt539_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_539_lotsgroup import (
    merge_bt195_bt539_lotsgroup_unpublished_identifier,
    parse_bt195_bt539_lotsgroup_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_540_lot import (
    merge_bt195_bt540_lot_unpublished_identifier,
    parse_bt195_bt540_lot_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_540_lotsgroup import (
    merge_bt195_bt540_lotsgroup_unpublished_identifier,
    parse_bt195_bt540_lotsgroup_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_541_lot_fixed import (
    merge_bt195_bt541_lot_fixed_unpublished_identifier,
    parse_bt195_bt541_lot_fixed_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_541_lot_threshold import (
    merge_bt195_bt541_lot_threshold_unpublished_identifier,
    parse_bt195_bt541_lot_threshold_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_541_lot_weight import (
    merge_bt195_bt541_lot_weight_unpublished_identifier,
    parse_bt195_bt541_lot_weight_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_541_lotsgroup_fixed import (
    merge_bt195_bt541_lotsgroup_fixed_unpublished_identifier,
    parse_bt195_bt541_lotsgroup_fixed_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_541_lotsgroup_threshold import (
    merge_bt195_bt541_lotsgroup_threshold_unpublished_identifier,
    parse_bt195_bt541_lotsgroup_threshold_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_541_lotsgroup_weight import (
    merge_bt195_bt541_lotsgroup_weight,
    parse_bt195_bt541_lotsgroup_weight,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_543_lot import (
    merge_bt195_bt543_lot,
    parse_bt195_bt543_lot,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_543_lotsgroup import (
    merge_bt195_bt543_lotsgroup,
    parse_bt195_bt543_lotsgroup,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_553_tender import (
    merge_bt195_bt553_tender,
    parse_bt195_bt553_tender,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_554_tender import (
    merge_bt195_bt554_unpublished_identifier,
    parse_bt195_bt554_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_555_tender import (
    merge_bt195_bt555_unpublished_identifier,
    parse_bt195_bt555_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_635_lotresult import (
    merge_bt195_bt635_unpublished_identifier,
    parse_bt195_bt635_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_636_lotresult import (
    merge_bt195_bt636_unpublished_identifier,
    parse_bt195_bt636_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_660_lotresult import (
    merge_bt195_bt660_unpublished_identifier,
    parse_bt195_bt660_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_709_lotresult import (
    merge_bt195_bt709_unpublished_identifier,
    parse_bt195_bt709_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_710_lotresult import (
    merge_bt195_bt710_unpublished_identifier,
    parse_bt195_bt710_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_711_lotresult import (
    merge_bt195_bt711_unpublished_identifier,
    parse_bt195_bt711_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_712_lotresult import (
    merge_bt195_bt712_unpublished_identifier,
    parse_bt195_bt712_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_720_tender import (
    merge_bt195_bt720_unpublished_identifier,
    parse_bt195_bt720_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_733_lot import (
    merge_bt195_bt733_unpublished_identifier,
    parse_bt195_bt733_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_733_lotsgroup import (
    merge_bt195_bt733_lotsgroup_unpublished_identifier,
    parse_bt195_bt733_lotsgroup_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_734_lot import (
    merge_bt195_bt734_lot_unpublished_identifier,
    parse_bt195_bt734_lot_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_734_lotsgroup import (
    merge_bt195_bt734_lotsgroup_unpublished_identifier,
    parse_bt195_bt734_lotsgroup_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_759_lotresult import (
    merge_bt195_bt759_lotresult_unpublished_identifier,
    parse_bt195_bt759_lotresult_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_760_lotresult import (
    merge_bt195_bt760_lotresult_unpublished_identifier,
    parse_bt195_bt760_lotresult_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_773_tender import (
    merge_bt195_bt773_tender_unpublished_identifier,
    parse_bt195_bt773_tender_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_1252_procedure import (
    merge_bt195_bt1252_unpublished_identifier,
    parse_bt195_bt1252_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_1351_procedure import (
    merge_bt195_bt1351_unpublished_identifier,
    parse_bt195_bt1351_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_5421_lot import (
    merge_bt195_bt5421_lot,
    parse_bt195_bt5421_lot,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_5421_lotsgroup import (
    merge_bt195_bt5421_lotsgroup,
    parse_bt195_bt5421_lotsgroup,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_5422_lot import (
    merge_bt195_bt5422_lot,
    parse_bt195_bt5422_lot,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_5422_lotsgroup import (
    merge_bt195_bt5422_lotsgroup,
    parse_bt195_bt5422_lotsgroup,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_5423_lot import (
    merge_bt195_bt5423_lot,
    parse_bt195_bt5423_lot,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_5423_lotsgroup import (
    merge_bt195_bt5423_lotsgroup,
    parse_bt195_bt5423_lotsgroup,
)

# BT_196
from ted_and_doffin_to_ocds.converters.bt_196_bt_09_procedure import (
    bt_196_merge_unpublished_justification_bt_09_procedure,
    bt_196_parse_unpublished_justification_bt_09_procedure,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_88_procedure import (
    merge_bt196_bt88_procedure_unpublished_justification,
    parse_bt196_bt88_procedure_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_105_procedure import (
    merge_bt196_bt105_unpublished_justification,
    parse_bt196_bt105_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_106_procedure import (
    merge_bt196_bt106_unpublished_justification,
    parse_bt196_bt106_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_135_procedure import (
    merge_bt196_bt135_unpublished_justification,
    parse_bt196_bt135_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_136_procedure import (
    merge_bt196_bt136_unpublished_justification,
    parse_bt196_bt136_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_142_lotresult import (
    merge_bt196_bt142_unpublished_justification,
    parse_bt196_bt142_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_144_lotresult import (
    merge_bt196_bt144_unpublished_justification,
    parse_bt196_bt144_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_160_tender import (
    merge_bt196_bt160_unpublished_justification,
    parse_bt196_bt160_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_162_tender import (
    merge_bt196_bt162_unpublished_justification,
    parse_bt196_bt162_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_163_tender import (
    merge_bt196_bt163_unpublished_justification,
    parse_bt196_bt163_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_171_tender import (
    merge_bt196_bt171_unpublished_justification,
    parse_bt196_bt171_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_191_tender import (
    merge_bt196_bt191_unpublished_justification,
    parse_bt196_bt191_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_193_tender import (
    merge_bt196_bt193_unpublished_justification,
    parse_bt196_bt193_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_539_lot import (
    merge_bt196_bt539_unpublished_justification,
    parse_bt196_bt539_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_539_lotsgroup import (
    merge_bt196_bt539_lotsgroup_unpublished_justification,
    parse_bt196_bt539_lotsgroup_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_540_lot import (
    merge_bt196_bt540_lot_unpublished_justification,
    parse_bt196_bt540_lot_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_540_lotsgroup import (
    merge_bt196_bt540_lotsgroup_unpublished_justification,
    parse_bt196_bt540_lotsgroup_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_541_lot_fixed import (
    merge_bt196_bt541_lot_fixed_unpublished_justification,
    parse_bt196_bt541_lot_fixed_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_541_lot_threshold import (
    merge_bt196_bt541_lot_threshold_unpublished_justification,
    parse_bt196_bt541_lot_threshold_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_541_lot_weight import (
    merge_bt196_bt541_lot_weight_unpublished_justification,
    parse_bt196_bt541_lot_weight_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_541_lotsgroup_fixed import (
    merge_bt196_bt541_lotsgroup_fixed_unpublished_justification,
    parse_bt196_bt541_lotsgroup_fixed_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_541_lotsgroup_threshold import (
    merge_bt196_bt541_lotsgroup_threshold_unpublished_justification,
    parse_bt196_bt541_lotsgroup_threshold_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_541_lotsgroup_weight import (
    merge_bt196_bt541_lotsgroup_weight,
    parse_bt196_bt541_lotsgroup_weight,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_543_lot import (
    merge_bt196_bt543_lot,
    parse_bt196_bt543_lot,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_543_lotsgroup import (
    merge_bt196_bt543_lotsgroup,
    parse_bt196_bt543_lotsgroup,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_553_tender import (
    merge_bt196_bt553_tender,
    parse_bt196_bt553_tender,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_554_tender import (
    merge_bt196_bt554_unpublished_justification,
    parse_bt196_bt554_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_555_tender import (
    merge_bt196_bt555_unpublished_justification,
    parse_bt196_bt555_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_635_lotresult import (
    merge_bt196_bt635_unpublished_justification,
    parse_bt196_bt635_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_636_lotresult import (
    merge_bt196_bt636_unpublished_justification,
    parse_bt196_bt636_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_660_lotresult import (
    merge_bt196_bt660_unpublished_justification,
    parse_bt196_bt660_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_709_lotresult import (
    merge_bt196_bt709_unpublished_justification,
    parse_bt196_bt709_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_710_lotresult import (
    merge_bt196_bt710_unpublished_justification,
    parse_bt196_bt710_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_711_lotresult import (
    merge_bt196_bt711_unpublished_justification,
    parse_bt196_bt711_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_712_lotresult import (
    merge_bt196_bt712_unpublished_justification,
    parse_bt196_bt712_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_720_tender import (
    merge_bt196_bt720_unpublished_justification,
    parse_bt196_bt720_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_733_lot import (
    merge_bt196_bt733_unpublished_justification,
    parse_bt196_bt733_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_733_lotsgroup import (
    merge_bt196_bt733_lotsgroup_unpublished_justification,
    parse_bt196_bt733_lotsgroup_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_734_lot import (
    merge_bt196_bt734_lot_unpublished_justification,
    parse_bt196_bt734_lot_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_734_lotsgroup import (
    merge_bt196_bt734_lotsgroup_unpublished_justification,
    parse_bt196_bt734_lotsgroup_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_759_lotresult import (
    merge_bt196_bt759_lotresult_unpublished_justification,
    parse_bt196_bt759_lotresult_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_760_lotresult import (
    merge_bt196_bt760_lotresult_unpublished_justification,
    parse_bt196_bt760_lotresult_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_773_tender import (
    merge_bt196_bt773_tender_unpublished_justification,
    parse_bt196_bt773_tender_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_1252_procedure import (
    merge_bt196_bt1252_unpublished_justification,
    parse_bt196_bt1252_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_1351_procedure import (
    merge_bt196_bt1351_unpublished_justification,
    parse_bt196_bt1351_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_5421_lot import (
    merge_bt196_bt5421_lot,
    parse_bt196_bt5421_lot,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_5421_lotsgroup import (
    merge_bt196_bt5421_lotsgroup,
    parse_bt196_bt5421_lotsgroup,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_5422_lot import (
    merge_bt196_bt5422_lot,
    parse_bt196_bt5422_lot,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_5422_lotsgroup import (
    merge_bt196_bt5422_lotsgroup,
    parse_bt196_bt5422_lotsgroup,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_5423_lot import (
    merge_bt196_bt5423_lot,
    parse_bt196_bt5423_lot,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_5423_lotsgroup import (
    merge_bt196_bt5423_lotsgroup,
    parse_bt196_bt5423_lotsgroup,
)

# #BT_197
from ted_and_doffin_to_ocds.converters.bt_197_bt_09_procedure import (
    bt_197_merge_unpublished_justification_code_bt_09_procedure,
    bt_197_parse_unpublished_justification_code_bt_09_procedure,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_88_procedure import (
    merge_bt197_bt88_procedure_unpublished_justification_code,
    parse_bt197_bt88_procedure_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_105_procedure import (
    merge_bt197_bt105_unpublished_justification_code,
    parse_bt197_bt105_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_106_procedure import (
    merge_bt197_bt106_unpublished_justification_code,
    parse_bt197_bt106_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_135_procedure import (
    merge_bt197_bt135_unpublished_justification_code,
    parse_bt197_bt135_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_136_procedure import (
    merge_bt197_bt136_unpublished_justification_code,
    parse_bt197_bt136_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_142_lotresult import (
    merge_bt197_bt142_unpublished_justification_code,
    parse_bt197_bt142_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_144_lotresult import (
    merge_bt197_bt144_unpublished_justification_code,
    parse_bt197_bt144_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_160_tender import (
    merge_bt197_bt160_unpublished_justification_code,
    parse_bt197_bt160_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_162_tender import (
    merge_bt197_bt162_unpublished_justification_code,
    parse_bt197_bt162_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_163_tender import (
    merge_bt197_bt163_unpublished_justification_code,
    parse_bt197_bt163_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_171_tender import (
    merge_bt197_bt171_unpublished_justification_code,
    parse_bt197_bt171_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_191_tender import (
    merge_bt197_bt191_unpublished_justification_code,
    parse_bt197_bt191_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_193_tender import (
    merge_bt197_bt193_unpublished_justification_code,
    parse_bt197_bt193_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_539_lot import (
    merge_bt197_bt539_unpublished_justification_code,
    parse_bt197_bt539_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_539_lotsgroup import (
    merge_bt197_bt539_lotsgroup_unpublished_justification_code,
    parse_bt197_bt539_lotsgroup_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_540_lot import (
    merge_bt197_bt540_lot_unpublished_justification_code,
    parse_bt197_bt540_lot_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_540_lotsgroup import (
    merge_bt197_bt540_lotsgroup_unpublished_justification_code,
    parse_bt197_bt540_lotsgroup_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_541_lot_fixed import (
    merge_bt197_bt541_lot_fixed_unpublished_justification_code,
    parse_bt197_bt541_lot_fixed_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_541_lot_threshold import (
    merge_bt197_bt541_lot_threshold_unpublished_justification_code,
    parse_bt197_bt541_lot_threshold_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_541_lot_weight import (
    merge_bt197_bt541_lot_weight_unpublished_justification_code,
    parse_bt197_bt541_lot_weight_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_541_lotsgroup import (
    merge_bt197_bt541_lotsgroup_threshold,
    parse_bt197_bt541_lotsgroup_threshold,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_541_lotsgroup_fixed import (
    merge_bt197_bt541_lotsgroup_fixed_unpublished_justification_code,
    parse_bt197_bt541_lotsgroup_fixed_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_541_lotsgroup_weight import (
    merge_bt197_bt541_lotsgroup_weight,
    parse_bt197_bt541_lotsgroup_weight,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_543_lot import (
    merge_bt197_bt543_lot,
    parse_bt197_bt543_lot,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_543_lotsgroup import (
    merge_bt197_bt543_lotsgroup,
    parse_bt197_bt543_lotsgroup,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_553_tender import (
    merge_bt197_bt553_tender,
    parse_bt197_bt553_tender,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_554_tender import (
    merge_bt197_bt554_unpublished_justification_code,
    parse_bt197_bt554_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_555_tender import (
    merge_bt197_bt555_unpublished_justification_code,
    parse_bt197_bt555_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_635_lotresult import (
    merge_bt197_bt635_unpublished_justification_code,
    parse_bt197_bt635_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_636_lotresult import (
    merge_bt197_bt636_unpublished_justification_code,
    parse_bt197_bt636_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_660_lotresult import (
    merge_bt197_bt660_unpublished_justification_code,
    parse_bt197_bt660_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_709_lotresult import (
    merge_bt197_bt709_unpublished_justification_code,
    parse_bt197_bt709_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_710_lotresult import (
    merge_bt197_bt710_unpublished_justification_code,
    parse_bt197_bt710_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_711_lotresult import (
    merge_bt197_bt711_unpublished_justification_code,
    parse_bt197_bt711_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_712_lotresult import (
    merge_bt197_bt712_unpublished_justification_code,
    parse_bt197_bt712_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_720_tender import (
    merge_bt197_bt720_unpublished_justification_code,
    parse_bt197_bt720_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_733_lot import (
    merge_bt197_bt733_unpublished_justification_code,
    parse_bt197_bt733_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_733_lotsgroup import (
    merge_bt197_bt733_lotsgroup_unpublished_justification_code,
    parse_bt197_bt733_lotsgroup_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_734_lot import (
    merge_bt197_bt734_lot_unpublished_justification_code,
    parse_bt197_bt734_lot_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_734_lotsgroup import (
    merge_bt197_bt734_lotsgroup_unpublished_justification_code,
    parse_bt197_bt734_lotsgroup_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_759_lotresult import (
    merge_bt197_bt759_lotresult_unpublished_justification_code,
    parse_bt197_bt759_lotresult_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_760_lotresult import (
    merge_bt197_bt760_lotresult_unpublished_justification_code,
    parse_bt197_bt760_lotresult_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_773_tender import (
    merge_bt197_bt773_tender_unpublished_justification_code,
    parse_bt197_bt773_tender_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_1252_procedure import (
    merge_bt197_bt1252_unpublished_justification_code,
    parse_bt197_bt1252_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_1351_procedure import (
    merge_bt197_bt1351_unpublished_justification_code,
    parse_bt197_bt1351_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_5421_lot import (
    merge_bt197_bt5421_lot,
    parse_bt197_bt5421_lot,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_5421_lotsgroup import (
    merge_bt197_bt5421_lotsgroup,
    parse_bt197_bt5421_lotsgroup,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_5422_lot import (
    merge_bt197_bt5422_lot,
    parse_bt197_bt5422_lot,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_5422_lotsgroup import (
    merge_bt197_bt5422_lotsgroup,
    parse_bt197_bt5422_lotsgroup,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_5423_lot import (
    merge_bt197_bt5423_lot,
    parse_bt197_bt5423_lot,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_5423_lotsgroup import (
    merge_bt197_bt5423_lotsgroup,
    parse_bt197_bt5423_lotsgroup,
)

#
# #BT_198
from ted_and_doffin_to_ocds.converters.bt_198_bt_09_procedure import (
    bt_198_merge_unpublished_access_date_bt_09_procedure,
    bt_198_parse_unpublished_access_date_bt_09_procedure,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_88_procedure import (
    merge_bt198_bt88_procedure_unpublished_access_date,
    parse_bt198_bt88_procedure_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_105_procedure import (
    merge_bt198_bt105_unpublished_access_date,
    parse_bt198_bt105_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_106_procedure import (
    merge_bt198_bt106_unpublished_access_date,
    parse_bt198_bt106_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_135_procedure import (
    merge_bt198_bt135_unpublished_access_date,
    parse_bt198_bt135_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_136_procedure import (
    merge_bt198_bt136_unpublished_access_date,
    parse_bt198_bt136_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_142_lotresult import (
    merge_bt198_bt142_unpublished_access_date,
    parse_bt198_bt142_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_144_lotresult import (
    merge_bt198_bt144_unpublished_access_date,
    parse_bt198_bt144_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_160_tender import (
    merge_bt198_bt160_unpublished_access_date,
    parse_bt198_bt160_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_162_tender import (
    merge_bt198_bt162_unpublished_access_date,
    parse_bt198_bt162_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_163_tender import (
    merge_bt198_bt163_unpublished_access_date,
    parse_bt198_bt163_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_171_tender import (
    merge_bt198_bt171_unpublished_access_date,
    parse_bt198_bt171_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_191_tender import (
    merge_bt198_bt191_unpublished_access_date,
    parse_bt198_bt191_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_193_tender import (
    merge_bt198_bt193_unpublished_access_date,
    parse_bt198_bt193_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_539_lot import (
    merge_bt198_bt539_unpublished_access_date,
    parse_bt198_bt539_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_539_lotsgroup import (
    merge_bt198_bt539_lotsgroup_unpublished_access_date,
    parse_bt198_bt539_lotsgroup_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_540_lot import (
    merge_bt198_bt540_lot_unpublished_access_date,
    parse_bt198_bt540_lot_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_540_lotsgroup import (
    merge_bt198_bt540_lotsgroup_unpublished_access_date,
    parse_bt198_bt540_lotsgroup_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_541_lot_fixed import (
    merge_bt198_bt541_lot_fixed_unpublished_access_date,
    parse_bt198_bt541_lot_fixed_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_541_lot_threshold import (
    merge_bt198_bt541_lot_threshold_unpublished_access_date,
    parse_bt198_bt541_lot_threshold_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_541_lot_weight import (
    merge_bt198_bt541_lot_weight_unpublished_access_date,
    parse_bt198_bt541_lot_weight_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_541_lotsgroup import (
    merge_bt198_bt541_lotsgroup_threshold,
    parse_bt198_bt541_lotsgroup_threshold,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_541_lotsgroup_fixed import (
    merge_bt198_bt541_lotsgroup_fixed_unpublished_access_date,
    parse_bt198_bt541_lotsgroup_fixed_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_541_lotsgroup_weight import (
    merge_bt198_bt541_lotsgroup_weight,
    parse_bt198_bt541_lotsgroup_weight,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_543_lot import (
    merge_bt198_bt543_lot,
    parse_bt198_bt543_lot,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_543_lotsgroup import (
    merge_bt198_bt543_lotsgroup,
    parse_bt198_bt543_lotsgroup,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_553_tender import (
    merge_bt198_bt553_tender,
    parse_bt198_bt553_tender,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_554_tender import (
    merge_bt198_bt554_unpublished_access_date,
    parse_bt198_bt554_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_555_tender import (
    merge_bt198_bt555_unpublished_access_date,
    parse_bt198_bt555_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_635_lotresult import (
    merge_bt198_bt635_unpublished_access_date,
    parse_bt198_bt635_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_636_lotresult import (
    merge_bt198_bt636_unpublished_access_date,
    parse_bt198_bt636_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_660_lotresult import (
    merge_bt198_bt660_unpublished_access_date,
    parse_bt198_bt660_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_709_lotresult import (
    merge_bt198_bt709_unpublished_access_date,
    parse_bt198_bt709_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_710_lotresult import (
    merge_bt198_bt710_unpublished_access_date,
    parse_bt198_bt710_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_711_lotresult import (
    merge_bt198_bt711_unpublished_access_date,
    parse_bt198_bt711_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_712_lotresult import (
    merge_bt198_bt712_unpublished_access_date,
    parse_bt198_bt712_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_720_tender import (
    merge_bt198_bt720_unpublished_access_date,
    parse_bt198_bt720_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_733_lot import (
    merge_bt198_bt733_unpublished_access_date,
    parse_bt198_bt733_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_733_lotsgroup import (
    merge_bt198_bt733_lotsgroup_unpublished_access_date,
    parse_bt198_bt733_lotsgroup_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_734_lot import (
    merge_bt198_bt734_lot_unpublished_access_date,
    parse_bt198_bt734_lot_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_734_lotsgroup import (
    merge_bt198_bt734_lotsgroup_unpublished_access_date,
    parse_bt198_bt734_lotsgroup_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_759_lotresult import (
    merge_bt198_bt759_lotresult_unpublished_access_date,
    parse_bt198_bt759_lotresult_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_760_lotresult import (
    merge_bt198_bt760_lotresult_unpublished_access_date,
    parse_bt198_bt760_lotresult_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_773_tender import (
    merge_bt198_bt773_tender_unpublished_access_date,
    parse_bt198_bt773_tender_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_1252_procedure import (
    merge_bt198_bt1252_unpublished_access_date,
    parse_bt198_bt1252_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_1351_procedure import (
    merge_bt198_bt1351_unpublished_access_date,
    parse_bt198_bt1351_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_5421_lot import (
    merge_bt198_bt5421_lot,
    parse_bt198_bt5421_lot,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_5421_lotsgroup import (
    merge_bt198_bt5421_lotsgroup,
    parse_bt198_bt5421_lotsgroup,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_5422_lot import (
    merge_bt198_bt5422_lot,
    parse_bt198_bt5422_lot,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_5422_lotsgroup import (
    merge_bt198_bt5422_lotsgroup,
    parse_bt198_bt5422_lotsgroup,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_5423_lot import (
    merge_bt198_bt5423_lot,
    parse_bt198_bt5423_lot,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_5423_lotsgroup import (
    merge_bt198_bt5423_lotsgroup,
    parse_bt198_bt5423_lotsgroup,
)
from ted_and_doffin_to_ocds.converters.bt_200_contract import (
    merge_contract_modification_reason,
    parse_contract_modification_reason,
)
from ted_and_doffin_to_ocds.converters.bt_201_contract import (
    merge_contract_modification_description,
    parse_contract_modification_description,
)
from ted_and_doffin_to_ocds.converters.bt_202_contract import (
    merge_contract_modification_summary,
    parse_contract_modification_summary,
)
from ted_and_doffin_to_ocds.converters.bt_262_lot import (
    merge_main_classification_code_lot,
    parse_main_classification_code_lot,
)
from ted_and_doffin_to_ocds.converters.bt_262_part import (
    merge_main_classification_code_part,
    parse_main_classification_code_part,
)
from ted_and_doffin_to_ocds.converters.bt_262_procedure import (
    merge_main_classification_code_procedure,
    parse_main_classification_code_procedure,
)
from ted_and_doffin_to_ocds.converters.bt_263_lot import (
    merge_additional_classification_code,
    parse_additional_classification_code,
)
from ted_and_doffin_to_ocds.converters.bt_263_part import (
    merge_additional_classification_code_part,
    parse_additional_classification_code_part,
)
from ted_and_doffin_to_ocds.converters.bt_263_procedure import (
    merge_additional_classification_code_procedure,
    parse_additional_classification_code_procedure,
)
from ted_and_doffin_to_ocds.converters.bt_271_lot import (
    merge_bt_271_lot,
    parse_bt_271_lot,
)
from ted_and_doffin_to_ocds.converters.bt_271_lotsgroup import (
    merge_bt_271_lots_group,
    parse_bt_271_lots_group,
)
from ted_and_doffin_to_ocds.converters.bt_271_procedure import (
    merge_bt_271_procedure,
    parse_bt_271_procedure,
)
from ted_and_doffin_to_ocds.converters.bt_300_lot import (
    merge_lot_additional_info,
    parse_lot_additional_info,
)
from ted_and_doffin_to_ocds.converters.bt_300_lotsgroup import (
    merge_lotsgroup_additional_info,
    parse_lotsgroup_additional_info,
)
from ted_and_doffin_to_ocds.converters.bt_300_part import (
    merge_part_additional_info,
    parse_part_additional_info,
)
from ted_and_doffin_to_ocds.converters.bt_300_procedure import (
    merge_procedure_additional_info,
    parse_procedure_additional_info,
)
from ted_and_doffin_to_ocds.converters.bt_330_procedure import (
    merge_group_identifier,
    parse_group_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_500_organization_company import (
    merge_organization_name,
    parse_organization_name,
)
from ted_and_doffin_to_ocds.converters.bt_500_organization_touchpoint import (
    merge_organization_touchpoint_name,
    parse_organization_touchpoint_name,
)
from ted_and_doffin_to_ocds.converters.bt_500_ubo import merge_ubo_name, parse_ubo_name
from ted_and_doffin_to_ocds.converters.bt_501_organization_company import (
    merge_organization_identifier,
    parse_organization_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_502_organization_company import (
    merge_organization_contact_point,
    parse_organization_contact_point,
)
from ted_and_doffin_to_ocds.converters.bt_502_organization_touchpoint import (
    merge_organization_touchpoint_contact_point,
    parse_organization_touchpoint_contact_point,
)
from ted_and_doffin_to_ocds.converters.bt_503_organization_company import (
    merge_organization_telephone,
    parse_organization_telephone,
)
from ted_and_doffin_to_ocds.converters.bt_503_organization_touchpoint import (
    merge_organization_touchpoint_telephone,
    parse_organization_touchpoint_telephone,
)
from ted_and_doffin_to_ocds.converters.bt_503_ubo import (
    merge_ubo_telephone,
    parse_ubo_telephone,
)
from ted_and_doffin_to_ocds.converters.bt_505_organization_company import (
    merge_organization_website,
    parse_organization_website,
)
from ted_and_doffin_to_ocds.converters.bt_505_organization_touchpoint import (
    merge_organization_touchpoint_website,
    parse_organization_touchpoint_website,
)
from ted_and_doffin_to_ocds.converters.bt_506_organization_company import (
    merge_organization_email,
    parse_organization_email,
)
from ted_and_doffin_to_ocds.converters.bt_506_organization_touchpoint import (
    merge_organization_touchpoint_email,
    parse_organization_touchpoint_email,
)
from ted_and_doffin_to_ocds.converters.bt_506_ubo import (
    merge_ubo_email,
    parse_ubo_email,
)
from ted_and_doffin_to_ocds.converters.bt_507_organization_company import (
    merge_organization_country_subdivision,
    parse_organization_country_subdivision,
)
from ted_and_doffin_to_ocds.converters.bt_507_organization_touchpoint import (
    merge_organization_touchpoint_country_subdivision,
    parse_organization_touchpoint_country_subdivision,
)
from ted_and_doffin_to_ocds.converters.bt_507_ubo import (
    merge_ubo_country_subdivision,
    parse_ubo_country_subdivision,
)
from ted_and_doffin_to_ocds.converters.bt_508_procedure_buyer import (
    merge_buyer_profile_url,
    parse_buyer_profile_url,
)
from ted_and_doffin_to_ocds.converters.bt_509_organization_company import (
    merge_organization_edelivery_gateway,
    parse_organization_edelivery_gateway,
)
from ted_and_doffin_to_ocds.converters.bt_509_organization_touchpoint import (
    merge_touchpoint_edelivery_gateway,
    parse_touchpoint_edelivery_gateway,
)
from ted_and_doffin_to_ocds.converters.bt_510a_organization_company import (
    merge_organization_street,
    parse_organization_street,
)
from ted_and_doffin_to_ocds.converters.bt_510a_organization_touchpoint import (
    merge_touchpoint_street,
    parse_touchpoint_street,
)
from ted_and_doffin_to_ocds.converters.bt_510a_ubo import (
    merge_ubo_street,
    parse_ubo_street,
)
from ted_and_doffin_to_ocds.converters.bt_510b_organization_company import (
    merge_organization_streetline1,
    parse_organization_streetline1,
)
from ted_and_doffin_to_ocds.converters.bt_510b_organization_touchpoint import (
    merge_touchpoint_streetline1,
    parse_touchpoint_streetline1,
)
from ted_and_doffin_to_ocds.converters.bt_510b_ubo import (
    merge_ubo_streetline1,
    parse_ubo_streetline1,
)
from ted_and_doffin_to_ocds.converters.bt_510c_organization_company import (
    merge_organization_streetline2,
    parse_organization_streetline2,
)
from ted_and_doffin_to_ocds.converters.bt_510c_organization_touchpoint import (
    merge_touchpoint_streetline2,
    parse_touchpoint_streetline2,
)
from ted_and_doffin_to_ocds.converters.bt_510c_ubo import (
    merge_ubo_streetline2,
    parse_ubo_streetline2,
)
from ted_and_doffin_to_ocds.converters.bt_512_organization_company import (
    merge_organization_postcode,
    parse_organization_postcode,
)
from ted_and_doffin_to_ocds.converters.bt_512_organization_touchpoint import (
    merge_touchpoint_postcode,
    parse_touchpoint_postcode,
)
from ted_and_doffin_to_ocds.converters.bt_512_ubo import (
    merge_ubo_postcode,
    parse_ubo_postcode,
)
from ted_and_doffin_to_ocds.converters.bt_513_organization_company import (
    merge_organization_city,
    parse_organization_city,
)
from ted_and_doffin_to_ocds.converters.bt_513_organization_touchpoint import (
    merge_organization_touchpoint_city,
    parse_organization_touchpoint_city,
)
from ted_and_doffin_to_ocds.converters.bt_513_ubo import merge_ubo_city, parse_ubo_city
from ted_and_doffin_to_ocds.converters.bt_514_organization_company import (
    merge_organization_country,
    parse_organization_country,
)
from ted_and_doffin_to_ocds.converters.bt_514_organization_touchpoint import (
    merge_touchpoint_country,
    parse_touchpoint_country,
)
from ted_and_doffin_to_ocds.converters.bt_514_ubo import (
    merge_ubo_country,
    parse_ubo_country,
)
from ted_and_doffin_to_ocds.converters.bt_531_lot import (
    merge_lot_additional_nature,
    parse_lot_additional_nature,
)
from ted_and_doffin_to_ocds.converters.bt_531_part import (
    merge_part_additional_nature,
    parse_part_additional_nature,
)
from ted_and_doffin_to_ocds.converters.bt_531_procedure import (
    merge_procedure_additional_nature,
    parse_procedure_additional_nature,
)
from ted_and_doffin_to_ocds.converters.bt_536_lot import (
    merge_lot_start_date,
    parse_lot_start_date,
)
from ted_and_doffin_to_ocds.converters.bt_536_part import (
    merge_part_contract_start_date,
    parse_part_contract_start_date,
)
from ted_and_doffin_to_ocds.converters.bt_537_lot import (
    merge_lot_duration_end_date,
    parse_lot_duration_end_date,
)
from ted_and_doffin_to_ocds.converters.bt_537_part import (
    merge_part_duration_end_date,
    parse_part_duration_end_date,
)
from ted_and_doffin_to_ocds.converters.bt_538_lot import (
    merge_lot_duration_other,
    parse_lot_duration_other,
)
from ted_and_doffin_to_ocds.converters.bt_538_part import (
    merge_part_duration_other,
    parse_part_duration_other,
)
from ted_and_doffin_to_ocds.converters.bt_539_lot import (
    merge_award_criterion_type,
    parse_award_criterion_type,
)
from ted_and_doffin_to_ocds.converters.bt_539_lotsgroup import (
    merge_award_criterion_type_lots_group,
    parse_award_criterion_type_lots_group,
)
from ted_and_doffin_to_ocds.converters.bt_540_lot import (
    merge_award_criterion_description,
    parse_award_criterion_description,
)
from ted_and_doffin_to_ocds.converters.bt_540_lotsgroup import (
    merge_award_criterion_description_lots_group,
    parse_award_criterion_description_lots_group,
)
from ted_and_doffin_to_ocds.converters.bt_541_lot_fixednumber import (
    merge_award_criterion_fixed_number,
    parse_award_criterion_fixed_number,
)
from ted_and_doffin_to_ocds.converters.bt_543_lot import (
    merge_award_criteria_complicated,
    parse_award_criteria_complicated,
)
from ted_and_doffin_to_ocds.converters.bt_543_lotsgroup import (
    merge_award_criteria_complicated_lotsgroup,
    parse_award_criteria_complicated_lotsgroup,
)
from ted_and_doffin_to_ocds.converters.bt_553_tender import (
    merge_subcontracting_value,
    parse_subcontracting_value,
)
from ted_and_doffin_to_ocds.converters.bt_554_tender import (
    merge_subcontracting_description,
    parse_subcontracting_description,
)
from ted_and_doffin_to_ocds.converters.bt_555_tender import (
    merge_subcontracting_percentage,
    parse_subcontracting_percentage,
)
from ted_and_doffin_to_ocds.converters.bt_610_procedure_buyer import (
    merge_activity_entity,
    parse_activity_entity,
)
from ted_and_doffin_to_ocds.converters.bt_615_lot import (
    merge_documents_restricted_url,
    parse_documents_restricted_url,
)
from ted_and_doffin_to_ocds.converters.bt_615_part import (
    merge_documents_restricted_url_part,
    parse_documents_restricted_url_part,
)
from ted_and_doffin_to_ocds.converters.bt_625_lot import merge_unit, parse_unit
from ted_and_doffin_to_ocds.converters.bt_630_lot import (
    merge_deadline_receipt_expressions,
    parse_deadline_receipt_expressions,
)
from ted_and_doffin_to_ocds.converters.bt_631_lot import (
    merge_dispatch_invitation_interest,
    parse_dispatch_invitation_interest,
)
from ted_and_doffin_to_ocds.converters.bt_632_lot import (
    merge_tool_name,
    parse_tool_name,
)
from ted_and_doffin_to_ocds.converters.bt_632_part import (
    merge_tool_name_part,
    parse_tool_name_part,
)
from ted_and_doffin_to_ocds.converters.bt_633_organization import (
    merge_organization_natural_person,
    parse_organization_natural_person,
)
from ted_and_doffin_to_ocds.converters.bt_635_lotresult import (
    merge_buyer_review_requests_count,
    parse_buyer_review_requests_count,
)
from ted_and_doffin_to_ocds.converters.bt_636_lotresult import (
    merge_buyer_review_requests_irregularity_type,
    parse_buyer_review_requests_irregularity_type,
)
from ted_and_doffin_to_ocds.converters.bt_644_lot_prize_value import (
    merge_lot_prize_value,
    parse_lot_prize_value,
)
from ted_and_doffin_to_ocds.converters.bt_651_lot_subcontracting_tender_indication import (
    merge_subcontracting_tender_indication,
    parse_subcontracting_tender_indication,
)
from ted_and_doffin_to_ocds.converters.bt_660_lotresult import (
    merge_framework_reestimated_value,
    parse_framework_reestimated_value,
)
from ted_and_doffin_to_ocds.converters.bt_681_lot import (
    merge_foreign_subsidies_regulation,
    parse_foreign_subsidies_regulation,
)
from ted_and_doffin_to_ocds.converters.bt_682_tender import (
    merge_foreign_subsidies_measures,
    parse_foreign_subsidies_measures,
)
from ted_and_doffin_to_ocds.converters.bt_702a_notice import (
    merge_notice_language,
    parse_notice_language,
)
from ted_and_doffin_to_ocds.converters.bt_706_ubo import (
    merge_ubo_nationality,
    parse_ubo_nationality,
)
from ted_and_doffin_to_ocds.converters.bt_707_lot import (
    merge_lot_documents_restricted_justification,
    parse_lot_documents_restricted_justification,
)
from ted_and_doffin_to_ocds.converters.bt_707_part import (
    merge_part_documents_restricted_justification,
    parse_part_documents_restricted_justification,
)
from ted_and_doffin_to_ocds.converters.bt_708_lot import (
    merge_lot_documents_official_language,
    parse_lot_documents_official_language,
)
from ted_and_doffin_to_ocds.converters.bt_708_part import (
    merge_part_documents_official_language,
    parse_part_documents_official_language,
)
from ted_and_doffin_to_ocds.converters.bt_709_lotresult import (
    merge_framework_maximum_value,
    parse_framework_maximum_value,
)
from ted_and_doffin_to_ocds.converters.bt_710_lotresult import (
    merge_tender_value_lowest,
    parse_tender_value_lowest,
)
from ted_and_doffin_to_ocds.converters.bt_711_lotresult import (
    merge_tender_value_highest,
    parse_tender_value_highest,
)
from ted_and_doffin_to_ocds.converters.bt_712a_lotresult import (
    merge_buyer_review_complainants_code,
    parse_buyer_review_complainants_code,
)
from ted_and_doffin_to_ocds.converters.bt_712b_lotresult import (
    merge_buyer_review_complainants_number,
    parse_buyer_review_complainants_number,
)
from ted_and_doffin_to_ocds.converters.bt_717_lot import (
    merge_clean_vehicles_directive,
    parse_clean_vehicles_directive,
)
from ted_and_doffin_to_ocds.converters.bt_719_notice import (
    merge_procurement_documents_change_date,
    parse_procurement_documents_change_date,
)
from ted_and_doffin_to_ocds.converters.bt_720_tender import (
    merge_tender_value,
    parse_tender_value,
)
from ted_and_doffin_to_ocds.converters.bt_721_contract_title import (
    merge_contract_title,
    parse_contract_title,
)
from ted_and_doffin_to_ocds.converters.bt_722_contract import (
    merge_contract_eu_funds,
    parse_contract_eu_funds,
)
from ted_and_doffin_to_ocds.converters.bt_723_lotresult import (
    merge_vehicle_category,
    parse_vehicle_category,
)
from ted_and_doffin_to_ocds.converters.bt_726_lot import (
    merge_lot_sme_suitability,
    parse_lot_sme_suitability,
)
from ted_and_doffin_to_ocds.converters.bt_726_lotsgroup import (
    merge_lots_group_sme_suitability,
    parse_lots_group_sme_suitability,
)
from ted_and_doffin_to_ocds.converters.bt_726_part import (
    merge_part_sme_suitability,
    parse_part_sme_suitability,
)
from ted_and_doffin_to_ocds.converters.bt_727_lot import (
    merge_lot_place_performance,
    parse_lot_place_performance,
)
from ted_and_doffin_to_ocds.converters.bt_727_part import (
    merge_part_place_performance,
    parse_part_place_performance,
)
from ted_and_doffin_to_ocds.converters.bt_727_procedure import (
    merge_procedure_place_performance,
    parse_procedure_place_performance,
)
from ted_and_doffin_to_ocds.converters.bt_728_lot import (
    merge_lot_place_performance_additional,
    parse_lot_place_performance_additional,
)
from ted_and_doffin_to_ocds.converters.bt_728_part import (
    merge_part_place_performance_additional,
    parse_part_place_performance_additional,
)
from ted_and_doffin_to_ocds.converters.bt_728_procedure import (
    merge_procedure_place_performance_additional,
    parse_procedure_place_performance_additional,
)
from ted_and_doffin_to_ocds.converters.bt_729_lot import (
    merge_lot_subcontracting_obligation_maximum,
    parse_lot_subcontracting_obligation_maximum,
)
from ted_and_doffin_to_ocds.converters.bt_732_lot import (
    merge_lot_security_clearance_description,
    parse_lot_security_clearance_description,
)
from ted_and_doffin_to_ocds.converters.bt_733_lot import (
    merge_lot_award_criteria_order_justification,
    parse_lot_award_criteria_order_justification,
)
from ted_and_doffin_to_ocds.converters.bt_733_lotsgroup import (
    merge_lots_group_award_criteria_order_justification,
    parse_lots_group_award_criteria_order_justification,
)
from ted_and_doffin_to_ocds.converters.bt_734_lot import (
    merge_award_criterion_name,
    parse_award_criterion_name,
)
from ted_and_doffin_to_ocds.converters.bt_734_lotsgroup import (
    merge_award_criterion_name_lotsgroup,
    parse_award_criterion_name_lotsgroup,
)
from ted_and_doffin_to_ocds.converters.bt_735_lot import (
    merge_cvd_contract_type,
    parse_cvd_contract_type,
)
from ted_and_doffin_to_ocds.converters.bt_735_lotresult import (
    merge_cvd_contract_type_lotresult,
    parse_cvd_contract_type_lotresult,
)
from ted_and_doffin_to_ocds.converters.bt_736_lot import (
    merge_reserved_execution,
    parse_reserved_execution,
)
from ted_and_doffin_to_ocds.converters.bt_736_part import (
    merge_reserved_execution_part,
    parse_reserved_execution_part,
)
from ted_and_doffin_to_ocds.converters.bt_737_lot import (
    merge_documents_unofficial_language,
    parse_documents_unofficial_language,
)
from ted_and_doffin_to_ocds.converters.bt_737_part import (
    merge_documents_unofficial_language_part,
    parse_documents_unofficial_language_part,
)
from ted_and_doffin_to_ocds.converters.bt_738_notice import (
    merge_notice_preferred_publication_date,
    parse_notice_preferred_publication_date,
)
from ted_and_doffin_to_ocds.converters.bt_739_organization_company import (
    merge_organization_contact_fax,
    parse_organization_contact_fax,
)
from ted_and_doffin_to_ocds.converters.bt_739_organization_touchpoint import (
    merge_touchpoint_contact_fax,
    parse_touchpoint_contact_fax,
)
from ted_and_doffin_to_ocds.converters.bt_739_ubo import merge_ubo_fax, parse_ubo_fax
from ted_and_doffin_to_ocds.converters.bt_740_procedure_buyer import (
    merge_buyer_contracting_entity,
    parse_buyer_contracting_entity,
)
from ted_and_doffin_to_ocds.converters.bt_743_lot import (
    merge_electronic_invoicing,
    parse_electronic_invoicing,
)
from ted_and_doffin_to_ocds.converters.bt_744_lot import (
    merge_submission_electronic_signature,
    parse_submission_electronic_signature,
)
from ted_and_doffin_to_ocds.converters.bt_745_lot import (
    merge_submission_nonelectronic_description,
    parse_submission_nonelectronic_description,
)
from ted_and_doffin_to_ocds.converters.bt_746_organization import (
    merge_winner_listed,
    parse_winner_listed,
)
from ted_and_doffin_to_ocds.converters.bt_750_lot import (
    merge_selection_criteria,
    parse_selection_criteria,
)
from ted_and_doffin_to_ocds.converters.bt_752_lot_thresholdnumber import (
    merge_selection_criteria_threshold_number,
    parse_selection_criteria_threshold_number,
)
from ted_and_doffin_to_ocds.converters.bt_752_lot_weightnumber import (
    merge_selection_criteria_weight_number,
    parse_selection_criteria_weight_number,
)
from ted_and_doffin_to_ocds.converters.bt_754_lot import (
    merge_accessibility_criteria,
    parse_accessibility_criteria,
)
from ted_and_doffin_to_ocds.converters.bt_755_lot import (
    merge_accessibility_justification,
    parse_accessibility_justification,
)
from ted_and_doffin_to_ocds.converters.bt_756_procedure import (
    merge_pin_competition_termination,
    parse_pin_competition_termination,
)
from ted_and_doffin_to_ocds.converters.bt_759_lotresult import (
    merge_received_submissions_count,
    parse_received_submissions_count,
)
from ted_and_doffin_to_ocds.converters.bt_760_lotresult import (
    merge_received_submissions_type,
    parse_received_submissions_type,
)
from ted_and_doffin_to_ocds.converters.bt_762_changereasondescription import (
    merge_change_reason_description,
    parse_change_reason_description,
)
from ted_and_doffin_to_ocds.converters.bt_763_lotsallrequired import (
    merge_lots_all_required,
    parse_lots_all_required,
)
from ted_and_doffin_to_ocds.converters.bt_764_submissionelectroniccatalogue import (
    merge_submission_electronic_catalogue,
    parse_submission_electronic_catalogue,
)
from ted_and_doffin_to_ocds.converters.bt_765_frameworkagreement import (
    merge_framework_agreement,
    parse_framework_agreement,
)
from ted_and_doffin_to_ocds.converters.bt_765_partframeworkagreement import (
    merge_part_framework_agreement,
    parse_part_framework_agreement,
)
from ted_and_doffin_to_ocds.converters.bt_766_dynamicpurchasingsystem import (
    merge_dynamic_purchasing_system,
    parse_dynamic_purchasing_system,
)
from ted_and_doffin_to_ocds.converters.bt_766_partdynamicpurchasingsystem import (
    merge_part_dynamic_purchasing_system,
    parse_part_dynamic_purchasing_system,
)
from ted_and_doffin_to_ocds.converters.bt_767_lot import (
    merge_electronic_auction,
    parse_electronic_auction,
)
from ted_and_doffin_to_ocds.converters.bt_769_lot import (
    merge_multiple_tenders,
    parse_multiple_tenders,
)
from ted_and_doffin_to_ocds.converters.bt_771_lot import (
    merge_late_tenderer_info,
    parse_late_tenderer_info,
)
from ted_and_doffin_to_ocds.converters.bt_772_lot import (
    merge_late_tenderer_info_description,
    parse_late_tenderer_info_description,
)
from ted_and_doffin_to_ocds.converters.bt_773_tender import (
    merge_subcontracting,
    parse_subcontracting,
)
from ted_and_doffin_to_ocds.converters.bt_774_lot import (
    merge_green_procurement,
    parse_green_procurement,
)
from ted_and_doffin_to_ocds.converters.bt_775_lot import (
    merge_social_procurement,
    parse_social_procurement,
)
from ted_and_doffin_to_ocds.converters.bt_776_lot import (
    merge_procurement_innovation,
    parse_procurement_innovation,
)
from ted_and_doffin_to_ocds.converters.bt_777_lot import (
    merge_strategic_procurement_description,
    parse_strategic_procurement_description,
)
from ted_and_doffin_to_ocds.converters.bt_801_lot import (
    merge_non_disclosure_agreement,
    parse_non_disclosure_agreement,
)
from ted_and_doffin_to_ocds.converters.bt_802_lot import (
    merge_non_disclosure_agreement_description,
    parse_non_disclosure_agreement_description,
)
from ted_and_doffin_to_ocds.converters.bt_805_lot import (
    merge_green_procurement_criteria,
    parse_green_procurement_criteria,
)
from ted_and_doffin_to_ocds.converters.bt_806_procedure import (
    merge_exclusion_grounds_sources,
    parse_exclusion_grounds_sources,
)
from ted_and_doffin_to_ocds.converters.bt_809_lot import (
    merge_selection_criteria_809,
    parse_selection_criteria_809,
)
from ted_and_doffin_to_ocds.converters.bt_821_lot import (
    merge_selection_criteria_source,
    parse_selection_criteria_source,
)
from ted_and_doffin_to_ocds.converters.bt_1252_procedure import (
    merge_direct_award_justification,
    parse_direct_award_justification,
)
from ted_and_doffin_to_ocds.converters.bt_1311_lot import (
    merge_deadline_receipt_requests,
    parse_deadline_receipt_requests,
)
from ted_and_doffin_to_ocds.converters.bt_1351_procedure import (
    merge_accelerated_procedure_justification,
    parse_accelerated_procedure_justification,
)
from ted_and_doffin_to_ocds.converters.bt_1375_procedure import (
    merge_group_lot_identifier,
    parse_group_lot_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_1451_contract import (
    merge_winner_decision_date,
    parse_winner_decision_date,
)
from ted_and_doffin_to_ocds.converters.bt_1711_tender import (
    merge_tender_ranked,
    parse_tender_ranked,
)
from ted_and_doffin_to_ocds.converters.bt_3201_tender import (
    merge_tender_identifier,
    parse_tender_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_3202_contract import (
    merge_contract_tender_id,
    parse_contract_tender_id,
)
from ted_and_doffin_to_ocds.converters.bt_5010_lot import (
    merge_eu_funds_financing_identifier,
    parse_eu_funds_financing_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_5011_contract import (
    merge_contract_eu_funds_financing_identifier,
    parse_contract_eu_funds_financing_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_5071_lot import (
    merge_place_performance_country_subdivision,
    parse_place_performance_country_subdivision,
)
from ted_and_doffin_to_ocds.converters.bt_5071_part import (
    merge_place_performance_country_subdivision_part,
    parse_place_performance_country_subdivision_part,
)
from ted_and_doffin_to_ocds.converters.bt_5071_procedure import (
    merge_place_performance_country_subdivision_procedure,
    parse_place_performance_country_subdivision_procedure,
)
from ted_and_doffin_to_ocds.converters.bt_5101_lot import (
    merge_place_performance_street_lot,
    parse_place_performance_street_lot,
)
from ted_and_doffin_to_ocds.converters.bt_5101a_part import (
    merge_part_place_performance_street,
    parse_part_place_performance_street,
)
from ted_and_doffin_to_ocds.converters.bt_5101a_procedure import (
    merge_procedure_place_performance_street,
    parse_procedure_place_performance_street,
)
from ted_and_doffin_to_ocds.converters.bt_5101b_part import (
    merge_part_place_performance_streetline1,
    parse_part_place_performance_streetline1,
)
from ted_and_doffin_to_ocds.converters.bt_5101b_procedure import (
    merge_procedure_place_performance_streetline1,
    parse_procedure_place_performance_streetline1,
)
from ted_and_doffin_to_ocds.converters.bt_5101c_part import (
    merge_part_place_performance_streetline2,
    parse_part_place_performance_streetline2,
)
from ted_and_doffin_to_ocds.converters.bt_5101c_procedure import (
    merge_procedure_place_performance_streetline2,
    parse_procedure_place_performance_streetline2,
)
from ted_and_doffin_to_ocds.converters.bt_5121_lot import (
    merge_place_performance_post_code,
    parse_place_performance_post_code,
)
from ted_and_doffin_to_ocds.converters.bt_5121_part import (
    merge_place_performance_post_code_part,
    parse_place_performance_post_code_part,
)
from ted_and_doffin_to_ocds.converters.bt_5121_procedure import (
    merge_place_performance_post_code_procedure,
    parse_place_performance_post_code_procedure,
)
from ted_and_doffin_to_ocds.converters.bt_5131_lot import (
    merge_place_performance_city,
    parse_place_performance_city,
)
from ted_and_doffin_to_ocds.converters.bt_5131_part import (
    merge_place_performance_city_part,
    parse_place_performance_city_part,
)
from ted_and_doffin_to_ocds.converters.bt_5131_procedure import (
    merge_place_performance_city_procedure,
    parse_place_performance_city_procedure,
)
from ted_and_doffin_to_ocds.converters.bt_5141_lot import (
    merge_lot_country,
    parse_lot_country,
)
from ted_and_doffin_to_ocds.converters.bt_5141_part import (
    merge_part_country,
    parse_part_country,
)
from ted_and_doffin_to_ocds.converters.bt_5141_procedure import (
    merge_procedure_country,
    parse_procedure_country,
)
from ted_and_doffin_to_ocds.converters.bt_5421_lot import (
    merge_award_criterion_number_weight_lot,
    parse_award_criterion_number_weight_lot,
)
from ted_and_doffin_to_ocds.converters.bt_5421_lotsgroup import (
    merge_award_criterion_number_weight_lots_group,
    parse_award_criterion_number_weight_lots_group,
)
from ted_and_doffin_to_ocds.converters.bt_5422_lot import (
    merge_award_criterion_number_fixed,
    parse_award_criterion_number_fixed,
)
from ted_and_doffin_to_ocds.converters.bt_5422_lotsgroup import (
    merge_award_criterion_number_fixed_lotsgroup,
    parse_award_criterion_number_fixed_lotsgroup,
)
from ted_and_doffin_to_ocds.converters.bt_5423_lot import (
    merge_award_criterion_number_threshold,
    parse_award_criterion_number_threshold,
)
from ted_and_doffin_to_ocds.converters.bt_5423_lotsgroup import (
    merge_award_criterion_number_threshold_lotsgroup,
    parse_award_criterion_number_threshold_lotsgroup,
)
from ted_and_doffin_to_ocds.converters.bt_6110_contract import (
    merge_contract_eu_funds_details,
    parse_contract_eu_funds_details,
)
from ted_and_doffin_to_ocds.converters.bt_6140_lot import (
    merge_lot_eu_funds_details,
    parse_lot_eu_funds_details,
)
from ted_and_doffin_to_ocds.converters.bt_7220_lot import (
    merge_lot_eu_funds,
    parse_lot_eu_funds,
)
from ted_and_doffin_to_ocds.converters.bt_7531_lot import (
    merge_selection_criteria_number_weight,
    parse_selection_criteria_number_weight,
)
from ted_and_doffin_to_ocds.converters.bt_7532_lot import (
    merge_selection_criteria_number_threshold,
    parse_selection_criteria_number_threshold,
)
from ted_and_doffin_to_ocds.converters.bt_13713_lotresult import (
    merge_lot_result_identifier,
    parse_lot_result_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_13714_tender import (
    merge_tender_lot_identifier,
    parse_tender_lot_identifier,
)
from ted_and_doffin_to_ocds.converters.opp_020_contract import (
    map_extended_duration_indicator,
    merge_extended_duration_indicator,
)
from ted_and_doffin_to_ocds.converters.opp_021_contract import (
    map_essential_assets,
    merge_essential_assets,
)
from ted_and_doffin_to_ocds.converters.opp_022_contract import (
    map_asset_significance,
    merge_asset_significance,
)
from ted_and_doffin_to_ocds.converters.opp_023_contract import (
    map_asset_predominance,
    merge_asset_predominance,
)
from ted_and_doffin_to_ocds.converters.opp_031_tender import (
    merge_contract_conditions,
    parse_contract_conditions,
)
from ted_and_doffin_to_ocds.converters.opp_032_tender import (
    merge_revenues_allocation,
    parse_revenues_allocation,
)
from ted_and_doffin_to_ocds.converters.opp_034_tender import (
    merge_penalties_and_rewards,
    parse_penalties_and_rewards,
)
from ted_and_doffin_to_ocds.converters.opp_040_procedure import (
    merge_main_nature_sub_type,
    parse_main_nature_sub_type,
)
from ted_and_doffin_to_ocds.converters.opp_050_organization import (
    merge_buyers_group_lead_indicator,
    parse_buyers_group_lead_indicator,
)
from ted_and_doffin_to_ocds.converters.opp_051_organization import (
    merge_awarding_cpb_buyer_indicator,
    parse_awarding_cpb_buyer_indicator,
)
from ted_and_doffin_to_ocds.converters.opp_052_organization import (
    merge_acquiring_cpb_buyer_indicator,
    parse_acquiring_cpb_buyer_indicator,
)
from ted_and_doffin_to_ocds.converters.opp_080_tender import (
    merge_kilometers_public_transport,
    parse_kilometers_public_transport,
)
from ted_and_doffin_to_ocds.converters.opp_090_procedure import (
    merge_previous_notice_identifier,
    parse_previous_notice_identifier,
)
from ted_and_doffin_to_ocds.converters.opt_030_procedure_sprovider import (
    merge_provided_service_type,
    parse_provided_service_type,
)
from ted_and_doffin_to_ocds.converters.opt_071_lot import (
    merge_quality_target_code,
    parse_quality_target_code,
)
from ted_and_doffin_to_ocds.converters.opt_072_lot import (
    merge_quality_target_description,
    parse_quality_target_description,
)
from ted_and_doffin_to_ocds.converters.opt_100_contract import (
    merge_framework_notice_identifier,
    parse_framework_notice_identifier,
)
from ted_and_doffin_to_ocds.converters.opt_110_lot_fiscallegis import (
    merge_fiscal_legislation_url,
    parse_fiscal_legislation_url,
)
from ted_and_doffin_to_ocds.converters.opt_110_part_fiscallegis import (
    merge_part_fiscal_legislation_url,
    parse_part_fiscal_legislation_url,
)
from ted_and_doffin_to_ocds.converters.opt_111_lot_fiscallegis import (
    merge_fiscal_legislation_document_id,
    parse_fiscal_legislation_document_id,
)
from ted_and_doffin_to_ocds.converters.opt_111_part_fiscallegis import (
    merge_part_fiscal_legislation_document_id,
    parse_part_fiscal_legislation_document_id,
)
from ted_and_doffin_to_ocds.converters.opt_112_lot_environlegis import (
    merge_environmental_legislation_document_id,
    parse_environmental_legislation_document_id,
)
from ted_and_doffin_to_ocds.converters.opt_112_part_environlegis import (
    merge_part_environmental_legislation_document_id,
    parse_part_environmental_legislation_document_id,
)
from ted_and_doffin_to_ocds.converters.opt_113_lot_employlegis import (
    merge_employment_legislation_document_id,
    parse_employment_legislation_document_id,
)
from ted_and_doffin_to_ocds.converters.opt_113_part_employlegis import (
    merge_part_employment_legislation_document_id,
    parse_part_employment_legislation_document_id,
)
from ted_and_doffin_to_ocds.converters.opt_120_lot_environlegis import (
    merge_environmental_legislation_url,
    parse_environmental_legislation_url,
)
from ted_and_doffin_to_ocds.converters.opt_120_part_environlegis import (
    merge_environmental_legislation_url_part,
    parse_environmental_legislation_url_part,
)
from ted_and_doffin_to_ocds.converters.opt_130_lot_employlegis import (
    merge_employment_legislation_url,
    parse_employment_legislation_url,
)
from ted_and_doffin_to_ocds.converters.opt_130_part_employlegis import (
    merge_employment_legislation_url_part,
    parse_employment_legislation_url_part,
)
from ted_and_doffin_to_ocds.converters.opt_140_lot_procurement_docs import (
    merge_procurement_documents_id,
    parse_procurement_documents_id,
)
from ted_and_doffin_to_ocds.converters.opt_140_part_procurement_docs import (
    merge_procurement_documents_id_part,
    parse_procurement_documents_id_part,
)
from ted_and_doffin_to_ocds.converters.opt_155_lotresult import (
    merge_vehicle_type,
    parse_vehicle_type,
)
from ted_and_doffin_to_ocds.converters.opt_156_lotresult import (
    merge_vehicle_numeric,
    parse_vehicle_numeric,
)
from ted_and_doffin_to_ocds.converters.opt_160_ubo_firstname import (
    merge_ubo_firstname,
    parse_ubo_firstname,
)
from ted_and_doffin_to_ocds.converters.opt_170_tenderer_leader import (
    merge_tendering_party_leader,
    parse_tendering_party_leader,
)
from ted_and_doffin_to_ocds.converters.opt_200_organization_company import (
    merge_organization_technical_identifier,
    parse_organization_technical_identifier,
)
from ted_and_doffin_to_ocds.converters.opt_201_organization_touchpoint import (
    merge_touchpoint_technical_identifier,
    parse_touchpoint_technical_identifier,
)
from ted_and_doffin_to_ocds.converters.opt_202_ubo import (
    merge_beneficial_owner_identifier,
    parse_beneficial_owner_identifier,
)
from ted_and_doffin_to_ocds.converters.opt_300_contract_signatory import (
    merge_signatory_identifier_reference,
    parse_signatory_identifier_reference,
)
from ted_and_doffin_to_ocds.converters.opt_300_procedure_buyer import (
    merge_buyer_technical_identifier,
    parse_buyer_technical_identifier,
)
from ted_and_doffin_to_ocds.converters.opt_300_procedure_sprovider import (
    merge_service_provider_identifier,
    parse_service_provider_identifier,
)
from ted_and_doffin_to_ocds.converters.opt_301_lot_addinfo import (
    merge_additional_info_provider,
    parse_additional_info_provider,
)
from ted_and_doffin_to_ocds.converters.opt_301_lot_docprovider import (
    merge_document_provider,
    parse_document_provider,
)
from ted_and_doffin_to_ocds.converters.opt_301_lot_employlegis import (
    merge_employment_legislation_org,
    parse_employment_legislation_org,
)
from ted_and_doffin_to_ocds.converters.opt_301_lot_environlegis import (
    merge_environmental_legislation_org,
    parse_environmental_legislation_org,
)
from ted_and_doffin_to_ocds.converters.opt_301_lot_fiscallegis import (
    merge_fiscal_legislation_org,
    parse_fiscal_legislation_org,
)
from ted_and_doffin_to_ocds.converters.opt_301_lot_mediator import (
    merge_mediator_technical_identifier,
    parse_mediator_technical_identifier,
)
from ted_and_doffin_to_ocds.converters.opt_301_lot_reviewinfo import (
    merge_review_info_provider_identifier,
    parse_review_info_provider_identifier,
)
from ted_and_doffin_to_ocds.converters.opt_301_lot_revieworg import (
    merge_review_organization_identifier,
    parse_review_organization_identifier,
)
from ted_and_doffin_to_ocds.converters.opt_301_lot_tendereval import (
    merge_tender_evaluator,
    parse_tender_evaluator,
)
from ted_and_doffin_to_ocds.converters.opt_301_lot_tenderreceipt import (
    merge_tender_recipient,
    parse_tender_recipient,
)
from ted_and_doffin_to_ocds.converters.opt_301_lotresult_financing import (
    merge_financing_party,
    parse_financing_party,
)
from ted_and_doffin_to_ocds.converters.opt_301_lotresult_paying import (
    merge_payer_party,
    parse_payer_party,
)
from ted_and_doffin_to_ocds.converters.opt_301_part_addinfo import (
    part_merge_additional_info_provider,
    part_parse_additional_info_provider,
)
from ted_and_doffin_to_ocds.converters.opt_301_part_docprovider import (
    part_merge_document_provider,
    part_parse_document_provider,
)
from ted_and_doffin_to_ocds.converters.opt_301_part_employlegis import (
    part_merge_employment_legislation_org_reference,
    part_parse_employment_legislation_org_reference,
)
from ted_and_doffin_to_ocds.converters.opt_301_part_environlegis import (
    merge_environmental_legislation_org_reference,
    parse_environmental_legislation_org_reference,
)
from ted_and_doffin_to_ocds.converters.opt_301_part_fiscallegis import (
    merge_fiscal_legislation_org_reference,
    parse_fiscal_legislation_org_reference,
)
from ted_and_doffin_to_ocds.converters.opt_301_part_mediator import (
    part_merge_mediator,
    part_parse_mediator,
)
from ted_and_doffin_to_ocds.converters.opt_301_part_reviewinfo import (
    part_merge_review_info_provider,
    part_parse_review_info_provider,
)
from ted_and_doffin_to_ocds.converters.opt_301_part_revieworg import (
    part_merge_review_organization,
    part_parse_review_organization,
)
from ted_and_doffin_to_ocds.converters.opt_301_part_tendereval import (
    part_merge_tender_evaluator,
    part_parse_tender_evaluator,
)
from ted_and_doffin_to_ocds.converters.opt_301_part_tenderreceipt import (
    part_merge_tender_recipient,
    part_parse_tender_recipient,
)
from ted_and_doffin_to_ocds.converters.opt_301_tenderer_maincont import (
    merge_main_contractor,
    parse_main_contractor,
)
from ted_and_doffin_to_ocds.converters.opt_301_tenderer_subcont import (
    merge_subcontractor,
    parse_subcontractor,
)
from ted_and_doffin_to_ocds.converters.opt_302_organization import (
    merge_beneficial_owner_reference,
    parse_beneficial_owner_reference,
)
from ted_and_doffin_to_ocds.converters.opt_310_tender import (
    merge_tendering_party_id_reference,
    parse_tendering_party_id_reference,
)
from ted_and_doffin_to_ocds.converters.opt_315_lotresult import (
    merge_contract_identifier_reference,
    parse_contract_identifier_reference,
)
from ted_and_doffin_to_ocds.converters.opt_316_contract import (
    merge_contract_technical_identifier,
    parse_contract_technical_identifier,
)
from ted_and_doffin_to_ocds.converters.opt_320_lotresult import (
    merge_tender_identifier_reference,
    parse_tender_identifier_reference,
)
from ted_and_doffin_to_ocds.converters.opt_321_tender import (
    merge_tender_technical_identifier,
    parse_tender_technical_identifier,
)
from ted_and_doffin_to_ocds.converters.opt_322_lotresult import (
    merge_lotresult_technical_identifier,
    parse_lotresult_technical_identifier,
)


def process_bt_section(
    release_json: dict[str, Any],
    xml_content: bytes,
    parse_funcs: Sequence[Callable],
    merge_func: Callable,
    section_name: str,
) -> None:
    """Process a single business term section."""
    logger = logging.getLogger(__name__)

    try:
        logger.info("Starting %s processing", section_name)
        for parse_function in parse_funcs:
            parsed_data = parse_function(xml_content)
            if parsed_data:
                merge_func(release_json, parsed_data)
                logger.info("Successfully merged data for %s", section_name)
                return
        logger.warning("No data found for %s", section_name)
    except Exception:
        logger.exception("Error processing %s data", section_name)


def process_bt_sections(release_json: dict[str, Any], xml_content: bytes) -> None:
    """Process all business term sections."""
    bt_sections = [
        (
            parse_procedure_legal_basis,
            merge_procedure_legal_basis,
            "procedure Legal Basis (BT-01)",
        ),
        (parse_form_type, merge_form_type, "Form Type (BT-03)"),
        (
            parse_procedure_identifier,
            merge_procedure_identifier,
            "procedure Identifier (BT-04)",
        ),
        (
            parse_notice_dispatch_date_time,
            merge_notice_dispatch_date_time,
            "notice Dispatch Date and Time (BT-05)",
        ),
        (
            parse_strategic_procurement,
            merge_strategic_procurement,
            "Strategic Procurement (BT-06)",
        ),
        (
            parse_cross_border_law,
            merge_cross_border_law,
            "Cross Border Law (BT-09)",
        ),
        (
            parse_authority_activity,
            merge_authority_activity,
            "organization Main Activity (BT-10)",
        ),
        (parse_procedure_type, merge_procedure_type, "procedure Type (BT-105)"),
        (
            parse_procedure_accelerated,
            merge_procedure_accelerated,
            "procedure Accelerated (BT-106)",
        ),
        (
            parse_framework_duration_justification,
            merge_framework_duration_justification,
            "Framework Duration Justification (BT-109)",
        ),
        (
            parse_buyer_legal_type,
            merge_buyer_legal_type,
            "buyer Legal Type (BT-11)",
        ),
        (
            parse_framework_buyer_categories,
            merge_framework_buyer_categories,
            "Framework buyer Categories (BT-111)",
        ),
        (
            parse_framework_max_participants,
            merge_framework_max_participants,
            "Framework Maximum participants Number (BT-113)",
        ),
        (parse_gpa_coverage, merge_gpa_coverage, "GPA Coverage (BT-115)"),
        (parse_dps_termination, merge_dps_termination, "DPS Termination (BT-119)"),
        (
            parse_no_negotiation_necessary,
            merge_no_negotiation_necessary,
            "No Negotiation Necessary (BT-120)",
        ),
        (
            parse_electronic_auction_description,
            merge_electronic_auction_description,
            "Electronic Auction Description (BT-122)",
        ),
        (
            parse_electronic_auction_url,
            merge_electronic_auction_url,
            "Electronic Auction URL (BT-123)",
        ),
        (
            parse_tool_atypical_url,
            merge_tool_atypical_url,
            "Tool Atypical URL (BT-124)",
        ),
        (
            parse_previous_planning_identifier_lot,
            merge_previous_planning_identifier_lot,
            "Previous Planning Identifier (Lot) (BT-125(i))",
        ),
        (
            parse_previous_planning_identifier_part,
            merge_previous_planning_identifier_part,
            "Previous Planning Identifier (part) (BT-125(i) and BT-1251)",
        ),
        (
            parse_direct_award_justification,
            merge_direct_award_justification,
            "Direct Award Justification (BT-1252)",
        ),
        (
            parse_future_notice_date,
            merge_future_notice_date,
            "Future notice Date (BT-127)",
        ),
        (
            parse_additional_info_deadline,
            merge_additional_info_deadline,
            "Additional Information Deadline (BT-13)",
        ),
        (
            parse_additional_info_deadline_part,
            merge_additional_info_deadline_part,
            "Additional Information Deadline (part) (BT-13)",
        ),
        (
            parse_dispatch_invitation_tender,
            merge_dispatch_invitation_tender,
            "Dispatch Invitation Tender (BT-130)",
        ),
        (
            parse_deadline_receipt_tenders,
            merge_deadline_receipt_tenders,
            "Deadline Receipt Tenders (BT-131)",
        ),
        (
            parse_deadline_receipt_requests,
            merge_deadline_receipt_requests,
            "Deadline Receipt Requests (BT-1311)",
        ),
        (
            parse_lot_public_opening_date,
            merge_lot_public_opening_date,
            "Lot Public Opening Date (BT-132)",
        ),
        (
            parse_lot_bid_opening_location,
            merge_lot_bid_opening_location,
            "Lot Bid Opening Location (BT-133)",
        ),
        (
            parse_lot_public_opening_description,
            merge_lot_public_opening_description,
            "Lot Public Opening Description (BT-134)",
        ),
        (
            parse_direct_award_justification_rationale,
            merge_direct_award_justification_rationale,
            "Direct Award Justification Rationale (BT-135)",
        ),
        (
            parse_accelerated_procedure_justification,
            merge_accelerated_procedure_justification,
            "Accelerated procedure Justification (BT-1351)",
        ),
        (
            parse_direct_award_justification_code,
            merge_direct_award_justification_code,
            "Direct Award Justification Code (BT-136)",
        ),
        (
            parse_purpose_lot_identifier,
            merge_purpose_lot_identifier,
            "Purpose Lot Identifier (BT-137-Lot)",
        ),
        (
            parse_lots_group_identifier,
            merge_lots_group_identifier,
            "Lots Group Identifier (BT-137-LotsGroup)",
        ),
        (
            parse_part_identifier,
            merge_part_identifier,
            "part Identifier (BT-137-part)",
        ),
        (
            parse_lot_result_identifier,
            merge_lot_result_identifier,
            "Lot Result Identifier (BT-13713)",
        ),
        (
            parse_tender_lot_identifier,
            merge_tender_lot_identifier,
            "Tender Lot Identifier (BT-13714)",
        ),
        (
            parse_group_lot_identifier,
            merge_group_lot_identifier,
            "Group Lot Identifier (BT-1375)",
        ),
        (
            parse_lot_documents_restricted,
            merge_lot_documents_restricted,
            "Lot Documents Restricted (BT-14-Lot)",
        ),
        (
            parse_part_documents_restricted,
            merge_part_documents_restricted,
            "part Documents Restricted (BT-14-part)",
        ),
        (
            parse_change_reason_code,
            merge_change_reason_code,
            "Change Reason Code (BT-140)",
        ),
        (parse_winner_chosen, merge_winner_chosen, "Winner Chosen (BT-142)"),
        (
            parse_not_awarded_reason,
            merge_not_awarded_reason,
            "Not Awarded Reason (BT-144)",
        ),
        (
            parse_contract_conclusion_date,
            merge_contract_conclusion_date,
            "Contract Conclusion Date (BT-145)",
        ),
        (
            parse_winner_decision_date,
            merge_winner_decision_date,
            "Winner Decision Date (BT-1451)",
        ),
        (parse_documents_url, merge_documents_url, "Documents URL (BT-15)"),
        (
            parse_contract_identifier,
            merge_contract_identifier,
            "Contract Identifier (BT-150)",
        ),
        (parse_contract_url, merge_contract_url, "Contract URL (BT-151)"),
        (
            parse_organization_name,
            merge_organization_name,
            "organization Name (BT-500)",
        ),
        (
            parse_organization_part_name,
            merge_organization_part_name,
            "organization part Name (BT-16-organization-company)",
        ),
        (
            parse_organization_touchpoint_part_name,
            merge_organization_touchpoint_part_name,
            "organization touchpoint part Name (BT-16-organization-touchpoint)",
        ),
        (
            parse_organization_touchpoint_name,
            merge_organization_touchpoint_name,
            "touchpoint Name (BT-500-organization-touchpoint)",
        ),
        (
            parse_concession_revenue_buyer,
            merge_concession_revenue_buyer,
            "Concession Revenue buyer (BT-160)",
        ),
        (
            parse_concession_revenue_user,
            merge_concession_revenue_user,
            "Concession Revenue User (BT-162)",
        ),
        (
            parse_concession_value_description,
            merge_concession_value_description,
            "Concession Value Description (BT-163)",
        ),
        (parse_winner_size, merge_winner_size, "Winner Size (BT-165)"),
        (
            parse_submission_electronic,
            merge_submission_electronic,
            "Submission Electronic (BT-17)",
        ),
        (parse_tender_rank, merge_tender_rank, "Tender Rank (BT-171)"),
        (parse_tender_ranked, merge_tender_ranked, "Tender Ranked (BT-1711)"),
        (parse_submission_url, merge_submission_url, "Submission URL (BT-18)"),
        (
            parse_submission_nonelectronic_justification,
            merge_submission_nonelectronic_justification,
            "Submission Nonelectronic Justification (BT-19)",
        ),
        (parse_country_origin, merge_country_origin, "Country Origin (BT-191)"),
        (parse_tender_variant, merge_tender_variant, "Tender Variant (BT-193)"),
        (
            bt_195_parse_unpublished_identifier_bt_09_procedure,
            bt_195_merge_unpublished_identifier_bt_09_procedure,
            "Unpublished Identifier (BT-195, BT-09)",
        ),
        (
            parse_bt195_bt105_unpublished_identifier,
            merge_bt195_bt105_unpublished_identifier,
            "Unpublished Identifier (BT-195, BT-105)",
        ),
        (
            parse_bt195_bt106_unpublished_identifier,
            merge_bt195_bt106_unpublished_identifier,
            "Unpublished Identifier (BT-195, BT-106)",
        ),
        (
            parse_bt195_bt1252_unpublished_identifier,
            merge_bt195_bt1252_unpublished_identifier,
            "Unpublished Identifier (BT-195, BT-1252)",
        ),
        (
            parse_bt195_bt135_unpublished_identifier,
            merge_bt195_bt135_unpublished_identifier,
            "Unpublished Identifier (BT-195, BT-135)",
        ),
        (
            parse_bt195_bt1351_unpublished_identifier,
            merge_bt195_bt1351_unpublished_identifier,
            "Unpublished Identifier (BT-195, BT-1351)",
        ),
        (
            parse_bt195_bt136_unpublished_identifier,
            merge_bt195_bt136_unpublished_identifier,
            "Unpublished Identifier (BT-195, BT-136)",
        ),
        (
            parse_bt195_bt142_unpublished_identifier,
            merge_bt195_bt142_unpublished_identifier,
            "Unpublished Identifier (BT-195, BT-142)",
        ),
        (
            parse_bt195_bt144_unpublished_identifier,
            merge_bt195_bt144_unpublished_identifier,
            "Unpublished Identifier (BT-195, BT-144)",
        ),
        (
            parse_bt195_bt160_unpublished_identifier,
            merge_bt195_bt160_unpublished_identifier,
            "procedure BT-195(BT-160)-Tender Unpublished Identifier",
        ),
        (
            parse_bt195_bt162_unpublished_identifier,
            merge_bt195_bt162_unpublished_identifier,
            "procedure BT-195(BT-162)-Tender Unpublished Identifier",
        ),
        (
            parse_bt195_bt163_unpublished_identifier,
            merge_bt195_bt163_unpublished_identifier,
            "procedure BT-195(BT-163)-Tender Unpublished Identifier",
        ),
        (
            parse_bt195_bt171_unpublished_identifier,
            merge_bt195_bt171_unpublished_identifier,
            "procedure BT-195(BT-171)-Tender Unpublished Identifier",
        ),
        (
            parse_bt195_bt191_unpublished_identifier,
            merge_bt195_bt191_unpublished_identifier,
            "procedure BT-195(BT-191)-Tender Unpublished Identifier",
        ),
        (
            parse_bt195_bt193_unpublished_identifier,
            merge_bt195_bt193_unpublished_identifier,
            "procedure BT-195(BT-193)-Tender Unpublished Identifier",
        ),
        (
            parse_bt195_bt539_unpublished_identifier,
            merge_bt195_bt539_unpublished_identifier,
            "procedure BT-195(BT-539)-Lot Unpublished Identifier",
        ),
        (
            parse_bt195_bt539_lotsgroup_unpublished_identifier,
            merge_bt195_bt539_lotsgroup_unpublished_identifier,
            "procedure BT-195(BT-539)-LotsGroup Unpublished Identifier",
        ),
        (
            parse_bt195_bt540_lot_unpublished_identifier,
            merge_bt195_bt540_lot_unpublished_identifier,
            "procedure BT-195(BT-540)-Lot Unpublished Identifier",
        ),
        (
            parse_bt195_bt540_lotsgroup_unpublished_identifier,
            merge_bt195_bt540_lotsgroup_unpublished_identifier,
            "procedure BT-195(BT-540)-LotsGroup Unpublished Identifier",
        ),
        (
            parse_bt195_bt541_lot_fixed_unpublished_identifier,
            merge_bt195_bt541_lot_fixed_unpublished_identifier,
            "procedure BT-195(BT-541)-Lot-Fixed Unpublished Identifier",
        ),
        (
            parse_bt195_bt541_lot_threshold_unpublished_identifier,
            merge_bt195_bt541_lot_threshold_unpublished_identifier,
            "Lot Threshold Unpublished Identifier (BT-195(BT-541))",
        ),
        (
            parse_bt195_bt541_lot_weight_unpublished_identifier,
            merge_bt195_bt541_lot_weight_unpublished_identifier,
            "Lot Weight Unpublished Identifier (BT-195(BT-541))",
        ),
        (
            parse_bt195_bt541_lotsgroup_fixed_unpublished_identifier,
            merge_bt195_bt541_lotsgroup_fixed_unpublished_identifier,
            "LotsGroup Fixed Unpublished Identifier (BT-195(BT-541))",
        ),
        (
            parse_bt195_bt541_lotsgroup_threshold_unpublished_identifier,
            merge_bt195_bt541_lotsgroup_threshold_unpublished_identifier,
            "LotsGroup Threshold Unpublished Identifier (BT-195(BT-541))",
        ),
        (
            parse_bt195_bt541_lotsgroup_weight,
            merge_bt195_bt541_lotsgroup_weight,
            "Unpublished Identifier for LotsGroup Weight (BT-195(BT-541))",
        ),
        (
            parse_bt195_bt5421_lot,
            merge_bt195_bt5421_lot,
            "Unpublished Identifier for Lot (BT-195(BT-5421))",
        ),
        (
            parse_bt195_bt5421_lotsgroup,
            merge_bt195_bt5421_lotsgroup,
            "Unpublished Identifier for LotsGroup (BT-195(BT-5421))",
        ),
        (
            parse_bt195_bt5422_lot,
            merge_bt195_bt5422_lot,
            "Unpublished Identifier for Lot (BT-195(BT-5422))",
        ),
        (
            parse_bt195_bt5422_lotsgroup,
            merge_bt195_bt5422_lotsgroup,
            "Unpublished Identifier for LotsGroup (BT-195(BT-5422))",
        ),
        (
            parse_bt195_bt5423_lot,
            merge_bt195_bt5423_lot,
            "Unpublished Identifier for Lot (BT-195(BT-5423))",
        ),
        (
            parse_bt195_bt5423_lotsgroup,
            merge_bt195_bt5423_lotsgroup,
            "Unpublished Identifier for LotsGroup (BT-195(BT-5423))",
        ),
        (
            parse_bt195_bt543_lot,
            merge_bt195_bt543_lot,
            "Unpublished Identifier for Lot (BT-195(BT-543))",
        ),
        (
            parse_bt195_bt543_lotsgroup,
            merge_bt195_bt543_lotsgroup,
            "Unpublished Identifier for LotsGroup (BT-195(BT-543))",
        ),
        (
            parse_bt195_bt553_tender,
            merge_bt195_bt553_tender,
            "Unpublished Identifier for Tender (BT-195(BT-553))",
        ),
        (
            parse_bt195_bt554_unpublished_identifier,
            merge_bt195_bt554_unpublished_identifier,
            "Unpublished Identifier for Tender Subcontracting Description (BT-195(BT-554))",
        ),
        (
            parse_bt195_bt555_unpublished_identifier,
            merge_bt195_bt555_unpublished_identifier,
            "Unpublished Identifier for Tender Subcontracting Percentage (BT-195(BT-555))",
        ),
        (
            parse_bt195_bt635_unpublished_identifier,
            merge_bt195_bt635_unpublished_identifier,
            "Unpublished Identifier for Lot Result buyer Review Request Count (BT-195(BT-635))",
        ),
        (
            parse_bt195_bt636_unpublished_identifier,
            merge_bt195_bt636_unpublished_identifier,
            "Unpublished Identifier for Lot Result buyer Review Request Irregularity Type (BT-195(BT-636))",
        ),
        (
            parse_bt195_bt660_unpublished_identifier,
            merge_bt195_bt660_unpublished_identifier,
            "Unpublished Identifier for Lot Result Framework Re-estimated Value (BT-195(BT-660))",
        ),
        (
            parse_bt195_bt709_unpublished_identifier,
            merge_bt195_bt709_unpublished_identifier,
            "Unpublished Identifier for Lot Result Maximum Value (BT-195(BT-709))",
        ),
        (
            parse_bt195_bt710_unpublished_identifier,
            merge_bt195_bt710_unpublished_identifier,
            "Unpublished Identifier for Lot Result Tender Lowest Value (BT-195(BT-710))",
        ),
        (
            parse_bt195_bt711_unpublished_identifier,
            merge_bt195_bt711_unpublished_identifier,
            "Unpublished Identifier for Lot Result Tender Highest Value (BT-195(BT-711))",
        ),
        (
            parse_bt195_bt712_unpublished_identifier,
            merge_bt195_bt712_unpublished_identifier,
            "Unpublished Identifier for Lot Result buyer Review Complainants (BT-195(BT-712))",
        ),
        (
            parse_bt195_bt720_unpublished_identifier,
            merge_bt195_bt720_unpublished_identifier,
            "Unpublished Identifier for Winning Tender Value (BT-195(BT-720))",
        ),
        (
            parse_bt195_bt733_unpublished_identifier,
            merge_bt195_bt733_unpublished_identifier,
            "Unpublished Identifier for Award Criteria Order Justification (BT-195(BT-733))",
        ),
        (
            parse_bt195_bt733_lotsgroup_unpublished_identifier,
            merge_bt195_bt733_lotsgroup_unpublished_identifier,
            "Unpublished Identifier for Award Criteria Order Justification in LotsGroup (BT-195(BT-733))",
        ),
        (
            parse_bt195_bt734_lot_unpublished_identifier,
            merge_bt195_bt734_lot_unpublished_identifier,
            "Unpublished Identifier for Award Criterion Name in Lot (BT-195(BT-734))",
        ),
        (
            parse_bt195_bt734_lotsgroup_unpublished_identifier,
            merge_bt195_bt734_lotsgroup_unpublished_identifier,
            "Unpublished Identifier for Award Criterion Name in LotGroup (BT-195(BT-734))",
        ),
        (
            parse_bt195_bt759_lotresult_unpublished_identifier,
            merge_bt195_bt759_lotresult_unpublished_identifier,
            "Unpublished Identifier for Received Submissions Count in Lot Result (BT-195(BT-759))",
        ),
        (
            parse_bt195_bt760_lotresult_unpublished_identifier,
            merge_bt195_bt760_lotresult_unpublished_identifier,
            "Unpublished Identifier for Received Submissions Type in Lot Result (BT-195(BT-760))",
        ),
        (
            parse_bt195_bt773_tender_unpublished_identifier,
            merge_bt195_bt773_tender_unpublished_identifier,
            "Unpublished Identifier for Subcontracting in Tender (BT-195(BT-773))",
        ),
        (
            parse_bt195_bt88_procedure_unpublished_identifier,
            merge_bt195_bt88_procedure_unpublished_identifier,
            "Unpublished Identifier for procedure Features (BT-195(BT-88))",
        ),
        # BT-196
        (
            bt_196_parse_unpublished_justification_bt_09_procedure,
            bt_196_merge_unpublished_justification_bt_09_procedure,
            "Unpublished Justification Description (BT-196, BT-09)",
        ),
        (
            parse_bt196_bt105_unpublished_justification,
            merge_bt196_bt105_unpublished_justification,
            "Unpublished Justification Description (BT-196, BT-105)",
        ),
        (
            parse_bt196_bt106_unpublished_justification,
            merge_bt196_bt106_unpublished_justification,
            "Unpublished Justification Description (BT-196, BT-106)",
        ),
        (
            parse_bt196_bt1252_unpublished_justification,
            merge_bt196_bt1252_unpublished_justification,
            "Unpublished Justification Description (BT-196, BT-1252)",
        ),
        (
            parse_bt196_bt135_unpublished_justification,
            merge_bt196_bt135_unpublished_justification,
            "Unpublished Justification Description (BT-196, BT-135)",
        ),
        (
            parse_bt196_bt1351_unpublished_justification,
            merge_bt196_bt1351_unpublished_justification,
            "Unpublished Justification Description (BT-196, BT-1351)",
        ),
        (
            parse_bt196_bt136_unpublished_justification,
            merge_bt196_bt136_unpublished_justification,
            "Unpublished Justification Description (BT-196, BT-136)",
        ),
        (
            parse_bt196_bt142_unpublished_justification,
            merge_bt196_bt142_unpublished_justification,
            "Unpublished Justification Description (BT-196, BT-142)",
        ),
        (
            parse_bt196_bt144_unpublished_justification,
            merge_bt196_bt144_unpublished_justification,
            "Unpublished Justification Description (BT-196, BT-144)",
        ),
        (
            parse_bt196_bt160_unpublished_justification,
            merge_bt196_bt160_unpublished_justification,
            "procedure BT-196(BT-160)-Tender Unpublished Justification Description",
        ),
        (
            parse_bt196_bt162_unpublished_justification,
            merge_bt196_bt162_unpublished_justification,
            "procedure BT-196(BT-162)-Tender Unpublished Justification Description",
        ),
        (
            parse_bt196_bt163_unpublished_justification,
            merge_bt196_bt163_unpublished_justification,
            "procedure BT-196(BT-163)-Tender Unpublished Justification Description",
        ),
        (
            parse_bt196_bt171_unpublished_justification,
            merge_bt196_bt171_unpublished_justification,
            "procedure BT-196(BT-171)-Tender Unpublished Justification Description",
        ),
        (
            parse_bt196_bt191_unpublished_justification,
            merge_bt196_bt191_unpublished_justification,
            "procedure BT-196(BT-191)-Tender Unpublished Justification Description",
        ),
        (
            parse_bt196_bt193_unpublished_justification,
            merge_bt196_bt193_unpublished_justification,
            "procedure BT-196(BT-193)-Tender Unpublished Justification Description",
        ),
        (
            parse_bt196_bt539_unpublished_justification,
            merge_bt196_bt539_unpublished_justification,
            "procedure BT-196(BT-539)-Lot Unpublished Justification Description",
        ),
        (
            parse_bt196_bt539_lotsgroup_unpublished_justification,
            merge_bt196_bt539_lotsgroup_unpublished_justification,
            "procedure BT-196(BT-539)-LotsGroup Unpublished Justification Description",
        ),
        (
            parse_bt196_bt540_lot_unpublished_justification,
            merge_bt196_bt540_lot_unpublished_justification,
            "procedure BT-196(BT-540)-Lot Unpublished Justification Description",
        ),
        (
            parse_bt196_bt540_lotsgroup_unpublished_justification,
            merge_bt196_bt540_lotsgroup_unpublished_justification,
            "procedure BT-196(BT-540)-LotsGroup Unpublished Justification Description",
        ),
        (
            parse_bt196_bt541_lot_fixed_unpublished_justification,
            merge_bt196_bt541_lot_fixed_unpublished_justification,
            "procedure BT-196(BT-541)-Lot-Fixed Unpublished Justification Description",
        ),
        (
            parse_bt196_bt541_lot_threshold_unpublished_justification,
            merge_bt196_bt541_lot_threshold_unpublished_justification,
            "Lot Threshold Unpublished Justification Description (BT-196(BT-541))",
        ),
        (
            parse_bt196_bt541_lot_weight_unpublished_justification,
            merge_bt196_bt541_lot_weight_unpublished_justification,
            "Lot Weight Unpublished Justification Description (BT-196(BT-541))",
        ),
        (
            parse_bt196_bt541_lotsgroup_fixed_unpublished_justification,
            merge_bt196_bt541_lotsgroup_fixed_unpublished_justification,
            "LotsGroup Fixed Unpublished Justification Description (BT-196(BT-541))",
        ),
        (
            parse_bt196_bt541_lotsgroup_threshold_unpublished_justification,
            merge_bt196_bt541_lotsgroup_threshold_unpublished_justification,
            "LotsGroup Threshold Unpublished Justification Description (BT-196(BT-541))",
        ),
        (
            parse_bt196_bt541_lotsgroup_weight,
            merge_bt196_bt541_lotsgroup_weight,
            "Unpublished Justification Description for LotsGroup Weight (BT-196(BT-541))",
        ),
        (
            parse_bt196_bt5421_lot,
            merge_bt196_bt5421_lot,
            "Unpublished Justification Description for Lot (BT-196(BT-5421))",
        ),
        (
            parse_bt196_bt5421_lotsgroup,
            merge_bt196_bt5421_lotsgroup,
            "Unpublished Justification Description for LotsGroup (BT-196(BT-5421))",
        ),
        (
            parse_bt196_bt5422_lot,
            merge_bt196_bt5422_lot,
            "Unpublished Justification Description for Lot (BT-196(BT-5422))",
        ),
        (
            parse_bt196_bt5422_lotsgroup,
            merge_bt196_bt5422_lotsgroup,
            "Unpublished Justification Description for LotsGroup (BT-196(BT-5422))",
        ),
        (
            parse_bt196_bt5423_lot,
            merge_bt196_bt5423_lot,
            "Unpublished Justification Description for Lot (BT-196(BT-5423))",
        ),
        (
            parse_bt196_bt5423_lotsgroup,
            merge_bt196_bt5423_lotsgroup,
            "Unpublished Justification Description for LotsGroup (BT-196(BT-5423))",
        ),
        (
            parse_bt196_bt543_lot,
            merge_bt196_bt543_lot,
            "Unpublished Justification Description for Lot (BT-196(BT-543))",
        ),
        (
            parse_bt196_bt543_lotsgroup,
            merge_bt196_bt543_lotsgroup,
            "Unpublished Justification Description for LotsGroup (BT-196(BT-543))",
        ),
        (
            parse_bt196_bt553_tender,
            merge_bt196_bt553_tender,
            "Unpublished Justification Description for Tender (BT-196(BT-553))",
        ),
        (
            parse_bt196_bt554_unpublished_justification,
            merge_bt196_bt554_unpublished_justification,
            "Unpublished Justification Description for Tender Subcontracting Description (BT-196(BT-554))",
        ),
        (
            parse_bt196_bt555_unpublished_justification,
            merge_bt196_bt555_unpublished_justification,
            "Unpublished Justification Description for Tender Subcontracting Percentage (BT-196(BT-555))",
        ),
        (
            parse_bt196_bt635_unpublished_justification,
            merge_bt196_bt635_unpublished_justification,
            "Unpublished Justification Description for Lot Result buyer Review Request Count (BT-196(BT-635))",
        ),
        (
            parse_bt196_bt636_unpublished_justification,
            merge_bt196_bt636_unpublished_justification,
            "Unpublished Justification Description for Lot Result buyer Review Request Irregularity Type (BT-196(BT-636))",
        ),
        (
            parse_bt196_bt660_unpublished_justification,
            merge_bt196_bt660_unpublished_justification,
            "Unpublished Justification Description for Lot Result Framework Re-estimated Value (BT-196(BT-660))",
        ),
        (
            parse_bt196_bt709_unpublished_justification,
            merge_bt196_bt709_unpublished_justification,
            "Unpublished Justification Description for Lot Result Maximum Value (BT-196(BT-709))",
        ),
        (
            parse_bt196_bt710_unpublished_justification,
            merge_bt196_bt710_unpublished_justification,
            "Unpublished Justification for Lot Result Tender Lowest Value (BT-196(BT-710))",
        ),
        (
            parse_bt196_bt711_unpublished_justification,
            merge_bt196_bt711_unpublished_justification,
            "Unpublished Justification for Lot Result Tender Highest Value (BT-196(BT-711))",
        ),
        (
            parse_bt196_bt712_unpublished_justification,
            merge_bt196_bt712_unpublished_justification,
            "Unpublished Justification for Lot Result buyer Review Complainants (BT-196(BT-712))",
        ),
        (
            parse_bt196_bt720_unpublished_justification,
            merge_bt196_bt720_unpublished_justification,
            "Unpublished Justification for Winning Tender Value (BT-196(BT-720))",
        ),
        (
            parse_bt196_bt733_unpublished_justification,
            merge_bt196_bt733_unpublished_justification,
            "Unpublished Justification for Award Criteria Order Justification (BT-196(BT-733))",
        ),
        (
            parse_bt196_bt733_lotsgroup_unpublished_justification,
            merge_bt196_bt733_lotsgroup_unpublished_justification,
            "Unpublished Justification for Award Criteria Order Justification in LotsGroup (BT-196(BT-733))",
        ),
        (
            parse_bt196_bt734_lot_unpublished_justification,
            merge_bt196_bt734_lot_unpublished_justification,
            "Unpublished Justification for Award Criterion Name in Lot (BT-196(BT-734))",
        ),
        (
            parse_bt196_bt734_lotsgroup_unpublished_justification,
            merge_bt196_bt734_lotsgroup_unpublished_justification,
            "Unpublished Justification for Award Criterion Name in Lots Group (BT-196(BT-734))",
        ),
        (
            parse_bt196_bt759_lotresult_unpublished_justification,
            merge_bt196_bt759_lotresult_unpublished_justification,
            "Unpublished Justification for Received Submissions Count in Lot Result (BT-196(BT-759))",
        ),
        (
            parse_bt196_bt760_lotresult_unpublished_justification,
            merge_bt196_bt760_lotresult_unpublished_justification,
            "Unpublished Justification for Received Submissions Type in Lot Result (BT-196(BT-760))",
        ),
        (
            parse_bt196_bt773_tender_unpublished_justification,
            merge_bt196_bt773_tender_unpublished_justification,
            "Unpublished Justification for Subcontracting in Tender (BT-196(BT-773))",
        ),
        (
            parse_bt196_bt88_procedure_unpublished_justification,
            merge_bt196_bt88_procedure_unpublished_justification,
            "Unpublished Justification for procedure Features (BT-196(BT-88))",
        ),
        # BT-197
        (
            bt_197_parse_unpublished_justification_code_bt_09_procedure,
            bt_197_merge_unpublished_justification_code_bt_09_procedure,
            "Unpublished Justification Code (BT-197, BT-09)",
        ),
        (
            parse_bt197_bt105_unpublished_justification_code,
            merge_bt197_bt105_unpublished_justification_code,
            "Unpublished Justification Code (BT-197, BT-105)",
        ),
        (
            parse_bt197_bt106_unpublished_justification_code,
            merge_bt197_bt106_unpublished_justification_code,
            "Unpublished Justification Code (BT-197, BT-106)",
        ),
        (
            parse_bt197_bt1252_unpublished_justification_code,
            merge_bt197_bt1252_unpublished_justification_code,
            "Unpublished Justification Code (BT-197, BT-1252)",
        ),
        (
            parse_bt197_bt135_unpublished_justification_code,
            merge_bt197_bt135_unpublished_justification_code,
            "Unpublished Justification Code (BT-197, BT-135)",
        ),
        (
            parse_bt197_bt1351_unpublished_justification_code,
            merge_bt197_bt1351_unpublished_justification_code,
            "Unpublished Justification Code (BT-197, BT-1351)",
        ),
        (
            parse_bt197_bt136_unpublished_justification_code,
            merge_bt197_bt136_unpublished_justification_code,
            "Unpublished Justification Code (BT-197, BT-136)",
        ),
        (
            parse_bt197_bt142_unpublished_justification_code,
            merge_bt197_bt142_unpublished_justification_code,
            "Unpublished Justification Code (BT-197, BT-142)",
        ),
        (
            parse_bt197_bt144_unpublished_justification_code,
            merge_bt197_bt144_unpublished_justification_code,
            "Unpublished Justification Code (BT-197, BT-144)",
        ),
        (
            parse_bt197_bt160_unpublished_justification_code,
            merge_bt197_bt160_unpublished_justification_code,
            "procedure BT-197(BT-160)-Tender Unpublished Justification Code",
        ),
        (
            parse_bt197_bt162_unpublished_justification_code,
            merge_bt197_bt162_unpublished_justification_code,
            "procedure BT-197(BT-162)-Tender Unpublished Justification Code",
        ),
        (
            parse_bt197_bt163_unpublished_justification_code,
            merge_bt197_bt163_unpublished_justification_code,
            "procedure BT-197(BT-163)-Tender Unpublished Justification Code",
        ),
        (
            parse_bt197_bt171_unpublished_justification_code,
            merge_bt197_bt171_unpublished_justification_code,
            "procedure BT-197(BT-171)-Tender Unpublished Justification Code",
        ),
        (
            parse_bt197_bt191_unpublished_justification_code,
            merge_bt197_bt191_unpublished_justification_code,
            "procedure BT-197(BT-191)-Tender Unpublished Justification Code",
        ),
        (
            parse_bt197_bt193_unpublished_justification_code,
            merge_bt197_bt193_unpublished_justification_code,
            "procedure BT-197(BT-193)-Tender Unpublished Justification Code",
        ),
        (
            parse_bt197_bt539_unpublished_justification_code,
            merge_bt197_bt539_unpublished_justification_code,
            "procedure BT-197(BT-539)-Lot Unpublished Justification Code",
        ),
        (
            parse_bt197_bt539_lotsgroup_unpublished_justification_code,
            merge_bt197_bt539_lotsgroup_unpublished_justification_code,
            "procedure BT-197(BT-539)-LotsGroup Unpublished Justification Code",
        ),
        (
            parse_bt197_bt540_lot_unpublished_justification_code,
            merge_bt197_bt540_lot_unpublished_justification_code,
            "procedure BT-197(BT-540)-Lot Unpublished Justification Code",
        ),
        (
            parse_bt197_bt540_lotsgroup_unpublished_justification_code,
            merge_bt197_bt540_lotsgroup_unpublished_justification_code,
            "procedure BT-197(BT-540)-LotsGroup Unpublished Justification Code",
        ),
        (
            parse_bt197_bt541_lot_fixed_unpublished_justification_code,
            merge_bt197_bt541_lot_fixed_unpublished_justification_code,
            "procedure BT-197(BT-541)-Lot-Fixed Unpublished Justification Code",
        ),
        (
            parse_bt197_bt541_lot_threshold_unpublished_justification_code,
            merge_bt197_bt541_lot_threshold_unpublished_justification_code,
            "Lot Threshold Unpublished Justification Code (BT-197(BT-541))",
        ),
        (
            parse_bt197_bt541_lot_weight_unpublished_justification_code,
            merge_bt197_bt541_lot_weight_unpublished_justification_code,
            "Lot Weight Unpublished Justification Code (BT-197(BT-541))",
        ),
        (
            parse_bt197_bt541_lotsgroup_fixed_unpublished_justification_code,
            merge_bt197_bt541_lotsgroup_fixed_unpublished_justification_code,
            "LotsGroup Fixed Unpublished Justification Code (BT-197(BT-541))",
        ),
        (
            parse_bt197_bt541_lotsgroup_threshold,
            merge_bt197_bt541_lotsgroup_threshold,
            "Unpublished Justification Code for LotsGroup Threshold (BT-197(BT-541))",
        ),
        (
            parse_bt197_bt541_lotsgroup_weight,
            merge_bt197_bt541_lotsgroup_weight,
            "Unpublished Justification Code for LotsGroup Weight (BT-197(BT-541))",
        ),
        (
            parse_bt197_bt5421_lot,
            merge_bt197_bt5421_lot,
            "Unpublished Justification Code for Lot (BT-197(BT-5421))",
        ),
        (
            parse_bt197_bt5421_lotsgroup,
            merge_bt197_bt5421_lotsgroup,
            "Unpublished Justification Code for LotsGroup (BT-197(BT-5421))",
        ),
        (
            parse_bt197_bt5422_lot,
            merge_bt197_bt5422_lot,
            "Unpublished Justification Code for Lot (BT-197(BT-5422))",
        ),
        (
            parse_bt197_bt5422_lotsgroup,
            merge_bt197_bt5422_lotsgroup,
            "Unpublished Justification Code for LotsGroup (BT-197(BT-5422))",
        ),
        (
            parse_bt197_bt5423_lot,
            merge_bt197_bt5423_lot,
            "Unpublished Justification Code for Lot (BT-197(BT-5423))",
        ),
        (
            parse_bt197_bt5423_lotsgroup,
            merge_bt197_bt5423_lotsgroup,
            "Unpublished Justification Code for LotsGroup (BT-197(BT-5423))",
        ),
        (
            parse_bt197_bt543_lot,
            merge_bt197_bt543_lot,
            "Unpublished Justification Code for Lot (BT-197(BT-543))",
        ),
        (
            parse_bt197_bt543_lotsgroup,
            merge_bt197_bt543_lotsgroup,
            "Unpublished Justification Code for LotsGroup (BT-197(BT-543))",
        ),
        (
            parse_bt197_bt553_tender,
            merge_bt197_bt553_tender,
            "Unpublished Justification Code for Tender (BT-197(BT-553))",
        ),
        (
            parse_bt197_bt554_unpublished_justification_code,
            merge_bt197_bt554_unpublished_justification_code,
            "Unpublished Justification Code for Tender Subcontracting Description (BT-197(BT-554))",
        ),
        (
            parse_bt197_bt555_unpublished_justification_code,
            merge_bt197_bt555_unpublished_justification_code,
            "Unpublished Justification Code for Tender Subcontracting Percentage (BT-197(BT-555))",
        ),
        (
            parse_bt197_bt635_unpublished_justification_code,
            merge_bt197_bt635_unpublished_justification_code,
            "Unpublished Justification Code for Lot Result buyer Review Request Count (BT-197(BT-635))",
        ),
        (
            parse_bt197_bt636_unpublished_justification_code,
            merge_bt197_bt636_unpublished_justification_code,
            "Unpublished Justification Code for Lot Result buyer Review Request Irregularity Type (BT-197(BT-636))",
        ),
        (
            parse_bt197_bt660_unpublished_justification_code,
            merge_bt197_bt660_unpublished_justification_code,
            "Unpublished Justification Code for Lot Result Framework Re-estimated Value (BT-197(BT-660))",
        ),
        (
            parse_bt197_bt709_unpublished_justification_code,
            merge_bt197_bt709_unpublished_justification_code,
            "Unpublished Justification Code for Lot Result Maximum Value (BT-197(BT-709))",
        ),
        (
            parse_bt197_bt710_unpublished_justification_code,
            merge_bt197_bt710_unpublished_justification_code,
            "Unpublished Justification Code for Lot Result Tender Lowest Value (BT-197(BT-710))",
        ),
        (
            parse_bt197_bt711_unpublished_justification_code,
            merge_bt197_bt711_unpublished_justification_code,
            "Unpublished Justification Code for Lot Result Tender Highest Value (BT-197(BT-711))",
        ),
        (
            parse_bt197_bt712_unpublished_justification_code,
            merge_bt197_bt712_unpublished_justification_code,
            "Unpublished Justification Code for Lot Result buyer Review Complainants (BT-197(BT-712))",
        ),
        (
            parse_bt197_bt720_unpublished_justification_code,
            merge_bt197_bt720_unpublished_justification_code,
            "Unpublished Justification Code for Winning Tender Value (BT-197(BT-720))",
        ),
        (
            parse_bt197_bt733_unpublished_justification_code,
            merge_bt197_bt733_unpublished_justification_code,
            "Unpublished Justification Code for Award Criteria Order Justification (BT-197(BT-733))",
        ),
        (
            parse_bt197_bt733_lotsgroup_unpublished_justification_code,
            merge_bt197_bt733_lotsgroup_unpublished_justification_code,
            "Unpublished Justification Code for Award Criteria Order Justification in LotsGroup (BT-197(BT-733))",
        ),
        (
            parse_bt197_bt734_lot_unpublished_justification_code,
            merge_bt197_bt734_lot_unpublished_justification_code,
            "Unpublished Justification Code for Award Criterion Name in Lot (BT-197(BT-734))",
        ),
        (
            parse_bt197_bt734_lotsgroup_unpublished_justification_code,
            merge_bt197_bt734_lotsgroup_unpublished_justification_code,
            "Unpublished Justification Code for Award Criterion Name in Lots Group (BT-197(BT-734))",
        ),
        (
            parse_bt197_bt759_lotresult_unpublished_justification_code,
            merge_bt197_bt759_lotresult_unpublished_justification_code,
            "Unpublished Justification Code for Received Submissions Count in Lot Result (BT-197(BT-759))",
        ),
        (
            parse_bt197_bt760_lotresult_unpublished_justification_code,
            merge_bt197_bt760_lotresult_unpublished_justification_code,
            "Unpublished Justification Code for Received Submissions Type in Lot Result (BT-197(BT-760))",
        ),
        (
            parse_bt197_bt773_tender_unpublished_justification_code,
            merge_bt197_bt773_tender_unpublished_justification_code,
            "Unpublished Justification Code for Subcontracting in Tender (BT-197(BT-773))",
        ),
        (
            parse_bt197_bt88_procedure_unpublished_justification_code,
            merge_bt197_bt88_procedure_unpublished_justification_code,
            "Unpublished Justification Code for procedure Features (BT-197(BT-88))",
        ),
        # BT-198
        (
            bt_198_parse_unpublished_access_date_bt_09_procedure,
            bt_198_merge_unpublished_access_date_bt_09_procedure,
            "Unpublished Access Date (BT-198, BT-09)",
        ),
        (
            parse_bt198_bt106_unpublished_access_date,
            merge_bt198_bt106_unpublished_access_date,
            "Unpublished Access Date (BT-198, BT-106)",
        ),
        (
            parse_bt198_bt105_unpublished_access_date,
            merge_bt198_bt105_unpublished_access_date,
            "Unpublished Access Date (BT-198, BT-105)",
        ),
        (
            parse_bt198_bt1252_unpublished_access_date,
            merge_bt198_bt1252_unpublished_access_date,
            "Unpublished Access Date (BT-198, BT-1252)",
        ),
        (
            parse_bt198_bt135_unpublished_access_date,
            merge_bt198_bt135_unpublished_access_date,
            "Unpublished Access Date (BT-198, BT-135)",
        ),
        (
            parse_bt198_bt1351_unpublished_access_date,
            merge_bt198_bt1351_unpublished_access_date,
            "Unpublished Access Date (BT-198, BT-1351)",
        ),
        (
            parse_bt198_bt142_unpublished_access_date,
            merge_bt198_bt142_unpublished_access_date,
            "Unpublished Access Date (BT-198, BT-142)",
        ),
        (
            parse_bt198_bt144_unpublished_access_date,
            merge_bt198_bt144_unpublished_access_date,
            "Unpublished Access Date (BT-198, BT-144)",
        ),
        (
            parse_bt198_bt160_unpublished_access_date,
            merge_bt198_bt160_unpublished_access_date,
            "procedure BT-198(BT-160)-Tender Unpublished Access Date",
        ),
        (
            parse_bt198_bt162_unpublished_access_date,
            merge_bt198_bt162_unpublished_access_date,
            "procedure BT-198(BT-162)-Tender Unpublished Access Date",
        ),
        (
            parse_bt198_bt163_unpublished_access_date,
            merge_bt198_bt163_unpublished_access_date,
            "procedure BT-198(BT-163)-Tender Unpublished Access Date",
        ),
        (
            parse_bt198_bt171_unpublished_access_date,
            merge_bt198_bt171_unpublished_access_date,
            "procedure BT-198(BT-171)-Tender Unpublished Access Date",
        ),
        (
            parse_bt198_bt191_unpublished_access_date,
            merge_bt198_bt191_unpublished_access_date,
            "procedure BT-198(BT-191)-Tender Unpublished Access Date",
        ),
        (
            parse_bt198_bt193_unpublished_access_date,
            merge_bt198_bt193_unpublished_access_date,
            "procedure BT-198(BT-193)-Tender Unpublished Access Date",
        ),
        (
            parse_bt198_bt539_unpublished_access_date,
            merge_bt198_bt539_unpublished_access_date,
            "procedure BT-198(BT-539)-Lot Unpublished Access Date",
        ),
        (
            parse_bt198_bt539_lotsgroup_unpublished_access_date,
            merge_bt198_bt539_lotsgroup_unpublished_access_date,
            "procedure BT-198(BT-539)-LotsGroup Unpublished Access Date",
        ),
        (
            parse_bt198_bt540_lot_unpublished_access_date,
            merge_bt198_bt540_lot_unpublished_access_date,
            "procedure BT-198(BT-540)-Lot Unpublished Access Date",
        ),
        (
            parse_bt198_bt540_lotsgroup_unpublished_access_date,
            merge_bt198_bt540_lotsgroup_unpublished_access_date,
            "procedure BT-198(BT-540)-LotsGroup Unpublished Access Date",
        ),
        (
            parse_bt198_bt541_lot_fixed_unpublished_access_date,
            merge_bt198_bt541_lot_fixed_unpublished_access_date,
            "procedure BT-198(BT-541)-Lot-Fixed Unpublished Access Date",
        ),
        (
            parse_bt198_bt541_lot_threshold_unpublished_access_date,
            merge_bt198_bt541_lot_threshold_unpublished_access_date,
            "Lot Threshold Unpublished Access Date (BT-198(BT-541))",
        ),
        (
            parse_bt198_bt541_lot_weight_unpublished_access_date,
            merge_bt198_bt541_lot_weight_unpublished_access_date,
            "Lot Weight Unpublished Access Date (BT-198(BT-541))",
        ),
        (
            parse_bt198_bt541_lotsgroup_fixed_unpublished_access_date,
            merge_bt198_bt541_lotsgroup_fixed_unpublished_access_date,
            "LotsGroup Fixed Unpublished Access Date (BT-198(BT-541))",
        ),
        (
            parse_bt198_bt541_lotsgroup_threshold,
            merge_bt198_bt541_lotsgroup_threshold,
            "Unpublished Access Date for LotsGroup Threshold (BT-198(BT-541))",
        ),
        (
            parse_bt198_bt541_lotsgroup_weight,
            merge_bt198_bt541_lotsgroup_weight,
            "Unpublished Access Date for LotsGroup Weight (BT-198(BT-541))",
        ),
        (
            parse_bt198_bt5421_lot,
            merge_bt198_bt5421_lot,
            "Unpublished Access Date for Lot (BT-198(BT-5421))",
        ),
        (
            parse_bt198_bt5421_lotsgroup,
            merge_bt198_bt5421_lotsgroup,
            "Unpublished Access Date for LotsGroup (BT-198(BT-5421))",
        ),
        (
            parse_bt198_bt5422_lot,
            merge_bt198_bt5422_lot,
            "Unpublished Access Date for Lot (BT-198(BT-5422))",
        ),
        (
            parse_bt198_bt5422_lotsgroup,
            merge_bt198_bt5422_lotsgroup,
            "Unpublished Access Date for LotsGroup (BT-198(BT-5422))",
        ),
        (
            parse_bt198_bt5423_lot,
            merge_bt198_bt5423_lot,
            "Unpublished Access Date for Lot (BT-198(BT-5423))",
        ),
        (
            parse_bt198_bt5423_lotsgroup,
            merge_bt198_bt5423_lotsgroup,
            "Unpublished Access Date for LotsGroup (BT-198(BT-5423))",
        ),
        (
            parse_bt198_bt543_lot,
            merge_bt198_bt543_lot,
            "Unpublished Access Date for Lot (BT-198(BT-543))",
        ),
        (
            parse_bt198_bt543_lotsgroup,
            merge_bt198_bt543_lotsgroup,
            "Unpublished Access Date for LotsGroup (BT-198(BT-543))",
        ),
        (
            parse_bt198_bt553_tender,
            merge_bt198_bt553_tender,
            "Unpublished Access Date for Tender (BT-198(BT-553))",
        ),
        (
            parse_bt198_bt554_unpublished_access_date,
            merge_bt198_bt554_unpublished_access_date,
            "Unpublished Access Date for Tender Subcontracting Description (BT-198(BT-554))",
        ),
        (
            parse_bt198_bt555_unpublished_access_date,
            merge_bt198_bt555_unpublished_access_date,
            "Unpublished Access Date for Tender Subcontracting Percentage (BT-198(BT-555))",
        ),
        (
            parse_bt198_bt635_unpublished_access_date,
            merge_bt198_bt635_unpublished_access_date,
            "Unpublished Access Date for Lot Result buyer Review Request Count (BT-198(BT-635))",
        ),
        (
            parse_bt198_bt636_unpublished_access_date,
            merge_bt198_bt636_unpublished_access_date,
            "Unpublished Access Date for Lot Result buyer Review Request Irregularity Type (BT-198(BT-636))",
        ),
        (
            parse_bt198_bt660_unpublished_access_date,
            merge_bt198_bt660_unpublished_access_date,
            "Unpublished Access Date for Lot Result Framework Re-estimated Value (BT-198(BT-660))",
        ),
        (
            parse_bt198_bt709_unpublished_access_date,
            merge_bt198_bt709_unpublished_access_date,
            "Unpublished Access Date for Lot Result Maximum Value (BT-198(BT-709))",
        ),
        (
            parse_bt198_bt710_unpublished_access_date,
            merge_bt198_bt710_unpublished_access_date,
            "Unpublished Access Date for Lot Result Tender Lowest Value (BT-198(BT-710))",
        ),
        (
            parse_bt198_bt711_unpublished_access_date,
            merge_bt198_bt711_unpublished_access_date,
            "Unpublished Access Date for Lot Result Tender Highest Value (BT-198(BT-711))",
        ),
        (
            parse_bt198_bt712_unpublished_access_date,
            merge_bt198_bt712_unpublished_access_date,
            "Unpublished Access Date for Lot Result buyer Review Complainants (BT-198(BT-712))",
        ),
        (
            parse_bt198_bt720_unpublished_access_date,
            merge_bt198_bt720_unpublished_access_date,
            "Unpublished Access Date for Winning Tender Value (BT-198(BT-720))",
        ),
        (
            parse_bt198_bt733_unpublished_access_date,
            merge_bt198_bt733_unpublished_access_date,
            "Unpublished Access Date for Award Criteria Order Justification (BT-198(BT-733))",
        ),
        (
            parse_bt198_bt733_lotsgroup_unpublished_access_date,
            merge_bt198_bt733_lotsgroup_unpublished_access_date,
            "Unpublished Access Date for Award Criteria Order Justification in LotsGroup (BT-198(BT-733))",
        ),
        (
            parse_bt198_bt734_lot_unpublished_access_date,
            merge_bt198_bt734_lot_unpublished_access_date,
            "Unpublished Access Date for Award Criterion Name in Lot (BT-198(BT-734))",
        ),
        (
            parse_bt198_bt734_lotsgroup_unpublished_access_date,
            merge_bt198_bt734_lotsgroup_unpublished_access_date,
            "Unpublished Access Date for Award Criterion Name in Lots Group (BT-198(BT-734))",
        ),
        (
            parse_bt198_bt759_lotresult_unpublished_access_date,
            merge_bt198_bt759_lotresult_unpublished_access_date,
            "Unpublished Access Date for Received Submissions Count in Lot Result (BT-198(BT-759))",
        ),
        (
            parse_bt198_bt760_lotresult_unpublished_access_date,
            merge_bt198_bt760_lotresult_unpublished_access_date,
            "Unpublished Access Date for Received Submissions Type in Lot Result (BT-198(BT-760))",
        ),
        (
            parse_bt198_bt773_tender_unpublished_access_date,
            merge_bt198_bt773_tender_unpublished_access_date,
            "Unpublished Access Date for Subcontracting in Tender (BT-198(BT-773))",
        ),
        (
            parse_bt198_bt88_procedure_unpublished_access_date,
            merge_bt198_bt88_procedure_unpublished_access_date,
            "Unpublished Access Date for procedure Features (BT-198(BT-88))",
        ),
        (
            parse_contract_modification_reason,
            merge_contract_modification_reason,
            "BT-200-Contract (Contract Modification Reason)",
        ),
        (
            parse_bt198_bt136_unpublished_access_date,
            merge_bt198_bt136_unpublished_access_date,
            "Unpublished Access Date (BT-198, BT-136)",
        ),
        (
            parse_contract_modification_description,
            merge_contract_modification_description,
            "BT-201-Contract (Contract Modification Description)",
        ),
        (
            parse_contract_modification_summary,
            merge_contract_modification_summary,
            "BT-202-Contract (Contract Modification Summary)",
        ),
        (parse_lot_title, merge_lot_title, "BT-21-Lot (Lot Title)"),
        (
            parse_lots_group_title,
            merge_lots_group_title,
            "BT-21-LotsGroup (Lots Group Title)",
        ),
        (parse_part_title, merge_part_title, "BT-21-part (part Title)"),
        (
            parse_procedure_title,
            merge_procedure_title,
            "BT-21-procedure (procedure Title)",
        ),
        (
            parse_lot_internal_identifier,
            merge_lot_internal_identifier,
            "BT-22-Lot (Lot Internal Identifier)",
        ),
        (parse_main_nature, merge_main_nature, "BT-23-Lot (Main Nature)"),
        (
            parse_main_nature_part,
            merge_main_nature_part,
            "BT-23-part (Main Nature part)",
        ),
        (
            parse_main_nature_procedure,
            merge_main_nature_procedure,
            "BT-23-procedure (Main Nature procedure)",
        ),
        (
            parse_lot_description,
            merge_lot_description,
            "BT-24-Lot (Lot Description)",
        ),
        (
            parse_lots_group_description,
            merge_lots_group_description,
            "BT-24-LotsGroup (Lots Group Description)",
        ),
        (
            parse_part_description,
            merge_part_description,
            "BT-24-part (part Description)",
        ),
        (
            parse_procedure_description,
            merge_procedure_description,
            "BT-24-procedure (procedure Description)",
        ),
        (parse_lot_quantity, merge_lot_quantity, "BT-25-Lot (Lot Quantity)"),
        (
            parse_classification_type,
            merge_classification_type,
            "BT-26-Lot (Classification Type)",
        ),
        (
            parse_classification_type_part,
            merge_classification_type_part,
            "BT-26-part (Classification Type part)",
        ),
        (
            parse_classification_type_procedure,
            merge_classification_type_procedure,
            "BT-26-procedure (Classification Type procedure)",
        ),
        (
            parse_main_classification_type_lot,
            merge_main_classification_type_lot,
            "Main Classification Type for Lot (BT_26m_lot)",
        ),
        (
            parse_main_classification_type_part,
            merge_main_classification_type_part,
            "Main Classification Type for part (BT_26m_part)",
        ),
        (
            parse_main_classification_type_procedure,
            merge_main_classification_type_procedure,
            "Main Classification Type for procedure (BT_26m_procedure)",
        ),
        (
            parse_main_classification_code_lot,
            merge_main_classification_code_lot,
            "Main Classification Code for Lot (BT_262_lot)",
        ),
        (
            parse_main_classification_code_part,
            merge_main_classification_code_part,
            "Main Classification Code for part (BT_262_part)",
        ),
        (
            parse_main_classification_code_procedure,
            merge_main_classification_code_procedure,
            "Main Classification Code for procedure (BT_262_procedure)",
        ),
        (
            parse_additional_classification_code,
            merge_additional_classification_code,
            "Additional Classification Code (BT-263-Lot)",
        ),
        (
            parse_additional_classification_code_part,
            merge_additional_classification_code_part,
            "Additional Classification Code for part (BT_263_part)",
        ),
        (
            parse_additional_classification_code_procedure,
            merge_additional_classification_code_procedure,
            "Additional Classification Code for procedure (BT_263_procedure)",
        ),
        (
            parse_lot_estimated_value,
            merge_lot_estimated_value,
            "Lot Estimated Value (BT-27-Lot)",
        ),
        (
            parse_bt_27_lots_group,
            merge_bt_27_lots_group,
            "LotsGroup Estimated Value (BT-27-LotsGroup)",
        ),
        (parse_bt_27_part, merge_bt_27_part, "part Estimated Value (BT-27-part)"),
        (
            parse_bt_27_procedure,
            merge_bt_27_procedure,
            "procedure Estimated Value (BT-27-procedure)",
        ),
        (
            parse_bt_271_lot,
            merge_bt_271_lot,
            "Lot Framework Maximum Value (BT-271-Lot)",
        ),
        (
            parse_bt_271_lots_group,
            merge_bt_271_lots_group,
            "LotsGroup Framework Maximum Value (BT-271-LotsGroup)",
        ),
        (
            parse_bt_271_procedure,
            merge_bt_271_procedure,
            "procedure Framework Maximum Value (BT-271-procedure)",
        ),
        (
            parse_lot_additional_info,
            merge_lot_additional_info,
            "BT-300-Lot (Lot Additional Information)",
        ),
        (
            parse_lotsgroup_additional_info,
            merge_lotsgroup_additional_info,
            "BT-300-LotsGroup (Lots Group Additional Information)",
        ),
        (
            parse_part_additional_info,
            merge_part_additional_info,
            "BT-300-part (part Additional Information)",
        ),
        (
            parse_procedure_additional_info,
            merge_procedure_additional_info,
            "BT-300-procedure (procedure Additional Information)",
        ),
        (
            parse_max_lots_allowed,
            merge_max_lots_allowed,
            "BT-31-procedure (Maximum Lots Allowed)",
        ),
        (
            parse_tender_identifier,
            merge_tender_identifier,
            "BT-3201-Tender (Tender Identifier)",
        ),
        (
            parse_contract_tender_id,
            merge_contract_tender_id,
            "BT-3202-Contract (Contract Tender ID)",
        ),
        (
            parse_max_lots_awarded,
            merge_max_lots_awarded,
            "BT-33 (Maximum Lots Awarded)",
        ),
        (
            parse_group_identifier,
            merge_group_identifier,
            "BT-330 (Group Identifier)",
        ),
        (parse_lot_duration, merge_lot_duration, "BT-36-Lot (Lot Duration)"),
        (parse_part_duration, merge_part_duration, "BT-36-part (part Duration)"),
        (
            parse_lot_selection_criteria_second_stage,
            merge_lot_selection_criteria_second_stage,
            "BT-40-Lot (Lot Selection Criteria Second Stage)",
        ),
        (
            parse_lot_following_contract,
            merge_lot_following_contract,
            "BT-41-Lot (Lot Following Contract)",
        ),
        (
            parse_lot_jury_decision_binding,
            merge_lot_jury_decision_binding,
            "BT-42-Lot (Lot Jury Decision Binding)",
        ),
        (parse_prize_rank, merge_prize_rank, "BT-44-Lot (Prize Rank)"),
        (
            parse_lot_rewards_other,
            merge_lot_rewards_other,
            "BT-45-Lot (Lot Rewards Other)",
        ),
        (
            parse_jury_member_name,
            merge_jury_member_name,
            "BT-46-Lot (Jury Member Name)",
        ),
        (
            parse_participant_name,
            merge_participant_name,
            "BT-47-Lot (participant Name)",
        ),
        (
            parse_minimum_candidates,
            merge_minimum_candidates,
            "BT-50-Lot (Minimum Candidates)",
        ),
        (parse_ubo_name, merge_ubo_name, "BT-500 (ubo Name)"),
        (
            parse_organization_identifier,
            merge_organization_identifier,
            "BT-501 (organization Identifier)",
        ),
        (
            parse_eu_funds_financing_identifier,
            merge_eu_funds_financing_identifier,
            "BT-5010-Lot (EU Funds Financing Identifier)",
        ),
        (
            parse_contract_eu_funds_financing_identifier,
            merge_contract_eu_funds_financing_identifier,
            "BT-5011-Contract (Contract EU Funds Financing Identifier)",
        ),
        (
            parse_organization_contact_point,
            merge_organization_contact_point,
            "BT-502-organization-company (organization Contact Point)",
        ),
        (
            parse_organization_touchpoint_contact_point,
            merge_organization_touchpoint_contact_point,
            "Organization TouchPoint Contact Point (BT-502)",
        ),
        (
            parse_organization_telephone,
            merge_organization_telephone,
            "Organization Contact Telephone Number (BT-503)",
        ),
        (
            parse_organization_touchpoint_telephone,
            merge_organization_touchpoint_telephone,
            "Organization TouchPoint Contact Telephone Number (BT-503)",
        ),
        (parse_ubo_telephone, merge_ubo_telephone, "BT-503-ubo (ubo Telephone)"),
        (
            parse_organization_website,
            merge_organization_website,
            "BT-505-organization-company (organization Website)",
        ),
        (
            parse_organization_touchpoint_website,
            merge_organization_touchpoint_website,
            "Organization TouchPoint Internet Address (BT-505)",
        ),
        (
            parse_organization_email,
            merge_organization_email,
            "Organization Contact Email Address (BT-506)",
        ),
        (
            parse_organization_touchpoint_email,
            merge_organization_touchpoint_email,
            "Organization TouchPoint Contact Email Address (BT-506)",
        ),
        (parse_ubo_email, merge_ubo_email, "BT-506-ubo (ubo Email)"),
        (
            parse_organization_country_subdivision,
            merge_organization_country_subdivision,
            "BT-507-organization-company (organization Country Subdivision)",
        ),
        (
            parse_organization_touchpoint_country_subdivision,
            merge_organization_touchpoint_country_subdivision,
            "Organization TouchPoint Country Subdivision (BT-507)",
        ),
        (
            parse_ubo_country_subdivision,
            merge_ubo_country_subdivision,
            "BT-507-ubo (ubo Country Subdivision)",
        ),
        (
            parse_place_performance_country_subdivision,
            merge_place_performance_country_subdivision,
            "BT-5071-Lot (Place Performance Country Subdivision)",
        ),
        (
            parse_place_performance_country_subdivision_part,
            merge_place_performance_country_subdivision_part,
            "Place Performance Country Subdivision part (BT-5071)",
        ),
        (
            parse_place_performance_country_subdivision_procedure,
            merge_place_performance_country_subdivision_procedure,
            "BT-5071-procedure (procedure Place Performance Country Subdivision)",
        ),
        (
            parse_buyer_profile_url,
            merge_buyer_profile_url,
            "BT-508-procedure-buyer (buyer Profile URL)",
        ),
        (
            parse_organization_edelivery_gateway,
            merge_organization_edelivery_gateway,
            "BT-509-organization-company (organization eDelivery Gateway)",
        ),
        (
            parse_touchpoint_edelivery_gateway,
            merge_touchpoint_edelivery_gateway,
            "BT-509-organization-touchpoint (touchpoint eDelivery Gateway)",
        ),
        (
            parse_lot_maximum_candidates,
            merge_lot_maximum_candidates,
            "BT-51-Lot (Lot Maximum Candidates Number)",
        ),
        (
            parse_organization_street,
            merge_organization_street,
            "BT-510(a)-organization-company (organization Street)",
        ),
        (
            parse_touchpoint_street,
            merge_touchpoint_street,
            "BT-510(a)-organization-touchpoint (touchpoint Street)",
        ),
        (parse_ubo_street, merge_ubo_street, "BT-510(a)-ubo (ubo Street)"),
        (
            parse_organization_streetline1,
            merge_organization_streetline1,
            "BT-510(b)-organization-company (organization Streetline 1)",
        ),
        (
            parse_touchpoint_streetline1,
            merge_touchpoint_streetline1,
            "BT-510(b)-organization-touchpoint (touchpoint Streetline 1)",
        ),
        (
            parse_ubo_streetline1,
            merge_ubo_streetline1,
            "BT-510(b)-ubo (ubo Streetline 1)",
        ),
        (
            parse_organization_streetline2,
            merge_organization_streetline2,
            "BT-510(c)-organization-company (organization Streetline 2)",
        ),
        (
            parse_touchpoint_streetline2,
            merge_touchpoint_streetline2,
            "BT-510(c)-organization-touchpoint (touchpoint Streetline 2)",
        ),
        (
            parse_ubo_streetline2,
            merge_ubo_streetline2,
            "BT-510(c)-ubo (ubo Streetline 2)",
        ),
        (
            parse_place_performance_street_lot,
            merge_place_performance_street_lot,
            "Place Performance Street Lot (BT-5101)",
        ),
        (
            parse_part_place_performance_street,
            merge_part_place_performance_street,
            "BT-5101(a)-part (part Place Performance Street)",
        ),
        (
            parse_procedure_place_performance_street,
            merge_procedure_place_performance_street,
            "BT-5101(a)-procedure (procedure Place Performance Street)",
        ),
        (
            parse_part_place_performance_streetline1,
            merge_part_place_performance_streetline1,
            "BT-5101(b)-part (part Place Performance Streetline 1)",
        ),
        (
            parse_procedure_place_performance_streetline1,
            merge_procedure_place_performance_streetline1,
            "BT-5101(b)-procedure (procedure Place Performance Streetline 1)",
        ),
        (
            parse_part_place_performance_streetline2,
            merge_part_place_performance_streetline2,
            "BT-5101(c)-part (part Place Performance Streetline 2)",
        ),
        (
            parse_procedure_place_performance_streetline2,
            merge_procedure_place_performance_streetline2,
            "BT-5101(c)-procedure (procedure Place Performance Streetline 2)",
        ),
        (
            parse_organization_postcode,
            merge_organization_postcode,
            "BT-512-organization-company (organization Postcode)",
        ),
        (
            parse_touchpoint_postcode,
            merge_touchpoint_postcode,
            "BT-512-organization-touchpoint (touchpoint Postcode)",
        ),
        (parse_ubo_postcode, merge_ubo_postcode, "BT-512-ubo (ubo Postcode)"),
        (
            parse_place_performance_post_code,
            merge_place_performance_post_code,
            "BT-5121-Lot (Place Performance Post Code)",
        ),
        (
            parse_place_performance_post_code_part,
            merge_place_performance_post_code_part,
            "BT-5121-part (Place Performance Post Code part)",
        ),
        (
            parse_place_performance_post_code_procedure,
            merge_place_performance_post_code_procedure,
            "BT-5121-procedure (Place Performance Post Code)",
        ),
        (
            parse_organization_city,
            merge_organization_city,
            "BT-513-organization-company (organization City)",
        ),
        (
            parse_organization_touchpoint_city,
            merge_organization_touchpoint_city,
            "Organization TouchPoint City (BT-513)",
        ),
        (parse_ubo_city, merge_ubo_city, "BT-513-ubo (ubo City)"),
        (
            parse_place_performance_city,
            merge_place_performance_city,
            "BT-5131 (Place Performance City)",
        ),
        (
            parse_place_performance_city_part,
            merge_place_performance_city_part,
            "BT-5131 part (Place Performance City part)",
        ),
        (
            parse_place_performance_city_procedure,
            merge_place_performance_city_procedure,
            "BT-5131 procedure (Place Performance City procedure)",
        ),
        (
            parse_organization_country,
            merge_organization_country,
            "BT-514-organization-company (organization Country)",
        ),
        (
            parse_touchpoint_country,
            merge_touchpoint_country,
            "BT-514-organization-touchpoint (touchpoint Country)",
        ),
        (parse_ubo_country, merge_ubo_country, "BT-514-ubo (ubo Country)"),
        (parse_lot_country, merge_lot_country, "BT-5141-Lot (Lot Country)"),
        (parse_part_country, merge_part_country, "BT-5141-part (part Country)"),
        (
            parse_procedure_country,
            merge_procedure_country,
            "BT-5141-procedure (procedure Country)",
        ),
        (
            parse_successive_reduction_indicator,
            merge_successive_reduction_indicator,
            "BT-52-Lot (Successive Reduction Indicator)",
        ),
        (
            parse_lot_additional_nature,
            merge_lot_additional_nature,
            "BT-531-Lot (Lot Additional Nature)",
        ),
        (
            parse_part_additional_nature,
            merge_part_additional_nature,
            "BT-531-part (part Additional Nature)",
        ),
        (
            parse_procedure_additional_nature,
            merge_procedure_additional_nature,
            "BT-531-procedure (procedure Additional Nature)",
        ),
        (parse_lot_start_date, merge_lot_start_date, "BT-536-Lot"),
        (
            parse_part_contract_start_date,
            merge_part_contract_start_date,
            "BT-536-part",
        ),
        (parse_lot_duration_end_date, merge_lot_duration_end_date, "BT-537-Lot"),
        (parse_part_duration_end_date, merge_part_duration_end_date, "BT-537-part"),
        (parse_lot_duration_other, merge_lot_duration_other, "BT-538-Lot"),
        (parse_part_duration_other, merge_part_duration_other, "BT-538-part"),
        (
            parse_award_criterion_type,
            merge_award_criterion_type,
            "BT-539-Lot (Award Criterion Type)",
        ),
        (
            parse_award_criterion_type_lots_group,
            merge_award_criterion_type_lots_group,
            "BT-539-LotsGroup (Award Criterion Type for Lot Groups)",
        ),
        (
            parse_award_criterion_description,
            merge_award_criterion_description,
            "BT-540-Lot (Award Criterion Description)",
        ),
        (
            parse_award_criterion_description_lots_group,
            merge_award_criterion_description_lots_group,
            "BT-540-LotsGroup (Award Criterion Description for Lot Groups)",
        ),
        (
            parse_options_description,
            merge_options_description,
            "BT-54-Lot (Options Description)",
        ),
        (
            parse_award_criterion_fixed_number,
            merge_award_criterion_fixed_number,
            "BT-541-Lot-FixedNumber (Award Criterion Fixed Number)",
        ),
        (
            parse_award_criterion_number_weight_lot,
            merge_award_criterion_number_weight_lot,
            "BT-5421-Lot",
        ),
        (
            parse_award_criterion_number_weight_lots_group,
            merge_award_criterion_number_weight_lots_group,
            "BT-5421-LotsGroup",
        ),
        (
            parse_award_criterion_number_fixed,
            merge_award_criterion_number_fixed,
            "BT-5422-Lot",
        ),
        (
            parse_award_criterion_number_fixed_lotsgroup,
            merge_award_criterion_number_fixed_lotsgroup,
            "BT-5422-LotsGroup",
        ),
        (
            parse_award_criterion_number_threshold,
            merge_award_criterion_number_threshold,
            "BT-5423-Lot",
        ),
        (
            parse_award_criterion_number_threshold_lotsgroup,
            merge_award_criterion_number_threshold_lotsgroup,
            "BT-5423-LotsGroup",
        ),
        (
            parse_award_criteria_complicated,
            merge_award_criteria_complicated,
            "BT-543-Lot",
        ),
        (
            parse_award_criteria_complicated_lotsgroup,
            merge_award_criteria_complicated_lotsgroup,
            "BT-543-LotsGroup",
        ),
        (
            parse_subcontracting_value,
            merge_subcontracting_value,
            "BT-553-Tender (Subcontracting Value)",
        ),
        (
            parse_subcontracting_description,
            merge_subcontracting_description,
            "BT-554-Tender (Subcontracting Description)",
        ),
        (
            parse_subcontracting_percentage,
            merge_subcontracting_percentage,
            "BT-555-Tender (Subcontracting Percentage)",
        ),
        (
            parse_renewal_description,
            merge_renewal_description,
            "BT-57-Lot (Renewal Description)",
        ),
        (
            parse_renewal_maximum,
            merge_renewal_maximum,
            "BT-58-Lot (Renewal Maximum)",
        ),
        (parse_eu_funds, merge_eu_funds, "BT-60-Lot (EU Funds)"),
        (
            parse_activity_entity,
            merge_activity_entity,
            "BT-610-procedure-buyer (Activity Entity)",
        ),
        (
            parse_contract_eu_funds_details,
            merge_contract_eu_funds_details,
            "BT-6110-Contract (Contract EU Funds Details)",
        ),
        (
            parse_lot_eu_funds_details,
            merge_lot_eu_funds_details,
            "BT-6140-Lot (EU Funds Details)",
        ),
        (
            parse_documents_restricted_url,
            merge_documents_restricted_url,
            "BT-615-Lot (Documents Restricted URL)",
        ),
        (
            parse_documents_restricted_url_part,
            merge_documents_restricted_url_part,
            "BT-615-part (Documents Restricted URL for parts)",
        ),
        (parse_unit, merge_unit, "BT-625-Lot (Unit)"),
        (parse_variants, merge_variants, "BT-63-Lot (Variants)"),
        (
            parse_deadline_receipt_expressions,
            merge_deadline_receipt_expressions,
            "BT-630-Lot Deadline Receipt Expressions",
        ),
        (
            parse_dispatch_invitation_interest,
            merge_dispatch_invitation_interest,
            "BT-631-Lot (Dispatch Invitation Interest)",
        ),
        (parse_tool_name, merge_tool_name, "BT-632-Lot (Tool Name)"),
        (parse_tool_name_part, merge_tool_name_part, "BT-632-part (Tool Name)"),
        (
            parse_organization_natural_person,
            merge_organization_natural_person,
            "BT-633-organization (Organisation Natural Person)",
        ),
        (
            parse_buyer_review_requests_count,
            merge_buyer_review_requests_count,
            "BT-635-LotResult buyer Review Requests Count",
        ),
        (
            parse_buyer_review_requests_irregularity_type,
            merge_buyer_review_requests_irregularity_type,
            "BT-636-LotResult Buyer Review Requests Irregularity Type",
        ),
        (
            parse_subcontracting_obligation_minimum,
            merge_subcontracting_obligation_minimum,
            "BT-64-Lot (Subcontracting Obligation Minimum)",
        ),
        (parse_lot_prize_value, merge_lot_prize_value, "BT-644-Lot (Prize Value)"),
        (
            parse_subcontracting_obligation,
            merge_subcontracting_obligation,
            "BT-65-Lot Subcontracting Obligation",
        ),
        (
            parse_subcontracting_tender_indication,
            merge_subcontracting_tender_indication,
            "BT-651-Lot Subcontracting Tender Indication",
        ),
        (
            parse_framework_reestimated_value,
            merge_framework_reestimated_value,
            "BT-660-LotResult (Framework Re-estimated Value)",
        ),
        (
            parse_exclusion_grounds,
            merge_exclusion_grounds,
            "BT-67 Exclusion Grounds",
        ),
        (
            parse_foreign_subsidies_regulation,
            merge_foreign_subsidies_regulation,
            "BT-681-Lot",
        ),
        (
            parse_foreign_subsidies_measures,
            merge_foreign_subsidies_measures,
            "BT-682-Tender",
        ),
        (
            parse_lot_performance_terms,
            merge_lot_performance_terms,
            "BT-70-Lot (Performance Terms)",
        ),
        (
            parse_notice_language,
            merge_notice_language,
            "BT-702(a)-notice (notice Official Language)",
        ),
        (
            parse_ubo_nationality,
            merge_ubo_nationality,
            "BT-706-ubo Winner Owner Nationality",
        ),
        (
            parse_lot_documents_restricted_justification,
            merge_lot_documents_restricted_justification,
            "BT-707-Lot (Documents Restricted Justification)",
        ),
        (
            parse_part_documents_restricted_justification,
            merge_part_documents_restricted_justification,
            "BT-707-part (Documents Restricted Justification)",
        ),
        (
            parse_lot_documents_official_language,
            merge_lot_documents_official_language,
            "BT-708-Lot (Documents Official Language)",
        ),
        (
            parse_part_documents_official_language,
            merge_part_documents_official_language,
            "BT-708-part (Documents Official Language)",
        ),
        (
            parse_framework_maximum_value,
            merge_framework_maximum_value,
            "BT-709-LotResult (Framework Maximum Value)",
        ),
        (
            parse_reserved_participation,
            merge_reserved_participation,
            "BT-71-Lot (Reserved participation)",
        ),
        (
            parse_reserved_participation_part,
            merge_reserved_participation_part,
            "BT-71-part (Reserved participation)",
        ),
        (
            parse_tender_value_lowest,
            merge_tender_value_lowest,
            "BT-710-LotResult Tender Value Lowest",
        ),
        (
            parse_tender_value_highest,
            merge_tender_value_highest,
            "BT-711-LotResult Tender Value Highest",
        ),
        (
            parse_buyer_review_complainants_code,
            merge_buyer_review_complainants_code,
            "BT-712(a)-LotResult buyer Review Complainants",
        ),
        (
            parse_buyer_review_complainants_number,
            merge_buyer_review_complainants_number,
            "BT-712(b)-LotResult buyer Review Complainants (Number)",
        ),
        (
            parse_clean_vehicles_directive,
            merge_clean_vehicles_directive,
            "Clean Vehicles Directive (BT-717-Lot)",
        ),
        (
            parse_procurement_documents_change_date,
            merge_procurement_documents_change_date,
            "Procurement Documents Change Date (BT-719-notice)",
        ),
        (parse_tender_value, merge_tender_value, "Tender Value (BT-720-Tender)"),
        (
            parse_contract_title,
            merge_contract_title,
            "Contract Title (BT-721-Contract)",
        ),
        (
            parse_contract_eu_funds,
            merge_contract_eu_funds,
            "Contract EU Funds (BT-722-Contract)",
        ),
        (parse_lot_eu_funds, merge_lot_eu_funds, "Lot EU Funds (BT-7220-Lot)"),
        (
            parse_vehicle_category,
            merge_vehicle_category,
            "Vehicle Category (BT-723-LotResult)",
        ),
        (
            parse_lot_sme_suitability,
            merge_lot_sme_suitability,
            "Lot SME Suitability (BT-726-Lot)",
        ),
        (
            parse_lots_group_sme_suitability,
            merge_lots_group_sme_suitability,
            "Lots Group SME Suitability (BT-726-LotsGroup)",
        ),
        (
            parse_part_sme_suitability,
            merge_part_sme_suitability,
            "part SME Suitability (BT-726-part)",
        ),
        (
            parse_lot_place_performance,
            merge_lot_place_performance,
            "Lot Place of Performance (BT-727-Lot)",
        ),
        (
            parse_part_place_performance,
            merge_part_place_performance,
            "part Place of Performance (BT-727-part)",
        ),
        (
            parse_procedure_place_performance,
            merge_procedure_place_performance,
            "procedure Place of Performance (BT-727-procedure)",
        ),
        (
            parse_lot_place_performance_additional,
            merge_lot_place_performance_additional,
            "Additional Lot Place of Performance (BT-728-Lot)",
        ),
        (
            parse_part_place_performance_additional,
            merge_part_place_performance_additional,
            "Additional part Place of Performance (BT-728-part)",
        ),
        (
            parse_procedure_place_performance_additional,
            merge_procedure_place_performance_additional,
            "Additional procedure Place of Performance (BT-728-procedure)",
        ),
        (
            parse_lot_subcontracting_obligation_maximum,
            merge_lot_subcontracting_obligation_maximum,
            "Lot Subcontracting Obligation Maximum Percentage (BT-729-Lot)",
        ),
        (
            parse_lot_security_clearance_description,
            merge_lot_security_clearance_description,
            "Lot Security Clearance Description (BT-732-Lot)",
        ),
        (
            parse_lot_award_criteria_order_justification,
            merge_lot_award_criteria_order_justification,
            "Lot Award Criteria Order Justification (BT-733-Lot)",
        ),
        (
            parse_lots_group_award_criteria_order_justification,
            merge_lots_group_award_criteria_order_justification,
            "Lots Group Award Criteria Order Justification (BT-733-LotsGroup)",
        ),
        (
            parse_award_criterion_name,
            merge_award_criterion_name,
            "Lot Award Criterion Name (BT-734-Lot)",
        ),
        (
            parse_award_criterion_name_lotsgroup,
            merge_award_criterion_name_lotsgroup,
            "Lots Group Award Criterion Name (BT-734-LotsGroup)",
        ),
        (
            parse_cvd_contract_type,
            merge_cvd_contract_type,
            "Lot CVD Contract Type (BT-735-Lot)",
        ),
        (
            parse_cvd_contract_type_lotresult,
            merge_cvd_contract_type_lotresult,
            "LotResult CVD Contract Type (BT-735-LotResult)",
        ),
        (
            parse_reserved_execution,
            merge_reserved_execution,
            "Lot Reserved Execution (BT-736-Lot)",
        ),
        (
            parse_reserved_execution_part,
            merge_reserved_execution_part,
            "part Reserved Execution (BT-736-part)",
        ),
        (
            parse_documents_unofficial_language,
            merge_documents_unofficial_language,
            "Lot Documents Unofficial Language (BT-737-Lot)",
        ),
        (
            parse_documents_unofficial_language_part,
            merge_documents_unofficial_language_part,
            "part Documents Unofficial Language (BT-737-part)",
        ),
        (
            parse_notice_preferred_publication_date,
            merge_notice_preferred_publication_date,
            "notice Preferred Publication Date (BT-738-notice)",
        ),
        (
            parse_organization_contact_fax,
            merge_organization_contact_fax,
            "Organisation Contact Fax (BT-739-organization-company)",
        ),
        (
            parse_touchpoint_contact_fax,
            merge_touchpoint_contact_fax,
            "touchpoint Contact Fax (BT-739-organization-touchpoint)",
        ),
        (parse_ubo_fax, merge_ubo_fax, "BT-739-ubo (ubo Fax)"),
        (
            parse_buyer_contracting_entity,
            merge_buyer_contracting_entity,
            "buyer Contracting Entity (BT-740-procedure-buyer)",
        ),
        (
            parse_electronic_invoicing,
            merge_electronic_invoicing,
            "Lot Electronic Invoicing (BT-743-Lot)",
        ),
        (
            parse_submission_electronic_signature,
            merge_submission_electronic_signature,
            "Lot Submission Electronic Signature (BT-744-Lot)",
        ),
        (
            parse_submission_nonelectronic_description,
            merge_submission_nonelectronic_description,
            "Lot Submission Nonelectronic Description (BT-745-Lot)",
        ),
        (
            parse_winner_listed,
            merge_winner_listed,
            "organization Winner Listed (BT-746-organization)",
        ),
        (
            parse_guarantee_required_description,
            merge_guarantee_required_description,
            "Lot Guarantee Required Description (BT-75-Lot)",
        ),
        (
            parse_selection_criteria,
            merge_selection_criteria,
            "Selection Criteria (BT-749 and BT-750)",
        ),
        (
            parse_selection_criteria_threshold_number,
            merge_selection_criteria_threshold_number,
            "Selection Criteria Second Stage Invite Threshold Number (BT-752-Lot-ThresholdNumber)",
        ),
        (
            parse_selection_criteria_weight_number,
            merge_selection_criteria_weight_number,
            "Selection Criteria Second Stage Invite Weight Number (BT-752-Lot-WeightNumber)",
        ),
        (
            parse_selection_criteria_number_weight,
            merge_selection_criteria_number_weight,
            "Selection Criteria Second Stage Invite Number Weight (BT-7531-Lot)",
        ),
        (
            parse_selection_criteria_number_threshold,
            merge_selection_criteria_number_threshold,
            "Selection Criteria Second Stage Invite Number Threshold (BT-7532-Lot)",
        ),
        (
            parse_accessibility_criteria,
            merge_accessibility_criteria,
            "Lot Accessibility Criteria (BT-754-Lot)",
        ),
        (
            parse_accessibility_justification,
            merge_accessibility_justification,
            "Lot Accessibility Justification (BT-755-Lot)",
        ),
        (
            parse_pin_competition_termination,
            merge_pin_competition_termination,
            "PIN Competition Termination (BT-756-procedure)",
        ),
        (
            parse_received_submissions_count,
            merge_received_submissions_count,
            "BT-759-LotResult Received Submissions Count",
        ),
        (
            parse_tenderer_legal_form,
            merge_tenderer_legal_form,
            "Lot Tenderer Legal Form Description (BT-76-Lot)",
        ),
        (
            parse_received_submissions_type,
            merge_received_submissions_type,
            "BT-760-LotResult Received Submissions Type",
        ),
        (
            parse_change_reason_description,
            merge_change_reason_description,
            "Change Reason Description (BT-762-notice)",
        ),
        (
            parse_lots_all_required,
            merge_lots_all_required,
            "Lots All Required (BT-763-procedure)",
        ),
        (
            parse_submission_electronic_catalogue,
            merge_submission_electronic_catalogue,
            "Submission Electronic Catalogue (BT-764-Lot)",
        ),
        (
            parse_framework_agreement,
            merge_framework_agreement,
            "Framework Agreement (BT-765-Lot)",
        ),
        (
            parse_part_framework_agreement,
            merge_part_framework_agreement,
            "part Framework Agreement (BT-765-part)",
        ),
        (
            parse_dynamic_purchasing_system,
            merge_dynamic_purchasing_system,
            "Dynamic Purchasing System (BT-766-Lot)",
        ),
        (
            parse_part_dynamic_purchasing_system,
            merge_part_dynamic_purchasing_system,
            "part Dynamic Purchasing System (BT-766-part)",
        ),
        (
            parse_electronic_auction,
            merge_electronic_auction,
            "Electronic Auction (BT-767-Lot)",
        ),
        (
            parse_multiple_tenders,
            merge_multiple_tenders,
            "Multiple Tenders (BT-769-Lot)",
        ),
        (
            parse_financial_terms,
            merge_financial_terms,
            "Financial Terms (BT-77-Lot)",
        ),
        (
            parse_late_tenderer_info,
            merge_late_tenderer_info,
            "Late Tenderer Information (BT-771-Lot)",
        ),
        (
            parse_late_tenderer_info_description,
            merge_late_tenderer_info_description,
            "Late Tenderer Information Description (BT-772-Lot)",
        ),
        (
            parse_subcontracting,
            merge_subcontracting,
            "Subcontracting (BT-773-Tender)",
        ),
        (
            parse_green_procurement,
            merge_green_procurement,
            "Green Procurement (BT-774-Lot)",
        ),
        (
            parse_social_procurement,
            merge_social_procurement,
            "Social Procurement (BT-775-Lot)",
        ),
        (
            parse_procurement_innovation,
            merge_procurement_innovation,
            "Procurement of Innovation (BT-776-Lot)",
        ),
        (
            parse_strategic_procurement_description,
            merge_strategic_procurement_description,
            "Strategic Procurement Description (BT-777-Lot)",
        ),
        (
            parse_security_clearance_deadline,
            merge_security_clearance_deadline,
            "Security Clearance Deadline (BT-78-Lot)",
        ),
        (
            parse_performing_staff_qualification,
            merge_performing_staff_qualification,
            "Performing Staff Qualification (BT-79-Lot)",
        ),
        (
            parse_non_disclosure_agreement,
            merge_non_disclosure_agreement,
            "Non Disclosure Agreement (BT-801-Lot)",
        ),
        (
            parse_non_disclosure_agreement_description,
            merge_non_disclosure_agreement_description,
            "Non Disclosure Agreement Description (BT-802-Lot)",
        ),
        (
            parse_green_procurement_criteria,
            merge_green_procurement_criteria,
            "Green Procurement Criteria (BT-805-Lot)",
        ),
        (
            parse_exclusion_grounds_sources,
            merge_exclusion_grounds_sources,
            "Exclusion Grounds Source (BT-806-Procedure)",
        ),
        (
            parse_selection_criteria_809,
            merge_selection_criteria_809,
            "Selection Criteria (BT-809-Lot)",
        ),
        (
            parse_selection_criteria_source,
            merge_selection_criteria_source,
            "Selection Criteria Source (BT-821-Lot)",
        ),
        (
            parse_procedure_features,
            merge_procedure_features,
            "procedure Features (BT-88-procedure)",
        ),
        (
            parse_electronic_ordering,
            merge_electronic_ordering,
            "Electronic Ordering (BT-92-Lot)",
        ),
        (
            parse_electronic_payment,
            merge_electronic_payment,
            "Electronic Payment (BT-93-Lot)",
        ),
        (parse_recurrence, merge_recurrence, "Recurrence (BT-94-Lot)"),
        (
            parse_recurrence_description,
            merge_recurrence_description,
            "Recurrence Description (BT-95-Lot)",
        ),
        (
            parse_submission_language,
            merge_submission_language,
            "Submission Language (BT-97-Lot)",
        ),
        (
            parse_tender_validity_deadline,
            merge_tender_validity_deadline,
            "Tender Validity Deadline (BT-98-Lot)",
        ),
        (
            parse_review_deadline_description,
            merge_review_deadline_description,
            "Review Deadline Description (BT-99-Lot)",
        ),
        ################################################################OPP
        ##########################################################################
        (
            map_extended_duration_indicator,
            merge_extended_duration_indicator,
            "ExtendedDurationIndicator (OPP-020)",
        ),
        (
            map_essential_assets,
            merge_essential_assets,
            "Essential Assets (OPP-021_Contract)",
        ),
        (
            map_asset_significance,
            merge_asset_significance,
            "Asset Significance (OPP_022_Contract)",
        ),
        (
            map_asset_predominance,
            merge_asset_predominance,
            "Asset Predominance (OPP_023_Contract)",
        ),
        (
            parse_contract_conditions,
            merge_contract_conditions,
            "Contract Conditions (OPP-031-Tender)",
        ),
        (
            parse_revenues_allocation,
            merge_revenues_allocation,
            "Revenues Allocation (OPP-032-Tender)",
        ),
        (
            parse_penalties_and_rewards,
            merge_penalties_and_rewards,
            "Penalties and Rewards (OPP-034-Tender)",
        ),
        (
            parse_main_nature_sub_type,
            merge_main_nature_sub_type,
            "Main Nature - Sub Type (OPP-040-procedure)",
        ),
        (
            parse_buyers_group_lead_indicator,
            merge_buyers_group_lead_indicator,
            "buyers Group Lead Indicator (OPP-050-organization)",
        ),
        (
            parse_awarding_cpb_buyer_indicator,
            merge_awarding_cpb_buyer_indicator,
            "Awarding CPB buyer Indicator (OPP-051-organization)",
        ),
        (
            parse_acquiring_cpb_buyer_indicator,
            merge_acquiring_cpb_buyer_indicator,
            "Acquiring CPB buyer Indicator (OPP-052-organization)",
        ),
        (
            parse_kilometers_public_transport,
            merge_kilometers_public_transport,
            "Kilometers Public Transport (OPP-080-Tender)",
        ),
        (
            parse_previous_notice_identifier,
            merge_previous_notice_identifier,
            "Previous notice Identifier (OPP-090-procedure)",
        ),
        (
            parse_provided_service_type,
            merge_provided_service_type,
            "Provided Service Type (OPT-030-procedure-sprovider)",
        ),
        (
            parse_quality_target_code,
            merge_quality_target_code,
            "Quality Target Code (OPT-071-Lot)",
        ),
        (
            parse_quality_target_description,
            merge_quality_target_description,
            "Quality Target Description (OPT-072-Lot)",
        ),
        (
            parse_framework_notice_identifier,
            merge_framework_notice_identifier,
            "Framework notice Identifier (OPT-100-Contract)",
        ),
        (
            parse_fiscal_legislation_url,
            merge_fiscal_legislation_url,
            "URL to Fiscal Legislation (OPT-110-Lot-FiscalLegis)",
        ),
        (
            parse_part_fiscal_legislation_url,
            merge_part_fiscal_legislation_url,
            "URL to Fiscal Legislation (OPT-110-Part-FiscalLegis)",
        ),
        (
            parse_fiscal_legislation_document_id,
            merge_fiscal_legislation_document_id,
            "Fiscal Legislation Document ID (OPT-111-Lot-FiscalLegis)",
        ),
        (
            parse_part_fiscal_legislation_document_id,
            merge_part_fiscal_legislation_document_id,
            "Fiscal Legislation Document ID (OPT-111-Part-FiscalLegis)",
        ),
        (
            parse_environmental_legislation_document_id,
            merge_environmental_legislation_document_id,
            "Environmental Legislation Document ID (OPT-112-Lot-EnvironLegis)",
        ),
        (
            parse_part_environmental_legislation_document_id,
            merge_part_environmental_legislation_document_id,
            "Environmental Legislation Document ID (OPT-112-Part-EnvironLegis)",
        ),
        (
            parse_employment_legislation_document_id,
            merge_employment_legislation_document_id,
            "Employment Legislation Document ID (OPT-113-Lot-EmployLegis)",
        ),
        (
            parse_part_employment_legislation_document_id,
            merge_part_employment_legislation_document_id,
            "Employment Legislation Document ID (OPT-113-Part-EmployLegis)",
        ),
        (
            parse_environmental_legislation_url_part,
            merge_environmental_legislation_url_part,
            "Environmental Legislation URL for Parts (OPT-120-Part-EnvironLegis)",
        ),
        (
            parse_environmental_legislation_url,
            merge_environmental_legislation_url,
            "Environmental Legislation URL (OPT-120-Lot-EnvironLegis)",
        ),
        (
            parse_employment_legislation_url,
            merge_employment_legislation_url,
            "Employment Legislation URL (OPT-130-Lot-EmployLegis)",
        ),
        (
            parse_employment_legislation_url_part,
            merge_employment_legislation_url_part,
            "Employment Legislation URL for Parts (OPT-130-Part-EmployLegis)",
        ),
        (
            parse_procurement_documents_id,
            merge_procurement_documents_id,
            "Procurement Documents ID (OPT-140-Lot)",
        ),
        (
            parse_procurement_documents_id_part,
            merge_procurement_documents_id_part,
            "Procurement Documents ID for Parts (OPT-140-Part)",
        ),
        (
            parse_vehicle_type,
            merge_vehicle_type,
            "Vehicle Type (OPT-155-LotResult)",
        ),
        (
            parse_vehicle_numeric,
            merge_vehicle_numeric,
            "Vehicle Numeric (OPT-156-LotResult)",
        ),
        (
            parse_ubo_firstname,
            merge_ubo_firstname,
            "UBO First Name (OPT-160-UBO)",
        ),
        (
            parse_tendering_party_leader,
            merge_tendering_party_leader,
            "Tendering party Leader (OPT-170-Tenderer)",
        ),
        (
            parse_organization_technical_identifier,
            merge_organization_technical_identifier,
            "organization Technical Identifier (OPT-200-organization-company)",
        ),
        (
            parse_touchpoint_technical_identifier,
            merge_touchpoint_technical_identifier,
            "touchpoint Technical Identifier (OPT-201-organization-touchpoint)",
        ),
        (
            parse_beneficial_owner_identifier,
            merge_beneficial_owner_identifier,
            "Beneficial Owner Technical Identifier (OPT-202-UBO)",
        ),
        (
            parse_signatory_identifier_reference,
            merge_signatory_identifier_reference,
            "Signatory Identifier Reference (OPT-300-Contract-Signatory)",
        ),
        (
            parse_buyer_technical_identifier,
            merge_buyer_technical_identifier,
            "Buyer Technical Identifier Reference (OPT-300-Procedure-Buyer)",
        ),
        (
            parse_service_provider_identifier,
            merge_service_provider_identifier,
            "Service Provider Technical Identifier Reference (OPT-300-Procedure-SProvider)",
        ),
        (
            parse_additional_info_provider,
            merge_additional_info_provider,
            "Additional Info Provider Technical Identifier Reference (OPT-301-Lot-AddInfo)",
        ),
        (
            parse_document_provider,
            merge_document_provider,
            "Document Provider Technical Identifier Reference (OPT-301-Lot-DocProvider)",
        ),
        (
            parse_employment_legislation_org,
            merge_employment_legislation_org,
            "Employment Legislation Organization Technical Identifier Reference (OPT-301-Lot-EmployLegis)",
        ),
        (
            parse_environmental_legislation_org,
            merge_environmental_legislation_org,
            "Environmental Legislation Organization Technical Identifier Reference (OPT-301-Lot-EnvironLegis)",
        ),
        (
            parse_fiscal_legislation_org,
            merge_fiscal_legislation_org,
            "Fiscal Legislation Organization Technical Identifier Reference (OPT-301-Lot-FiscalLegis)",
        ),
        (
            parse_review_info_provider_identifier,
            merge_review_info_provider_identifier,
            "Review Info Provider Technical Identifier Reference (OPT-301-Lot-ReviewInfo)",
        ),
        (
            parse_mediator_technical_identifier,
            merge_mediator_technical_identifier,
            "Mediator Technical Identifier Reference (OPT-301-Lot-Mediator)",
        ),
        (
            parse_review_organization_identifier,
            merge_review_organization_identifier,
            "Review Organization Technical Identifier Reference (OPT-301-Lot-ReviewOrg)",
        ),
        (
            parse_tender_evaluator,
            merge_tender_evaluator,
            "Tender Evaluator Technical Identifier Reference (OPT-301-Lot-TenderEval)",
        ),
        (
            parse_tender_recipient,
            merge_tender_recipient,
            "Tender Recipient Technical Identifier Reference (OPT-301-Lot-TenderReceipt)",
        ),
        (
            parse_financing_party,
            merge_financing_party,
            "Financing Party (ID reference) (OPT-301-LotResult-Financing)",
        ),
        (
            parse_payer_party,
            merge_payer_party,
            "Payer Party (ID reference) (OPT-301-LotResult-Paying)",
        ),
        (
            part_parse_additional_info_provider,
            part_merge_additional_info_provider,
            "Additional Info Provider (OPT-301-Part-AddInfo)",
        ),
        (
            part_parse_document_provider,
            part_merge_document_provider,
            "Document Provider (OPT-301-Part-DocProvider)",
        ),
        (
            part_parse_employment_legislation_org_reference,
            part_merge_employment_legislation_org_reference,
            "Employment Legislation (OPT-301-Part-EmployLegis)",
        ),
        (
            parse_environmental_legislation_org_reference,
            merge_environmental_legislation_org_reference,
            "Environmental Legislation Organization Reference (OPT-301-Part-EnvironLegis)",
        ),
        (
            parse_fiscal_legislation_org_reference,
            merge_fiscal_legislation_org_reference,
            "Fiscal Legislation Organization Reference (OPT-301-Part-FiscalLegis)",
        ),
        (
            part_parse_mediator,
            part_merge_mediator,
            "Mediator (OPT-301-Part-Mediator)",
        ),
        (
            part_parse_review_info_provider,
            part_merge_review_info_provider,
            "Review Info Provider (OPT-301-Part-ReviewInfo)",
        ),
        (
            part_parse_review_organization,
            part_merge_review_organization,
            "Review Organization (OPT-301-Part-ReviewOrg)",
        ),
        (
            part_parse_tender_evaluator,
            part_merge_tender_evaluator,
            "Tender Evaluator (OPT-301-Part-TenderEval)",
        ),
        (
            part_parse_tender_recipient,
            part_merge_tender_recipient,
            "Tender Recipient (OPT-301-Part-TenderReceipt)",
        ),
        (
            parse_main_contractor,
            merge_main_contractor,
            "Main Contractor (OPT-301-Tenderer-MainCont)",
        ),
        (
            parse_subcontractor,
            merge_subcontractor,
            "Subcontractor (OPT-301-Tenderer-SubCont)",
        ),
        (
            parse_beneficial_owner_reference,
            merge_beneficial_owner_reference,
            "Beneficial Owner Reference (OPT-302-organization)",
        ),
        (
            parse_tendering_party_id_reference,
            merge_tendering_party_id_reference,
            "Tendering party ID Reference (OPT-310-Tender)",
        ),
        (
            parse_contract_identifier_reference,
            merge_contract_identifier_reference,
            "Contract Identifier Reference (OPT-315-LotResult)",
        ),
        (
            parse_contract_technical_identifier,
            merge_contract_technical_identifier,
            "Contract Technical Identifier (OPT-316-Contract)",
        ),
        (
            parse_tender_identifier_reference,
            merge_tender_identifier_reference,
            "Tender Identifier Reference (OPT-320-LotResult)",
        ),
        (
            parse_tender_technical_identifier,
            merge_tender_technical_identifier,
            "Tender Technical Identifier (OPT-321-Tender)",
        ),
        (
            parse_lotresult_technical_identifier,
            merge_lotresult_technical_identifier,
            "LotResult Technical Identifier (OPT-322-LotResult)",
        ),
    ]

    for parse_func, merge_func, section_name in bt_sections:
        process_bt_section(
            release_json, xml_content, [parse_func], merge_func, section_name
        )

    # Add UBO fax processing
    process_bt_section(
        release_json, xml_content, [parse_ubo_fax], merge_ubo_fax, "UBO fax"
    )
