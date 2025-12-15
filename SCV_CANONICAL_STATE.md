\# SCV – Canonical State (DO NOT GUESS)



\## Ground truth

\- A BFF / SCV composition layer EXISTS (see backend\_v2)

\- The frontend UI is written to expect a composed SCV profile

\- Blank panels are NOT a frontend bug

\- Blank panels occur because the running profile endpoint is thin



\## Canonical backend

\- Canonical backend: backend\_v2

\- Key file: backend\_v2/app/main.py

\- SCV composition logic exists here and must be used



\## Canonical profile contract

\- There must be ONE canonical SCV profile endpoint

\- That endpoint must return:

&nbsp; - client

&nbsp; - accounts

&nbsp; - match\_decisions

&nbsp; - trade\_history

&nbsp; - audit\_trail

&nbsp; - regulatory\_enrichment

&nbsp; - evidence\_artefacts

\- Keys must exist even when empty



\## Current mismatch (known issue)

\- Frontend currently calls a thin profile endpoint

\- BFF composition is NOT wired into that endpoint at runtime

\- This is the reason panels are blank



\## Agreed direction (locked)

\- Do NOT redesign frontend

\- Do NOT abandon the BFF

\- Wire the existing BFF / SCV composition into the canonical profile endpoint

\- Incrementally enrich via stories and MissionLog



\## Next concrete step (when resuming)

\- Identify the canonical SCV profile endpoint exposed by backend\_v2

\- Ensure frontend calls that endpoint

\- Or ensure that endpoint delegates to BFF composition internally

\- Start with ONE section (trade history) and prove end-to-end



