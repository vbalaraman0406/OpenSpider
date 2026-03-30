import os

last_check_file = 'workspace/memory/trump_truth_social_last_check.md'
os.makedirs('workspace/memory', exist_ok=True)

with open(last_check_file, 'w') as f:
    f.write("""# Trump Truth Social - Last Check
## Checked at: 2026-03-20 19:56 PDT

### Recent Posts Found (carried forward from previous checks):

1. **~5:21 PM PDT** - Trump says US considering "winding down" military efforts/war in Iran, but says other nations must guard Strait of Hormuz
2. **~5:07 PM PDT** - Trump says no ceasefire as Khamenei issues defiant message; references ongoing military operations
3. **~4:26 PM PDT** - Trump declared US-Israeli war on Iran "Militarily WON" on Truth Social
4. **~3:26 PM PDT** - Trump posted on Truth Social about "getting very close to meeting our" objectives regarding Iran
5. **~3:00 PM PDT** - Post about Strait of Hormuz threat and other nations needing to protect it
6. **~3:00 PM PDT** - Post referencing Israel striking South Pars Gas Field

### Content Hashes (for dedup):
- winding_down_iran_strait_of_hormuz
- no_ceasefire_khamenei_defiant
- militarily_won_iran
- getting_very_close_objectives
- strait_of_hormuz_other_nations
- south_pars_gas_field

### Status: No new posts detected in 19:26-19:56 PM PDT window.
""")

print('Last check file updated with correct data.')
