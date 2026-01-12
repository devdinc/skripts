# Skript Reflect – Testing Framework Documentation

## Overview

This module implements a minimal, event-driven testing framework written entirely in **Skript**. It enables definition, discovery, and execution of tests using custom events, assertions, and explicit failure handling.

Tests are **lazily registered** at parse time and executed via a dedicated custom event, providing isolation, deterministic execution order, and immediate termination on failure.

The framework is intentionally lightweight and non-intrusive, designed for embedding directly into Skript projects without external dependencies.

---

## Core Concepts

* Each test is identified by a **unique string name**, scoped per script.
* Tests are registered implicitly when parsed.
* Tests execute inside a custom event (`skriptTest`).
* Assertions and explicit failures **abort test execution immediately**.
* Tests may be executed individually, in groups, or automatically on load.

---

## Defining a Test

Tests are defined using custom event syntax:

```skript

test "<test name>":
    <test body>
```

Example:

```skript

test "math works":
    assert true: 2 + 2 = 4
```

---

## Running Tests

### Effect

```skript
run test(s) %strings%
```

* Executes one or more fully-qualified test identifiers.
* Identifiers are in the form:

```
<script>/<test name>
```

### Autorun Mode

```skript
autorun %strings%
```

When autorun is used, tests may explicitly opt out of execution using `stop auto test execution here`.

---

## Discovering Tests

### Expression

```skript
all tests [with test name %-string%] [within|from %-script%]
```

#### Behavior

* Without arguments: returns all discovered tests across all scripts.
* With `from <script>`: limits discovery to a single script.
* With `with test name <string>`: returns only the matching test if present.

Returned values are fully-qualified test identifiers.

---

## Automatic Execution on Load

On script load:

1. Internal test state is reset.
2. A hidden sentinel test is executed to initialize the framework.
3. All discovered tests are collected.
4. Tests are executed automatically using autorun.

Automatic execution may be suppressed **per test**.

---

## Assertions

### Effect

```skript
assert true: <condition>
assert false: <condition>
```

Optional error message:

```skript
assert true with error message "<message>": <condition>
```

#### Semantics

* `assert true`: fails if the condition evaluates to false.
* `assert false`: fails if the condition evaluates to true.
* Conditions are parsed dynamically using Skript's `Condition` parser.
* On failure:

  * The test aborts immediately.
  * The failure is recorded.
  * A formatted error is sent to the console.

Assertions are only valid inside the `skriptTest` event context.

---

## Explicit Test Failure

### Effect

```skript
fail test [with error message "<message>"]
```

* Immediately aborts the test.
* Records a failure.
* Emits a formatted console message.

---

## Controlling Autorun Execution

### Effect

```skript
stop auto test execution here
```

* Only usable during autorun execution.
* When invoked, prevents the current test from executing further in autorun mode.
* Has no effect during manual execution.

---

## Output and Reporting

* Each failed assertion or explicit failure increments the test's error count.
* After execution, a summary is printed to the console:

```
<passed>/<total> tests passed
```

Tests that intentionally opt out of execution are excluded from totals.

---

## Notes and Guarantees

* Test registration is implicit and automatic.
* Tests are uniquely scoped per script.
* Fail-fast behavior is enforced per test.
* No global state leaks between test executions.
* Designed for minimal footprint and predictable behavior.

---

## Internal Details (Non-API)

* A hidden sentinel test is used internally for framework initialization.
* Internal variables are namespaced under `-test.sk::*`.
* Error tracking is per-test and cleared before execution.

These details are implementation-specific and not part of the public API.
