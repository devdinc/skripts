# Skript Lambda Expressions (Java-Compatible)

This module introduces lightweight, Java-compatible lambda expressions for **Skript**, backed by real Java functional interfaces.
Lambdas are compiled into proxy instances and can be passed directly into Java APIs, streams, or stored for deferred execution.

---

## Requirements

* **Skript**
* **singlelinesection.sk**

  * Must be loaded **before** this module
  * Recommended: rename to `!singlelinesection.sk` to ensure alphabetical load order
* **skript-reflect**

---

## Supported Java Functional Interfaces

Lambdas are mapped to the following Java interfaces:

* `Supplier<T>`
* `Function<T, R>`
* `BiFunction<T, U, R>`
* `Runnable`
* `Consumer<T>`
* `BiConsumer<T, U>`

All generated lambdas are real Java proxy instances.

---

## Core Lambda Syntax (Single-Line)

### 1. Returning Lambda

```skript
lambda [<variables>]: <expression>
````

* Returns a value
* Automatically mapped to a Java functional interface
* Return vs effect behavior is auto-detected

---

### 2. Non-Returning Lambda (Effect Only)

```skript
lambda [<variables>]:- <effect>
```

* Used for side effects only
* Produces no return value

---

### 3. Forced Returning Lambda

```skript
lambda [<variables>]:+ <expression>
```

* Forces returning behavior
* Useful when the body might otherwise be parsed as an effect

---

## Multiline Lambdas (Section-Based)

Lambdas may also be written as **multiline sections**.
These allow more complex logic while still compiling into Java functional interfaces.

Multiline lambdas are created using **typed aliases** (`new runnable:`, `new function {_x}:`, etc.).

---

### Multiline Non-Returning Lambda

Maps to:

* `Runnable`
* `Consumer<T>`
* `BiConsumer<T, U>`

depending on arity.

```skript
set {_task} to new runnable:
    broadcast "working"
    broadcast "still working"
```

Rules:

* Produces **no return value**
* All lines must be **effects**
* `return` is not allowed

---

### Multiline Returning Lambda

Multiline returning lambdas **must use the `return` effect**.
The lambda does **not** infer a return value from the last line.

```skript
set {_double} to new function {_x}:
    broadcast "doubling %{_x}%"
    return {_x} * 2
```

Rules:

* `return <expression>` is **mandatory**
* The final line does **not** need to be an expression
* Effects may appear anywhere before `return`
* Multiple control-flow paths may use `return`

Maps to:

* `Supplier<T>`
* `Function<T, R>`
* `BiFunction<T, U, R>`

based on arity.

---

## Java Interface Mapping (Arity-Based)

The target Java interface is selected based on **parameter count** and **return behavior**.

### 0 Arguments

| Behavior      | Interface     |
| ------------- | ------------- |
| Returning     | `Supplier<T>` |
| Non-returning | `Runnable`    |

### 1 Argument

| Behavior      | Interface        |
| ------------- | ---------------- |
| Returning     | `Function<T, R>` |
| Non-returning | `Consumer<T>`    |

### 2 Arguments

| Behavior      | Interface             |
| ------------- | --------------------- |
| Returning     | `BiFunction<T, U, R>` |
| Non-returning | `BiConsumer<T, U>`    |

> Lambdas with more than **2 parameters are not supported**.

---

## Workaround for Higher Arity

Pass a single composite object instead:

* `map`
* `list`
* custom object

---

## Examples

### Supplier (No Arguments, Returns a Value)

```skript
set {_supplier} to lambda: "hello"
broadcast {_supplier}.get()

set {_sum} to lambda: 2 + 3
broadcast {_sum}.get()
```

---

### Function (One Argument, Returns a Value)

```skript
set {_double} to lambda {_x}: {_x} * 2
broadcast {_double}.apply(5) # 10

set {_format} to lambda {_x}: "%{_x}%_ok"
broadcast {_format}.apply("abc") # abc_ok
```

---

### BiFunction (Two Arguments, Returns a Value)

```skript
set {_add} to lambda {_a}, {_b}: {_a} + {_b}
broadcast {_add}.apply(3, 4) # 7
```

---

### Runnable (No Arguments, No Return)

```skript
set {_task} to lambda:- broadcast "ran"
{_task}.run()
```

---

### Consumer (One Argument, No Return)

```skript
set {_printer} to lambda {_x}:- broadcast {_x}
{_printer}.accept(42)
```

---

### BiConsumer (Two Arguments, No Return)

```skript
set {_pair} to lambda {_a}, {_b}:- broadcast "%{_a}%, %{_b}%"
{_pair}.accept("x", "y")
```

---

## Typed Alias Syntax

In addition to the generic `lambda` syntax, explicit aliases are available.
These enforce **arity and return behavior at parse time**.

### Returning Aliases

```skript
supplier:
getter:
function {_x}:
applier {_x}:
bifunction {_a}, {_b}:
biapplier {_a}, {_b}:
```

### Non-Returning Aliases

```skript
runnable:
runner:
consumer {_x}:
accepter {_x}:
biconsumer {_a}, {_b}:
biaccepter {_a}, {_b}:
```

### Example

```skript
set {_f} to function {_x}: {_x} * 2
set {_r} to runnable:
    broadcast "hello"
```

---

## Invoking Lambdas (Helper Expression)

Lambdas can be invoked directly via Java methods **or** using the helper syntax:

```skript
run lambda <lambda> [with <arguments>]
```

The correct method (`get`, `apply`, `accept`, `run`) is resolved automatically.

### Examples

```skript
run lambda {_supplier}
run lambda {_double} with 5
run lambda {_pair} with "a", "b"
```

---

## Composite Data Example (Arity Workaround)

```skript
set {_map} to new HashMap()
{_map}.put(1, 2)
{_map}.put(2, 3)

set {-total} to 0
set {_inlineforeach} to lambda {_v}:- add {_v} to {-total}
set {_adder} to lambda {_m}:- {_m}.values().stream().forEach({_inlineforeach})

{_adder}.accept({_map})
```

---

## Limitations

* Lambdas may be **single-line or multiline**
* Single-line lambdas infer return vs effect behavior
* Multiline returning lambdas **require `return`**
* Multiline non-returning lambdas **must not return**
* Lambdas are limited to **0–2 parameters**
* Variable lists as parameters are **not supported**
* Arrays are unreliable inside lambdas:

  * Indexing (`[n]`) does not work
  * Use `spread(...)` before passing arrays
* Imported classes or complex expressions may fail inline

  * Prefer multiline lambdas
  * Or wrap logic in a normal Skript function

---

## Notes

* Single-line lambdas auto-detect return vs effect
* Multiline lambdas require explicit intent
* Lambdas are real Java proxy objects and fully compatible with:

  * Java streams
  * Java APIs
  * skript-reflect usage
* Experimentally, local values are passed into lambda sections. Use with care.

---

## Planned

* Additional utility expressions (e.g., `for each` helpers)
* These will be introduced in **separate files**

