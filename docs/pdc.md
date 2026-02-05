# Persistent Data Container (PDC) Utility Expressions for Skript

---

## Overview

This document describes a set of Skript expressions and helpers for interacting with Bukkit's `PersistentDataContainer` (PDC).

It supports:

- Native `PersistentDataType` (PDT) values
- Arbitrary object storage via Java serialization into `BYTE_ARRAY`

---

## Requirements

- Paper server
- Skript
- skript-reflect

---

## Key Features

### 1. Unified `key … in pdc` Expression

- Read, write, and delete PDC entries using a single expression
- Automatically resolves:
  - `PersistentDataHolder` → `PersistentDataContainer`

---

### 2. Native and Arbitrary Object Storage

- When a `PersistentDataType` is provided:
  → Values are stored natively using that PDT
- When omitted:
  → Values are serialized and stored as `PersistentDataType.BYTE_ARRAY`

---

### 3. Built-in NamespacedKey Handling

There is **no standalone NamespacedKey expression**.

Instead, namespaced keys are handled directly by the main expression using string input.

Key strings must be in the form:

```

namespace:key

````

Example:

```skript
"minecraft:foo"
"myplugin:data"
````

---

### 4. Safety and Validation

* Runtime validation ensures correct types for:

  * Key string
  * Container / holder
  * PersistentDataType (if provided)
* Invalid expressions fail silently to avoid hard Skript errors

---

## Serialization Notes

* Arbitrary objects are serialized using `BukkitObjectOutputStream`
* Data is stored directly as `byte[]` via `PersistentDataType.BYTE_ARRAY`
* Objects **must** implement `java.io.Serializable`

---

## Syntax Summary

### Core Expression

```skript
expression [devdinc] [namespaced]( |-)key %string% [with]in %pdcholder/pdc% [for %-pdt%]
```

---

### Reading

```skript
set {_value} to key "plugin:test" within player's pdc
set {_value} to key "plugin:test" in player's pdc for pdt string
```

---

### Writing

```skript
set key "plugin:test" within player's pdc to {_object}
set key "plugin:test" in player's pdc for pdt integer to 5
```

---

### Deleting

```skript
delete key "plugin:test" within player's pdc
```

---

## Behavior Notes

* If no `PersistentDataType` is specified, `BYTE_ARRAY` storage is used
* Setting a key to `null` removes the entry
* Deleting a key removes it regardless of storage type

---

## Caveats

* Deserialization failures will propagate runtime errors
* Class definition changes may break previously serialized data
* Stored objects must remain compatible with Java serialization

---

