# Scoped Variables Utility for Skript

This module introduces **scoped variables**, allowing variables to be namespaced automatically by
script, folder (package), or a custom scope string.

It provides:

- A configurable **default scope per script**
- A `scoped variable` expression that transparently rewrites variable paths
- Full support for **get / set / add / remove / delete / reset**
- Correct handling of **local**, **ephemeral**, and **list** variables

All scoping is implemented by rewriting variable names internally.

---

## Concepts

### What Is a Scoped Variable?

A scoped variable is a normal Skript variable whose **storage key is prefixed with a scope**.

Instead of:

```skript
set {count} to 1
````

you get:

```text
scoped::<scope>::count
```

Scopes prevent collisions between scripts, folders, or logical modules while still using Skript’s variable system.

---

## Default Scope per Script

Each script can define a **default scope** that is used whenever no explicit scope is provided.

### Effect Syntax

```skript
set default scope for scoped variables in current script to
    current folder
    current package
    current script
    folder <string>
    package <string>
    <script>
```

### Meanings

| Option                                 | Resulting Scope                               |
| -------------------------------------- | --------------------------------------------- |
| `current script`                       | Script file name                              |
| `current folder` / `current package`   | Script’s parent folder relative to `/scripts` |
| `folder <string>` / `package <string>` | Custom folder/package scope                   |
| `<script>`                             | Explicit script scope                         |

### Examples

```skript
set default scope for scoped variables in current script to current folder
```

```skript
set default scope for scoped variables in current script to folder "economy"
```

```skript
set default scope for scoped variables in current script to script "main.sk"
```

If no default scope is set, the script name is used.

---

## Scoped Variable Expression

### Syntax

```skript
scoped [variable] %variable% [within|from|by
    %-script%
  | current folder
  | current package
]
```

This expression rewrites the backing variable name based on:

* The variable being accessed
* The resolved scope
* Variable modifiers (local, ephemeral, list)

---

## Scope Resolution Rules

If no explicit scope is provided:

1. Use the script’s **default scope**, if set
2. Otherwise, use the **current script name**

If an explicit scope is provided:

| Clause                               | Scope Used             |
| ------------------------------------ | ---------------------- |
| `within <script>`                    | That script            |
| `current folder` / `current package` | Script’s parent folder |

---

## Variable Modifiers

Scoped variables preserve all Skript variable semantics.

### Local Variables

```skript
set {_x} to 1
set scoped {_x} to 5
```

→ stored under:

```text
_scoped::<scope>::x
```

---

### Ephemeral Variables

```skript
set {-temp} to 3
set scoped {-temp} to 9
```

→ stored under:

```text
-scoped::<scope>::temp
```

---

### List Variables

```skript
set {data::a} to 1
set scoped {data::*} to 2
```

→ stored under:

```text
scoped::<scope>::data::*
```

---

## Supported Operations

The `scoped variable` expression supports **all standard variable operations**:

* get
* set
* add
* remove
* remove all
* delete
* reset

### Examples

```skript
set scoped {count} to 1
add 5 to scoped {count}
broadcast scoped {count}
```

```skript
delete scoped {playerdata::*}
```

```skript
set scoped {_local} to "hello"
```

---

## Explicit Scope Usage

```skript
set scoped {coins} within current folder to 100
```

```skript
set scoped {coins} within script "bank.sk" to 250
```

---

## Internal Storage Format

Internally, variables are rewritten as:

```text
[prefix]scoped::<scope>::<variable-name>[:: *]
```

Where:

* `prefix` is:

  * `_` for local variables
  * `-` for ephemeral variables
* `<scope>` is the resolved scope string
* `::*` is appended for list variables

This is an implementation detail and should not be relied upon directly.

---

## Notes & Caveats

* Scoped variables are **not a new variable type** — they are rewritten normal variables
* Scope resolution depends on the script’s file path
* Moving scripts between folders may change scope values
* Local and ephemeral behavior matches native Skript semantics
* Variable names are resolved at runtime using the current event

---

## Intended Use Cases

* Script modularization
* Library-style Skript files
* Avoiding global variable collisions
* Folder-based namespaces
* Shared state with controlled visibility

---

