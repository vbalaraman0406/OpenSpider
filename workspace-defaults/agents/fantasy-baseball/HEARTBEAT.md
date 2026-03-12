# HEARTBEAT: Baseball Optimization Loop

- **Interval**: 1 hour
- **Active Hours**: 08:00 - 22:00 (Your local time)
- **Routine**:
  1. `browser` open: https://baseball.fantasysports.yahoo.com/
  2. Scrape "My Team" for status updates.
  3. Cross-reference with `rotowire.com/baseball/daily-lineups.php`.
  4. **Action**: If mismatch found, navigate to Yahoo and "Edit Lineup".
  5. **Alert**: send_whatsapp "Lineup Updated: Swapped [Player A] for [Player B] due to [Reason]."
