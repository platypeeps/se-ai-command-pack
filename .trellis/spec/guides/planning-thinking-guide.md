# Planning Thinking Guide

> **Purpose**: Stop and think before a multi-file change - is the plan
> actually executable, and do you know what it touches?

---

## The Problem

**Most plan failures are scope failures, not execution failures.**

A plan that looks complete and turns out wrong usually has one of three
holes in it:

- Nobody enumerated what the change touches, so a caller nobody listed
  breaks
- The steps cannot be verified independently, so "done" is a judgement
  call instead of a check
- There is no named point to roll back to, so a partial failure leaves
  the tree in a state nobody designed

These questions surface those holes while they are still cheap.

---

## Before Writing `prd.md`

### Scope interview

Answer these in writing, in the PRD, not in your head:

- [ ] What is explicitly **in** scope? Name the deliverables.
- [ ] What is explicitly **out** of scope? Name the tempting adjacent
      work you are declining.
- [ ] What would make this task **not worth doing**? If nothing would,
      the requirements are not falsifiable yet.
- [ ] Who or what consumes the result? A fleet-wide product change and a
      repo-local fix have different blast radii.

### Blast radius enumeration

**Enumerate before editing, from the filesystem or the database - never
from memory.** A list built from what you already know cannot contain
what you did not know about.

- [ ] Every file that **writes** the name, value, or contract you are
      changing
- [ ] Every file that **reads** it - including other repositories when
      the thing is shared
- [ ] Every **inventory** that recites it: catalogs, manifests, docs
      that list what exists, generated surfaces
- [ ] Every **derived store**: an index, a cache, a snapshot, a lock
      file that was computed from the thing you are correcting

```bash
# The passing form enumerates. This finds what you did not think to open:
grep -rn "the_thing" .
ls the/directory/
```

If your check only covers the files you edited, it is scoped to the
wrong thing. Scope it to the blast radius.

---

## Before Writing `design.md`

- [ ] Which **decision** does this design actually make? A design that
      records no rejected alternative recorded no decision.
- [ ] What is the **compatibility** story - what breaks for an existing
      consumer, and is that acceptable?
- [ ] What is the **failure mode** if this design is wrong? Cheap and
      loud, or silent and expensive?
- [ ] Does any **value** in this design (a count, a path, an identifier)
      also appear in `prd.md`? They must agree, and they drift silently.

---

## Before Writing `implement.md`

### Plan-quality probes

- [ ] Is every step **independently verifiable**? Name the command and
      the result that means failure, not "check it works."
- [ ] Does each step name its **rollback point**? "Revert this file
      alone" is a rollback point; "undo the change" is not.
- [ ] Is the **ordering** forced by real dependencies, or is it just the
      order you thought of things? Forced ordering belongs in the plan;
      incidental ordering is noise.
- [ ] Where a step is **expected to fail** partway through the sequence
      (a generator that cannot pass until later files exist), say so and
      describe the expected failure shape. Otherwise the next reader
      treats a healthy intermediate state as a defect.

### Delegation inventory

- [ ] Which steps could run in **parallel**, and do they share mutable
      state? Same files or same metadata store means one lane, serial.
- [ ] Which steps need **isolation** because they write? A writer gets
      its own worktree or returns a patch; two writers never share a
      checkout.
- [ ] What is each delegated step's **budget and return contract**? A
      step with no deadline and no defined result cannot fail visibly.

---

## Quick Reference: Planning Triggers

Reach for this guide when:

- [ ] The change spans **3 or more files**
- [ ] You are renaming or replacing a **name** that other code reads
- [ ] You are swapping a **tool, library, or transport** - remember that
      three things change: what it is called, what authorizes it, and
      what it can do
- [ ] You are adding or removing something that **gets listed** somewhere
- [ ] You are correcting a **stored fact** that other stores derive from
- [ ] You are about to delegate work to **parallel workers**

---

## Relationship to the Trellis Phases

This guide feeds the planning artifacts; it does not decide when
planning starts. The Trellis workflow owns that: Phase 1 classifies the
request, and a complex task needs `prd.md`, `design.md`, and
`implement.md` before `task.py start`. Use these questions while writing
those artifacts, and again at the planning convergence boundary before
requesting implementation approval.

---

**Core Principle**: A plan you cannot falsify is a wish with a checklist.
