# Skript Runtime Testing Framework

## Overview

## Compatibility with Skript Native Tests

This framework **is compatible** with Skript’s native **quickTest** and **test-action** systems, but with important limitations.

### What Actually Happens

When using Skript’s native test suite:

* Skript’s own `test` event **overrides** the framework’s `skriptTest` event
* Only features that exist in Skript’s native test environment are available
* Framework-specific extensions become unavailable

As a result:

* Core assertions such as:

```skript
assert <condition>
```

remain usable

* Framework-specific features such as:

```skript
stop auto test execution here
```

are **not usable** under quickTest or native `test-action`

* Extended event-values (`event-test`, autorun flag, script scoping) may be missing or incomplete

### Mitigation Strategy

To regain full framework behavior, simply **prefix your existing test with `devdinc`**:

```skript
devdinc test "<name>"
```

This forces execution through the framework’s custom event pipeline and restores:

* Full event-values
* Autorun vs manual execution control
* Reflection-backed features

### Recommendation

* **Prefer Skript’s native test suite when possible** for maximum compatibility
* Use `devdinc test` only when you need:

  * Script scoping
    n  * Autorun control
  * Parser / log inspection
  * Extended lifecycle hooks

---

This document describes a **runtime testing framework for Skript** implemented entirely in Skript using **custom events, reflection, and controlled parser interaction**.

The framework is designed to mirror key aspects of Skript’s internal development test suite while remaining:

* Safe to execute at runtime
* Deterministic and event-driven
* Compatible with production servers
* Capable of testing **syntax, parsing, and runtime behavior**

All framework state is stored under the namespace:

```
-test.sk::*
```

---

## Design Goals

The framework is intentionally strict and explicit.

It aims to:

* Allow tests to be written directly in `.sk` files
* Associate tests **with the script they originate from**
* Support both **automatic (autorun)** and **manual** execution paths
* Provide before/after hooks at both **per-test** and **per-script** levels
* Prevent state leakage between tests
* Enable parser-level testing via reflection

---

## High-Level Architecture

The framework is built around the following principles:

1. **Tests are custom events** (`skriptTest`)
2. **Tests are registered at parse time**
3. **Execution is scheduled, not inline** (scheduler + proxy Runnable)
4. **Each test is scoped to its source script**
5. **Failures are tracked per test, per script**

Execution is fully event-driven and never relies on direct control flow from the script loader.

---

## Test Definition

### Syntax

```skript
devdinc test "<test name>" [when <condition>]:
    <test body>
```

* Tests are registered automatically during parsing
* `when <condition>` is evaluated immediately before execution
* Each test is associated with its **originating script**

---

### Syntax

```skript
devdinc test "<test name>" [when <condition>]:
    <test body>
```

* Tests are registered automatically during parsing
* `when <condition>` is evaluated immediately before execution
* Each test is associated with its **originating script**

---

## Test Identity & Scoping

Each test is uniquely identified by **both its name and its source script**.

Internal representation:

```
[event-string, event-script]
```

This ensures:

* No collisions between scripts
* Deterministic execution order
* Correct isolation and error attribution

---

Internally, each test is stored as a **pair**:

```
[<test name>, <script>]
```

This enables:

* Multiple scripts defining tests with identical names
* Script-scoped test execution
* Accurate isolation and error tracking

---

## Test Registration (Parse-Time)

Tests are registered during the **parse phase**, not execution.

Registration format:

```
-test.sk::tests::<script>::<test name> = [<test name>, <script>]
```

A hidden sentinel test is used during load to guarantee full registration before autorun begins.

---

## Running Tests

### Automatic Execution (Autorun)

On script load:

1. Global test state is cleared
2. A sentinel test establishes autorun context
3. All tests across all scripts are discovered
4. Tests are executed in load order

Autorun tests receive:

```
event-boolean = true
```

---

### Manual Execution

```skript
run test(s) %objects%
```

* Accepts one or more `[test name, script]` objects
* Runs tests with:

```
event-boolean = false
```

* Autorun-only tests may opt out (see below)

---

## Test Discovery

### Expression

```skript
all tests [with test name %-string%] [[in] %-script%]
```

### Behavior

* No arguments → all tests from all scripts
* `with test name` → exact match
* `in <script>` → restricts to a single script

Return type:

```
[test name, script]
```

---

## Assertions

Assertions validate runtime conditions and record failures.

### Syntax

```skript
assert true: <condition>
assert false: <condition>
assert <condition> to fail
```

### Modifiers

* `without halting` – records failure but continues
* `with error message "<msg>"` – prints formatted output
* `with no error message` – suppresses console output

Assertions are only valid inside `skriptTest`.

---

## Explicit Failure

