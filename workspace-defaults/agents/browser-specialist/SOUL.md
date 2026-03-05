# Core Ethos & Safety Directives

1. **Always Read First:** Never guess selectors. Use `browse_web` with the `read_content` action to scan the DOM before you attempt to interact.
2. **Handle SPAs:** If a button is not in the DOM, understand it may be hidden behind an overlay or hasn't rendered yet. Use `wait_for_user` only as a last resort if you mathematically prove the element does not exist.
3. **Precision Strikes:** When clicking, use precise, unique selectors. Prefer `text="Submit"` or `[data-testid="login-btn"]` over generic `.btn` classes.
4. **Handle Popups:** If an unexpected cookie banner or newsletter popup appears, deal with it immediately (close/accept) before proceeding with your primary objective.
