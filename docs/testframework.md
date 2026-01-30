# Skript Runtime Testing Framework

## Overview

This document describes a **self-contained runtime testing framework for Skript**. The framework replicates much of Skript’s internal development test suite while extending it with runtime-safe execution, reflection-based inspection, and deterministic event-driven control.

Unlike Skript’s native internal tests, this framework:

* Runs entirely at runtime
* Is safe for production servers
* Supports both **automatic (autorun)** and **manual** execution
* Tracks failures centrally with optional console suppression

All framework state is stored under the `-test.sk::*` namespace.

---

## Design Goals

The framework is intentionally minimal and predictable.

It is designed to:

* Allow tests to be written directly in `.sk` files
* Achieve functional parity with Skript’s internal test actions where feasible
* Enable meta-testing of Skript syntax and parser behavior
* Support fail-fast behavior with optional non-halting assertions
* Prevent state leakage between tests

---

## Feature Parity with Skript’s Native Test Suite

| Feature                   | Status       | Description                                           |
| ------------------------- | ------------ | ----------------------------------------------------- |
| **Test structure**        | Achieved     | `test %string%` mirrors native test declarations      |
| **Conditional execution** | Achieved     | `when <condition>` skips tests dynamically            |
| **Assertions**            | Achieved     | `assert <condition>` and `assert <condition> to fail` |
| **Explicit failure**      | Achieved     | `fail test` effect                                    |
| **Parser inspection**     | Experimental | Parse sections and log capture                        |

## Skript Native Test Tracker Integration (Experimental)

This framework includes **experimental support for Skript’s native `TestTracker`**.

### What This Means

* Test failures are forwarded to Skript’s internal test tracker
* Failures appear in Skript’s native reporting pipeline
* CI-style tooling can observe results

### Important Limitations

**This does NOT imply full parity with Skript’s internal test framework.**

Many test expressions and effects from this script are **not available** via test %string% pattern when using Skript's quickTest.

You **must** use:

```skript
devdinc test %string%
```

---

### Experimental Status

Test tracker support is:

* **Experimental**

It may:

* Break across Skript versions
* Be disabled in future releases

No compatibility guarantees are provided.

---

## High-Level Architecture

The framework is built around four core principles:

1. **Tests are custom events**
2. **Tests are registered implicitly at parse time**
3. **Execution is event-driven, not inline**
4. **Failures are tracked centrally per test**

Each test executes inside a dedicated `skriptTest` event context.

---

## Test Definition

### Syntax

```skript
test "<test name>" [when <condition>]:
    <test body>
```

* Tests are registered automatically when the script is parsed
* The optional `when` condition is evaluated immediately before execution

### Event Context

Inside a test, the framework provides:

* **`event-string` / `event-test`**
  Fully-qualified test identifier:

  ```
  <test name>
  ```

* **`event-boolean`**
  Indicates whether the test is running in **autorun mode**

---

## Test Registration

Tests are registered automatically at parse time. No explicit registration step is required.

Internal storage format:

```
-test.sk::tests::<test name>
```

---

## Running Tests

### Automatic Execution (Autorun)

On script load:

1. Previous global test state is cleared
2. A hidden sentinel test establishes autorun context
3. All registered tests are discovered
4. Tests are executed in autorun mode

Autorun execution passes `true` as the event-boolean value.

---

### Manual Execution

```skript
run test(s) %strings%
```

* Accepts one or more **fully-qualified test identifiers**
* Clears prior error state for each test
* Executes tests outside autorun mode

Identifier format:

```
<test name>
```

---

## Test Discovery

### Expression

```skript
all tests [with test name %-string%]
```

### Behavior

* No arguments → all tests from all scripts
* `with test name <string>` → exact match only

Returned values are fully-qualified test identifiers.

---

## Assertions

Assertions validate test behavior and record failures.

### Syntax Variants

```skript
assert true: <condition>
assert false: <condition>
assert <condition> [to fail]
```

### Optional Modifiers

* **`without halting`**
  Records failure but continues execution

* **`with error message "<message>"`**
  Prints formatted failure output

* **`with no error message`**
  Suppresses console output entirely

Assertions are only valid inside a test context.

---

## Error Tracking

### Expression

```skript
test errors [for %-strings%]
```

* Returns all recorded failures for the current test
* Includes:

  * Assertion failures
  * Explicit `fail test` invocations
  * Internally tracked errors

Errors are reset between tests and never leak across executions.

---

## Explicit Test Failure

### Syntax

```skript
fail test
fail test with error message "<message>"
```

Behavior:

* Records a failure immediately
* Optionally prints formatted output
* Halts execution unless `without halting` is specified

## Autorun Execution Semantics

### Autorun Flag (Test Context)

**Expression:**

```skript
event-test is autorun
event-test is not autorun
```

**Type:** Boolean condition

**Meaning:**

* Evaluates to `true` when the current test is executing as part of automatic test execution
* Evaluates to `false` when the test is executed manually via `run test(s)`

**Scope:**

* Valid only inside a `test` block
* Bound to the `skriptTest` event context