```skript
fail test
fail test with error message "<msg>"
```

* Records a failure immediately
* Halts execution unless `without halting` is used

---

## Error Tracking

Errors are tracked per **test + script**:

```
-test.sk::errors::<script>::<test name>::*
```

### Expression

```skript
test errors [for %-objects%]
```

* Without arguments → current test
* With objects → aggregated errors

Errors are cleared before each test and never leak.

---

## Event Values (Complete Reference)

Every test and lifecycle hook executed by this framework exposes the following **event-values**:

| Event Value     | Type    | Meaning                        |
| --------------- | ------- | ------------------------------ |
| `event-string`  | string  | Test name                      |
| `event-script`  | script  | Script that defines the test   |
| `event-boolean` | boolean | Autorun flag                   |
| `event-test`    | object  | `[event-string, event-script]` |

### Availability

* All values are guaranteed when using `devdinc test`
* Under Skript native tests, availability depends on Skript’s test runner

---

---------------|----------|--------|
| `event-string`   | string   | Test name |
| `event-script`   | script   | Originating script |
| `event-boolean`  | boolean  | Autorun flag |
| `event-test`     | object   | `[event-string, event-script]` |

These values are **guaranteed** only when using `devdinc test`.

They are **undefined** when running via quickTest or native test-action.

---

## Autorun Semantics

### Autorun Flag

```skript
event-test is autorun
event-test is not autorun
```

* `true` during load-time execution
* `false` during manual execution

The flag is immutable and scoped to the test event.

---

### Stopping Autorun Execution

```skript
stop auto test execution here
```

* Halts the current test **only if** autorun is active
* No effect during manual execution

Typical usage:

```skript
if event-test is autorun:
    stop auto test execution here
```

---

## Test Lifecycle Hooks

The framework provides structured lifecycle hooks that integrate with both framework and native execution.

### Hooks

```skript
before each test
after each test
before all tests
after all tests
```

### `event-script` Usage

Inside **all** lifecycle hooks, `event-script` refers to:

> **The script whose tests are currently executing**

Examples:

```skript
before all tests:
    broadcast "Running tests for %event-script%"

after each test:
    delete {-tmp::%event-script%::*}
```

This allows:

* Per-script setup and teardown
* Shared resources scoped to a script
* Accurate cleanup even when multiple scripts define tests

### Execution Semantics

* `before all tests` / `after all tests` run **once per script**
* `before each test` / `after each test` run **per test**, with `event-string` set

---

## Parser & Syntax Testing (Reflection)

The framework supports **parser-level testing** using reflection.

### Parse Section

```skript
parse:
    <skript code>
```

* Uses `ParserInstance` to parse nodes
* Does not execute code
* Fully restores parser state afterward

### Log Capture

```skript
last parse logs
```

* Captures `SkriptLogger` output
* Enables assertions against expected parser errors

---

## Native TestTracker Integration (Experimental)

Failures are forwarded to Skript’s internal `TestTracker`.

### Implications

* Native reporting tools can observe results
* CI-style environments can consume output

### Limitations

* Experimental and version-dependent
* No compatibility guarantees

You **must** use:

```skript
devdinc test "<name>"
```

Native `test` syntax is not supported.

---

## Test Environment Utilities

The framework provides controlled fixtures:

* `test-world` – `skripttest` or fallback world
* `test-location` – fixed offset location
* `test-block` – temporary block (auto-restored)
* `test-offline-player` – generated offline player

These utilities guarantee cleanup after each test.

---

## World Isolation Policy

### Default

* World state is **shared** across tests
* This is intentional for performance and safety

### Opt-In Isolation

Users may implement isolation manually via hooks:

```skript
before each test:
    # snapshot world

after each test:
    # restore world
```

No built-in snapshotting is provided.

---

## Console Output

Failures are printed as:

```
[Skript] [TEST FAILURE] <test name> <optional message>
```

Output is suppressed when `with no error message` is used.

---

## Guarantees

The framework guarantees:

* Deterministic registration and execution
* Script-scoped test isolation
* No state leakage between tests
* Reliable autorun vs manual distinction
* Parser state is always restored

---

## Non-Public Implementation Details

The following must not be relied upon:

* Sentinel test mechanics
* Internal variable layout
* Scheduler timing assumptions
* Reflection internals

These may change without notice.

---

## Reflection Disclaimer

Reflection is used for:

* `ParserInstance` manipulation
* Condition parsing
* Log capture
* Native `TestTracker` forwarding

### Guarantees

* All reflected state is backed up and restored
* No permanent mutation of Skript internals

### Non-Guarantees

* Binary compatibility across versions
* Stability under obfuscation
* Support on modified Skript forks

Reflection-backed features are **best-effort** and may degrade gracefully.

