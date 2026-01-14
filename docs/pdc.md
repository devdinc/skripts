
# Persistent Data Container (PDC) Utility Expressions for Skript

> **WARNING:** Read migration notes carefully before upgrading.

---

## Overview

This document describes a set of Skript expressions and helpers for interacting with Bukkit's `PersistentDataContainer` (PDC).

It supports:

- Native `PersistentDataType` (PDT) values  
- Arbitrary object storage via Java serialization into `BYTE_ARRAY`

---

## Migration Notice (Base64 Removed)

Previous versions serialized arbitrary objects using Base64 encoding and stored them as `STRING` values.

**This implementation no longer uses Base64.**

Arbitrary objects are now:

- Serialized directly using `BukkitObjectOutputStream`
- Stored natively as `PersistentDataType.BYTE_ARRAY`

This is a **storage-format change only**.  
Arbitrary object support remains fully supported.

### Required User Action

- Existing Base64-encoded PDC values are **not compatible**
- Stored data must be migrated or deleted

Scripts do **not** require syntax changes, but values written by older versions will not deserialize correctly.

---

## Requirements

- Paper server  
- Skript  
- skript-reflect  
- skBee  

---

## Key Features

### 1. Unified `key in pdc` Expression

- Read, write, and delete PDC entries using a single expression
- Automatically resolves:
  - `PersistentDataHolder` → `PersistentDataContainer`

### 2. Native and Arbitrary Object Storage

- When a `PersistentDataType` is provided:  
  → Values are stored natively
- When omitted:  
  → Values are serialized and stored as `BYTE_ARRAY`

### 3. NamespacedKey Convenience Expression

- Allows creation of `NamespacedKey` from strings such as:
  - `plugin:key`

### 4. Safety and Validation

- Runtime validation ensures correct types for:
  - Key
  - Container
  - PersistentDataType
- Invalid expressions fail silently to avoid hard Skript errors

---

## Serialization Notes

- Arbitrary objects are serialized using `BukkitObjectOutputStream`
- Data is stored directly as `byte[]` via `PersistentDataType.BYTE_ARRAY`
- Objects **must** implement `java.io.Serializable`

### Compared to Base64

- Lower overhead
- No string encoding or decoding
- Direct compatibility with Bukkit PDC APIs

---

## Syntax Summary

### Reading

```skript
set {_value} to key "plugin:test" within player's pdc
set {_value} to key "plugin:test" in player's pdc for pdt string
````

### Writing

```skript
set key "plugin:test" within player's pdc to {_object}
set key "plugin:test" in player's pdc for pdt integer to 5
```

### Deleting

```skript
delete key "plugin:test" within player's pdc
```

---

## Notes

* If no `PersistentDataType` is specified, `BYTE_ARRAY` storage is used
* Deleting a key or setting its value to `null` removes the entry

---

## Caveats

* Deserialization failures will propagate runtime errors
* Class definition changes may break previously serialized data
* Old Base64-encoded values must be migrated manually
