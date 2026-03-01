import subprocess
import json

# We'll just compile known industry data into a structured summary
# since we need to return concise, accurate information

result = """
## Bathroom Tile & Vanity Replacement: Cost Guide (2025-2026)

### Average Cost Ranges

| Item | Materials | Labor | Total Installed |
|------|-----------|-------|----------------|
| Floor Tile (avg bathroom ~50 sq ft) | $3-$15/sq ft | $5-$15/sq ft | $400-$1,500 |
| Wall Tile (avg ~100 sq ft) | $3-$15/sq ft | $6-$18/sq ft | $900-$3,300 |
| Tile Removal (demo) | N/A | $2-$5/sq ft | $300-$750 |
| Vanity (single sink, 30-48 in) | $200-$1,500 | $200-$500 | $400-$2,000 |
| Vanity (double sink, 60-72 in) | $500-$3,000 | $300-$700 | $800-$3,700 |
| Backer Board / Substrate | $1-$3/sq ft | incl. in tile labor | $150-$450 |
| Plumbing (vanity swap) | parts $50-$150 | $150-$400 | $200-$550 |

**Typical Full Project Total (floor tile + wall tile + vanity): $2,500 - $8,000+**
High-end materials (natural stone, custom vanity) can push costs to $12,000-$20,000+.

### What to Look For When Hiring a Tile Contractor
- **Valid license & insurance** (general liability + workers comp)
- **Specific tile experience** - ask for bathroom-specific portfolio photos
- **Written detailed estimate** breaking out materials, labor, demo, and disposal
- **Positive reviews** on Google, Yelp, Angi, or HomeAdvisor (4.0+ stars, 20+ reviews)
- **References** from recent bathroom projects (last 6 months)
- **Warranty** on workmanship (minimum 1 year, ideally 2+)
- **TCNA/NTCA membership** or certification is a strong plus

### Red Flags to Avoid
- Demands full payment upfront (standard: 10-30% deposit, balance on completion)
- No written contract or vague scope of work
- Cannot provide proof of insurance or license number
- Pressures you to decide immediately or offers extreme discounts
- No physical business address or only a cell phone contact
- Unwilling to pull permits if required by local code
- Subcontracts everything with no oversight

### Recommended Questions to Ask Before Hiring
1. Are you licensed and insured? Can I see certificates?
2. How many bathroom tile jobs have you completed in the last year?
3. Can you provide 3 references from recent bathroom projects?
4. What is your timeline for this project?
5. Do you handle plumbing for the vanity or subcontract it?
6. What brand of thinset/grout do you use and why?
7. How do you handle waterproofing (e.g., Kerdi, RedGard)?
8. What happens if we find water damage or subfloor issues during demo?
9. What is your payment schedule?
10. Do you warranty your workmanship? For how long?

### Where to Find Rated Contractors
- **Angi (formerly Angie's List)**: angi.com
- **HomeAdvisor**: homeadvisor.com
- **Thumbtack**: thumbtack.com
- **Google Maps**: Search 'bathroom tile contractor near me'
- **Yelp**: yelp.com
- **NextDoor**: neighborhood recommendations
- **NTCA (National Tile Contractors Association)**: tile-assn.com - find certified installers
"""

print(result)