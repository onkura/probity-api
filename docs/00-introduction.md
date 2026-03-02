# Introduction

## The Problem

Autonomous systems now perform actions with real-world consequences.

After an incident, organizations attempt to answer:

- Why did the system act?
- What information did it rely on?
- Was the action expected from its inputs?

Traditional observability systems record execution events.  
They rarely preserve decision context.

As systems become non-deterministic, replaying events no longer explains decisions.

A new primitive is required: preserved decision state.

---

## The Probity Approach

Probity defines a record representing the moment a system commits from reasoning into consequence.

The record captures:

- decision context
- responsibility attribution
- committed action
- observed outcome
- integrity evidence

The record is created once and interpreted later.

Probity does not judge decisions.  
Probity preserves the conditions under which they occurred.

---

## Evidence, Not Assertion

A Probity record is historical evidence.

It describes what the system believed at the time of action.

It does not certify correctness, permission, or compliance.

Interpretation remains a human responsibility.

---

## Design Principles

### Minimal Sufficiency
Records contain enough information to reconstruct the decision environment, not reproduce computation.

### Independence
Records remain interpretable without the original runtime system.

### Non-Determinism Compatibility
Different future behavior does not invalidate past records.

### Attribution Over Authorization
Records attribute responsibility; they do not grant permission.

---

## Structure of This Documentation

The documentation is divided into layers:

- Conceptual — meaning of a record
- Behavioral — lifecycle of records
- Trust — integrity guarantees
- Operational — investigation usage

Each layer builds on the previous one.