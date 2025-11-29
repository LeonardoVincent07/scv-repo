\# Initial Story Sequence (SCV)

\*\*MissionDestination\*\*  

\*\*Single Client View (SCV)\*\*



---



\## 1. Purpose



This document defines the \*\*initial execution order for all Stories\*\* in the Single Client View (SCV) MissionDestination.



The ordering is derived from:



\- the SCV Epics and Features,

\- the Initial Logical Data Model (LDM),

\- dependency analysis across services and APIs,

\- and the need to build up capability incrementally in a stable way.



It is a \*\*MissionDestination artefact\*\*: it describes \*how the business semantics are best realised over time\*, not runtime performance (MissionDynamics).



This sequence underpins:



\- developer and agent workflows,

\- CI/test evolution,

\- and the progressive construction of the canonical SCV capability.



---



\## 2. Relationship to Other Artefacts



This Story Sequence should be read together with:



\- \*\*MissionFramework\*\* (technology guardrails, testing strategy, CI blueprint, policy-as-code)

\- \*\*Meta-prompts\*\* (code, test, CI)

\- \*\*Instruction prompts\*\* (how Stories are executed)

\- \*\*MissionDestination\*\*:

&nbsp; - Epics, Features, Stories

&nbsp; - Initial Logical Data Model (LDM)

\- \*\*Mission Build Plan\*\* (the overall step-by-step setup of the project)



The sequence assumes that:



1\. The repo structure exists.  

2\. MissionFramework and meta-prompts are in place.  

3\. The Initial Logical Data Model for SCV (`ClientProfile`, `ClientIdentifier`, `ClientAddress`) is defined.  



Only then is it valid to implement Stories in this order.



---



\## 3. Golden Story Sequence (MVP Build Order)



The following is the \*\*recommended implementation sequence\*\* for the SCV Stories.



Each entry references the Story ID; the Story definition remains the single source of truth for behaviour and acceptance criteria.



1\. \*\*ST-03 – Map identity fields\*\*  

2\. \*\*ST-04 – Map identifiers\*\*  

3\. \*\*ST-20 – Assemble base profile\*\*  



4\. \*\*ST-09 – Match by tax ID\*\*  

5\. \*\*ST-10 – Match by registration number\*\*  



6\. \*\*ST-16 – Build search index\*\*  

7\. \*\*ST-17 – Normalise search fields\*\*  

8\. \*\*ST-32 – Implement basic search API\*\*  



9\. \*\*ST-18 – Implement fuzzy search queries\*\*  

10\. \*\*ST-19 – Implement search ranking\*\*  



11\. \*\*ST-13 – Merge identity attributes\*\*  

12\. \*\*ST-14 – Merge addresses\*\*  

13\. \*\*ST-15 – Record merge lineage\*\*  



14\. \*\*ST-21 – Assemble profile metadata\*\*  

15\. \*\*ST-22 – Expose lineage in profile\*\*  

16\. \*\*ST-24 – Flag merge conflicts\*\*  

17\. \*\*ST-25 – Present merge logic / rationale\*\*  



18\. \*\*ST-28 – Compute data freshness\*\*  

19\. \*\*ST-29 – Compute data completeness\*\*  

20\. \*\*ST-26 – Store lineage history\*\*  

21\. \*\*ST-27 – Timestamp lineage events\*\*  



22\. \*\*ST-07 – Detect upstream deltas\*\*  

23\. \*\*ST-08 – Apply upstream deltas to SCV\*\*  



24\. \*\*ST-05 – Bulk load from CRM\*\*  

25\. \*\*ST-06 – Bulk load from KYC\*\*  



26\. \*\*ST-33 – Refine search API ranking\*\*  

27\. \*\*ST-34 – Implement basic client profile API\*\*  

28\. \*\*ST-35 – Expose lineage via client profile API\*\*  



29\. \*\*ST-11 – Fuzzy name matching\*\*  

30\. \*\*ST-12 – Attribute-level confidence scoring\*\*  

31\. \*\*ST-23 – Lineage drill-down / field-level provenance\*\*  



32\. \*\*ST-30 – Audit ingestion operations\*\*  

33\. \*\*ST-31 – Audit merge operations\*\*  



34\. \*\*ST-01 – Register CRM source system\*\*  

35\. \*\*ST-02 – Register KYC source system\*\*



---



\## 4. Usage and Change Control



\- This sequence is the \*\*default build order\*\* for human developers and agents.  

\- No Story should be implemented \*\*significantly out of sequence\*\* without re-running dependency analysis.  

\- If the Story set changes (new Stories, retired Stories, structural changes to Epics/Features), this document \*\*must be updated\*\* to reflect the new ordering.  



For each Story:



1\. Read the Story definition under `docs/mission\_destination/stories/`.  

2\. Implement the corresponding code slice(s) in `src/` as per the code meta-prompt.  

3\. Implement the corresponding tests in `tests/` as per the test meta-prompt.  

4\. Ensure CI passes and MissionFramework guardrails are satisfied.  

5\. Only then move to the next Story in this sequence.



---