**Notes:**

* This flag is set by the framework before test execution begins
* It remains constant for the duration of the test
* It is commonly used to guard unsafe, destructive, or environment-dependent logic

---

### Autorun Control Effect

**Syntax:**

```skript
stop auto test execution here
```

**Behavior:**

* If `event-test is autorun`:

  * Immediately halts execution of the current test
    
* If `event-test is not autorun`:

  * Has no effect

**Use Case:**
Allows tests to opt out of autorun safely while still being available for manual execution.

---

### Typical Usage Pattern

```skript
test "destructive test":
    if event-test is autorun:
        stop auto test execution here
    # manual-only logic below
```

---

### Guarantees

* Autorun mode is always enabled during load-time execution
* Manual execution always runs with autorun disabled
* The autorun flag is not mutable by user code
* Autorun state never leaks between tests

## Experimental: Parsing & Log Inspection

The framework supports testing Skript syntax itself.

### Parse Section

```skript
parse:
    <skript code>
```

* Attempts to parse the nested code using `ParserInstance`
* Does not execute the code

### Log Inspection

```skript
last parse logs
```

* Returns all `SkriptLogger` messages captured during the most recent parse
* Enables validation of expected parser errors

---

## Test Lifecycle Hooks (Before / After)

The framework provides **test lifecycle hooks** that allow controlled setup and teardown logic.

### Available Hooks

```skript
before each test
after each test
before all tests
after all tests
```

### Semantics

* **`before each test`**
  Runs immediately before every individual test execution.

* **`after each test`**
  Runs immediately after every individual test execution, regardless of outcome.

* **`before all tests`**
  Runs once before any test is executed.

* **`after all tests`**
  Runs once after all test execution completes.

### Event Context

Hooks execute with the same event values as a normal test:

* `event-string` – current test identifier (for per-test hooks)
* `event-boolean` – autorun flag

### Intended Usage

Hooks are designed for:

* Environment setup / teardown
* Temporary state mutation
* Resource allocation and cleanup
* Optional world isolation (see below)

Hooks **must not** be used to implement assertions directly.

---

## Test Environment Utilities

To ensure isolation and repeatability, the framework provides controlled test fixtures:

**`test-world`** – the `"skripttest"` world if present, otherwise the first loaded world
* **`test-location`** – fixed location (`spawn + 10, 1, 0`) in test-world
* **`test-block`** – self-resetting block restored after tests located at test-location
* **`test-offline-player`** – generated offline player instance
  
---

## World Isolation & Persistence Guarantees

### Default Behavior

By default, **tests share the same world state**.

This is intentional.

Automatic per-test world isolation is **not enabled** because:

* Full world backup/restore is **disk-intensive**
* Synchronous world copying is **slow**
* Asynchronous restore is **unsafe**
* Large worlds make isolation prohibitively expensive

The framework therefore prioritizes **predictable runtime safety** over implicit isolation.

---

### Opt-In World Isolation Using Hooks

Full isolation **can** be achieved manually using lifecycle hooks:

```skript
before each test:
    # backup world state

after each test:
    # restore world state
```

This allows users to:

* Snapshot world folders
* Restore region files
* Roll back test-specific mutations

⚠ **Important:**
This approach is **explicitly opt-in** and entirely user-controlled.

The framework does **not** provide built-in world snapshotting utilities and makes no assumptions about storage strategy, synchronization model, or performance tradeoffs.


---

## Failure Reporting

Each test maintains its own failure count:

```
-test.sk::errors::<test id>
```

After execution completes:

* A summary line is printed:

```
<X>/<Y> tests passed
```

Where:

* `Y` = executed tests
* `X` = tests without recorded failures

---

## Console Output Format

When enabled, failures are printed as:

```
[Skript] [TEST FAILURE] <test name> <optional message>
```

Output is suppressed entirely when `with no error message` is specified.

---

## Internal Guarantees

The framework guarantees that:

* Test execution state is isolated per test
* Registration is implicit and deterministic
* Autorun and manual execution are distinguishable
* Failures are recorded even in non-halting mode
* State never leaks between tests

---

## Internal & Non-Public Details

The following are implementation details and must not be relied upon:

* Sentinel test usage
* Internal variable layout
* Reflection-based hooks

These may change without notice.

---

## Intended Use Cases

* Regression testing for Skript libraries
* Validation of complex event-driven logic
* Syntax and parser validation
* Automated sanity checks on server startup
* Lightweight CI-style verification

This framework is deliberately constrained to ensure reliability and transparency.

---

## Reflection Usage Disclaimer

Several advanced features rely on **reflection**:

* Parser inspection (`ParserInstance`)
* Condition parsing
* Native test tracker forwarding
* Log capture via `SkriptLogger`

### Guarantees

* Reflection usage is **read-only or carefully scoped**
* No permanent internal state is mutated
* All parser state is backed up and restored

### Non-Guarantees

* Binary compatibility across Skript versions
* Stability under obfuscation
* Availability on forks with modified internals

Reflection-backed features are considered **best-effort** and may degrade gracefully.
