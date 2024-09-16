indicator = "flexible_work"
action_map = {
            "flexible_work": "action_validate_flexible_work",
            "applied_context": "action_validate_applied_context_form",
            "eligibility_criteria": "action_validate_eligibility_criteria"
        }
folowupaction = action_map[indicator]
print(f"follow up action - {folowupaction}")