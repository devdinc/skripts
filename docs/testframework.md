# Skript Testing Framework

## Purpose

This module implements a lightweight, self-contained **testing framework for Skript**. It allows scripts to define tests, automatically discover them, execute them deterministically, and report failures with precise diagnostics.

The framework is designed to:

* Run entirely inside Skript
* Avoid external dependencies
* Support both manual and automatic test execution
* Fail fast while still allowing optional non-halting assertions

---

## High-Level Architecture

The framework is built around four core ideas:

1. **Tests are custom events** identified by name
2. **Tests are registered implicitly** during script parsing
3. **Execution is event-driven**, not inline
4. **Failures are tracked centrally** and reported after execution

All internal state is stored under the `-test.sk::*` variable namespace.

---

## Test Definition

### Syntax

```skript
test "<test name>":
    <test body>
```

* `<test name>` must be unique **within the script**.
* The test body runs inside the `skriptTest` custom event.
* The event provides two event-values:

  * `string` – the fully-qualified test identifier
  * `boolean` – whether the test is running in autorun mode

### Example

```skript
test "basic arithmetic":
    assert true: 2 + 2 = 4
```

---

## Test Registration

Tests are registered automatically at parse time.

Internally, the framework records tests under:

```
-test.sk::tests::<script>::<test name>
```

No explicit registration step is required.

---

## Running Tests

### Manual Execution

```skript
run test(s) %strings%
```

* Accepts one or more test identifiers
* Identifiers must be fully-qualified:

```
<script>/<test name>
```

Before execution:

* Any previous error count for the test is cleared
* The test is executed via the `skriptTest` custom event

---

### Automatic Execution (Autorun)

On script load, the framework:

1. Clears all previous test state
2. Executes an internal sentinel test
3. Discovers all registered tests
4. Executes them using autorun mode

Autorun passes a boolean event-value (`true`) to each test, allowing tests to alter behavior when executed automatically.

---

## Test Discovery

### Expression

```skript
all tests [with test name %-string%] [within|from %-script%]
```

### Behavior

* **No arguments** → all tests from all scripts
* **from `<script>`** → only tests in that script
* **with test name `<string>`** → only the matching test (if present)

Returned values are fully-qualified identifiers:

```
<script>/<test name>
```

---

## Assertions

### Syntax

```skript
assert true: <condition>
assert false: <condition>
```

Optional error message:

```skript
assert true with error message "<message>": <condition>
```

Optional non-halting mode:

```skript
without halting assert true: <condition>
```

---

### Semantics

* `assert true` fails if the condition evaluates to `false`
* `assert false` fails if the condition evaluates to `true`
* Conditions are parsed dynamically using Skript’s `Condition` parser

On failure:

* The test’s error counter is incremented
* A formatted failure message may be sent to the console
* By default, the test **halts immediately**
* If `without halting` is used, execution continues

Assertions are only valid inside the `skriptTest` event context.

---

## Explicit Test Failure

### Syntax

```skript
fail test
fail test with error message "<message>"
```

Behavior:

* Immediately records a failure
* Optionally prints a formatted error
* Halts test execution unless `without halting` is specified

---

## Controlling Autorun Execution

### Effect

```skript
stop auto test execution here
```

* Only meaningful during autorun execution
* If the test is running in autorun mode, execution stops immediately
* Has no effect when the test is run manually

This allows tests that are unsafe, destructive, or environment-dependent to opt out of autorun.

---

## Failure Reporting

Each test maintains an internal error counter:

```
-test.sk::errors::<test id>
```

After execution completes:

* Tests that were intentionally skipped are excluded
* A summary line is printed to the console:

```
<X>/<Y> tests passed
```

Where:

* `Y` is the number of valid executed tests
* `X` is `Y - total failures`

---

## Console Output Format

Failures are reported using the following format:

```
[Skript] [TEST FAILURE] <test name> <optional message>
```

This output is emitted only when an error message is enabled for the assertion or failure.

---

## Internal and Non-Public Details

The following are implementation details and should not be relied upon:

* A hidden sentinel test is used during initialization
* Internal variables are prefixed with `-test.sk::*`
* The sentinel test ensures framework integrity before user tests run

These details may change without notice.

---

## Design Guarantees

* Tests are isolated by identifier
* Registration is implicit and deterministic
* Autorun and manual execution are distinguishable
* Failures are recorded even in non-halting mode
* The framework does not leak state between executions

---

## Intended Use Cases

* Regression testing for Skript libraries
* Validation of complex event-driven logic
* Automated sanity checks during development
* Lightweight CI-style verification on server startup

This framework is intentionally minimal and favors predictability over flexibility.
