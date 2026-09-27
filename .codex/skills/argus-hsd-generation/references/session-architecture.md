# HSD Session Architecture

## Control session

The control session owns the HSD-wide TOC, chapter purposes, reader journey,
chapter boundaries, cross-reference policy, duplication control, terminology,
granularity, representation policy, Chapter Contracts, and final consistency
review. It does not mass-produce section bodies.

## Major-chapter writer session

Start one fresh LLM writer session per major chapter. All child sections of that
chapter share the session so their narrative and visual placement remain
coherent. End the session before starting the next major chapter.

Only the approved global structure, the target Chapter Contract, writer rules,
approved terminology/reference rules, and explicitly allowed cross-reference
metadata cross a chapter-session boundary. Conversation history and previous
chapter text do not cross it.

The writer creates a Human Structure Plan before prose. Subsections, prose,
tables, and diagrams follow semantic need. Python validates but never constructs
the plan or Human-facing text. Missing support returns `CONTEXT_INSUFFICIENT`.

This is currently a Human-operated orchestration requirement. A different
session ID records intended separation but does not prove fresh context or
previous-context isolation. Session-creation provenance and isolation evidence
remain explicit work for the future real-LLM harness.
