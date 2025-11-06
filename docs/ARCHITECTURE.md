# Architecture Guide

This document explains the design patterns, architecture decisions, and internal workings of the python-sepa library.

## Table of Contents

- [Overview](#overview)
- [Design Philosophy](#design-philosophy)
- [Core Architecture](#core-architecture)
- [Data-Driven Structure Definitions](#data-driven-structure-definitions)
- [Processing Pipeline](#processing-pipeline)
- [Module Architecture](#module-architecture)
- [Message Registration System](#message-registration-system)
- [Structure Definition System](#structure-definition-system)
- [Parser Structure Reversal](#parser-structure-reversal)
- [Namespace Handling](#namespace-handling)
- [Validation Architecture](#validation-architecture)
- [Extension Points](#extension-points)
- [Design Patterns](#design-patterns)
- [Performance Considerations](#performance-considerations)

## Overview

Python-sepa is built around a **declarative, data-driven architecture** that separates message structure definitions from the processing logic. This design makes it easy to add support for new ISO 20022 message types without modifying core functionality.

### Key Architectural Principles

1. **Separation of Concerns** - Clear boundaries between building, parsing, validation, and signing
2. **Data-Driven Design** - Message structures defined as data, not code
3. **Single Source of Truth** - One structure definition serves both building and parsing
4. **Auto-Discovery** - Messages are automatically registered and available
5. **Extensibility** - Easy to add new message types and definitions

## Design Philosophy

### Why Data-Driven?

ISO 20022 defines hundreds of message types with complex nested structures. Rather than writing custom code for each message type, python-sepa uses **structure definitions** (nested dictionaries) that describe the message format.

**Benefits:**
- Add new message types by defining structure, no algorithm changes needed
- Structure definitions are easier to understand than procedural code
- Single definition serves both XML building and parsing
- Less code = fewer bugs

### Declarative vs Imperative

**Traditional Approach (Imperative):**
```python
def build_mandate(data):
    root = Element('Document')
    mandate_req = SubElement(root, 'MndtInitnReq')
    grp_hdr = SubElement(mandate_req, 'GrpHdr')
    msg_id = SubElement(grp_hdr, 'MsgId')
    msg_id.text = data['message_id']
    # ... hundreds more lines
```

**Python-sepa Approach (Declarative):**
```python
structure = {
    '_self': 'MndtInitnReq',
    'group_header': {
        '_self': 'GrpHdr',
        'message_id': 'MsgId'
    }
}

xml = builder.build(structure, data)
```

## Core Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Application                          │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐     ┌──────────────┐
│   Builder    │      │    Parser    │     │  Validator   │
│              │      │              │     │              │
│ Dict → XML   │      │ XML → Dict   │     │ XSD Check    │
└──────────────┘      └──────────────┘     └──────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
            ┌──────────────┐    ┌──────────────┐
            │   Messages   │    │ Definitions  │
            │              │    │              │
            │ pain.008.py  │    │  general.py  │
            │ pain.009.py  │    │  payment.py  │
            │ camt.053.py  │    │  mandate.py  │
            │     ...      │    │     ...      │
            └──────────────┘    └──────────────┘
                    │                   │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │                   │
                    │  Structure Defs   │
                    │  (Nested Dicts)   │
                    │                   │
                    └───────────────────┘
```

## Data-Driven Structure Definitions

### Structure Definition Format

Structure definitions are nested Python dictionaries with special keys prefixed with `_`:

```python
{
    '_self': 'ElementName',           # XML tag name
    '_namespaces': {...},             # Namespace mapping (root only)
    '_sorting': ['Tag1', 'Tag2'],     # Child element order
    '_attribs': {'key': 'AttrName'},  # Attribute mappings
    '_nochildren': True,              # Text-only element flag

    'data_key': 'XMLTag',             # Simple element mapping
    'nested_key': {                   # Nested structure
        '_self': 'NestedTag',
        'child': 'ChildTag'
    },
    'list_key': [{                    # List of elements
        '_self': 'ItemTag',
        'field': 'FieldTag'
    }]
}
```

### Special Keys Explained

| Key | Purpose | Example |
|-----|---------|---------|
| `_self` | XML tag name for this element | `'_self': 'GrpHdr'` |
| `_namespaces` | XML namespace declarations (root only) | `'_namespaces': {'': 'urn:...'}` |
| `_sorting` | Order child elements must appear | `'_sorting': ['MsgId', 'CreDtTm']` |
| `_attribs` | Map data keys to XML attributes | `'_attribs': {'currency': 'Ccy'}` |
| `_nochildren` | Element contains only text, no children | `'_nochildren': True` |

### Example: Complete Structure

```python
mandate_group_header = {
    '_self': 'GrpHdr',
    '_sorting': ['MsgId', 'CreDtTm', 'NbOfTxs', 'InitgPty'],

    'message_id': 'MsgId',
    'creation_date_time': 'CreDtTm',
    'number_of_transactions': 'NbOfTxs',
    'initiating_party': {
        '_self': 'InitgPty',
        'name': 'Nm',
        'identification': {
            '_self': 'Id',
            'organisation_id': {
                '_self': 'OrgId',
                'other': {
                    '_self': 'Othr',
                    'id': 'Id'
                }
            }
        }
    }
}
```

## Processing Pipeline

### Building Flow

```
Python Dict → build() → build_tree() → build_child() → XML Tree
                │
                ├─ Apply _sorting
                ├─ Add _attribs
                └─ Wrap in <Document> (if document=True)
```

**Step-by-step:**

1. **User provides data dict** matching structure keys
2. **`build()`** creates root and optionally wraps in `<Document>`
3. **`build_tree()`** recursively processes structure:
   - Creates element with `_self` tag name
   - Adds attributes from `_attribs`
   - For each non-special key, calls `build_child()`
   - Sorts children according to `_sorting`
4. **`build_child()`** handles:
   - Nested dicts → recursive `build_tree()`
   - Lists → multiple elements
   - Simple values → text content
5. **Returns lxml.etree.Element**

### Parsing Flow

```
XML Tree → parse() → get_structure() → parse_tree() → Python Dict
             │           (if None)
             │
             └─ Auto-detect from xmlns namespace
```

**Step-by-step:**

1. **User provides XML** (string or tree)
2. **`parse_string()`** converts string to tree if needed
3. **`parse()`** checks if structure is None:
   - If None: **`get_structure()`** extracts namespace, looks up message type
   - If provided: uses given structure
4. **`parse_tree()`** recursively processes XML:
   - For each child element, lookup in structure
   - Handle lists (append to array)
   - Handle nested dicts (recursive call)
   - Handle simple elements (extract text)
5. **Returns dict** with parsed data

## Module Architecture

### Builder Module (`sepa/builder.py`)

**Responsibilities:**
- Convert Python dicts to XML trees
- Handle element ordering and attributes
- Wrap messages in `<Document>` element

**Exports:**
- Functions: `build()`, `build_string()`, `build_tree()`, `build_child()`
- Message structures: `builder.mandate_initiation_request`, etc.

**Key Algorithm (build_tree):**
```python
def build_tree(structure, data):
    tag = etree.Element(structure['_self'])

    # Add attributes
    if '_attribs' in structure and '_attribs' in data:
        for key, attr_name in data['_attribs'].items():
            tag.attrib[structure['_attribs'][key]] = attr_name

    # Skip children if text-only element
    if '_nochildren' in structure:
        tag.text = data.get('_value', '')
        return tag

    # Add child elements
    for child_key in structure:
        if not child_key.startswith('_') and child_key in data:
            # Build child (handles lists and nested dicts)
            child_element = build_child(structure[child_key], data[child_key])
            tag.append(child_element)

    # Sort children
    if '_sorting' in structure:
        tag[:] = sorted(tag, key=lambda el: structure['_sorting'].index(el.tag))

    return tag
```

### Parser Module (`sepa/parser.py`)

**Responsibilities:**
- Convert XML trees to Python dicts
- Auto-detect message types from XML namespaces
- Reverse builder structures to parser structures

**Exports:**
- Functions: `parse()`, `parse_string()`, `get_structure()`, `reverse()`
- Exception: `UnsupportedDocumentType`
- Message structures: `parser.mandate_initiation_request`, etc.

**Key Algorithm (parse_tree):**
```python
def parse_tree(structure, tag):
    data = {}

    for child in tag:
        child.tag = etree.QName(child).localname  # Remove namespace

        if child.tag in structure:
            substructure = structure[child.tag]

            if isinstance(substructure, list):
                # Handle list elements
                key = substructure[0]['_self'] if isinstance(substructure[0], dict) else substructure[0]
                value = parse_tree(substructure[0], child) if isinstance(substructure[0], dict) else child.text

                if key not in data:
                    data[key] = []
                data[key].append(value)

            elif isinstance(substructure, dict):
                # Handle nested dict
                data[substructure['_self']] = parse(substructure, child)

            else:
                # Handle simple element
                data[substructure] = child.text

    return data
```

### Validator Module (`sepa/validator.py`)

**Responsibilities:**
- Load and cache XSD schemas
- Validate XML against schemas
- Provide boolean and exception-based validation

**Schema Loading:**
- Schemas stored in `sepa/schemas/*.xsd`
- Loaded on-demand using `lxml.etree.XMLSchema`
- Cached for performance

### Signer Module (`sepa/signer.py`)

**Responsibilities:**
- Wrap signxml library for XML signing
- Provide simplified signing and verification API

**Implementation:**
- Thin wrapper around `signxml.XMLSigner` and `signxml.XMLVerifier`
- Delegates all functionality to signxml library

## Message Registration System

### Auto-Discovery

Messages are automatically discovered and registered using Python's `pkgutil.walk_packages()`:

```python
# In sepa/messages/__init__.py

import pkgutil
from collections import namedtuple

Message = namedtuple('Message', ['name', 'standard', 'compatible_standards', 'definition'])

sepa_messages = {}

# Walk through all message modules
for importer, modname, ispkg in pkgutil.walk_packages(__path__, prefix=__name__ + '.'):
    if not ispkg:
        module = __import__(modname, fromlist=[''])

        # Each module exports: name, standard, compatible_standards, definition
        group = modname.split('.')[-2]  # 'pain' or 'camt'

        if group not in sepa_messages:
            sepa_messages[group] = {}

        sepa_messages[group][module.name] = Message(
            name=module.name,
            standard=module.standard,
            compatible_standards=getattr(module, 'compatible_standards', []),
            definition=module.definition
        )
```

### Adding a New Message Type

To add support for a new message type (e.g., pain.001.001.08):

1. **Create message file** `sepa/messages/pain/pain001.py`:
```python
from sepa.definitions import payment

name = 'customer_credit_transfer_initiation'
standard = 'pain.001.001.08'
compatible_standards = ['pain.001.001.03', 'pain.001.001.09']

definition = {
    '_self': 'CstmrCdtTrfInitn',
    '_namespaces': {
        '': 'urn:iso:std:iso:20022:tech:xsd:pain.001.001.08',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    },
    '_sorting': ['GrpHdr', 'PmtInf'],
    'group_header': payment.payment_group_header('GrpHdr'),
    'payment': [payment.payment('PmtInf')]
}
```

2. **Add XSD schema** to `sepa/schemas/pain.001.001.08.xsd`

3. **Done!** The message is automatically:
   - Registered in `sepa_messages`
   - Exported from builder, parser, validator modules
   - Available as `builder.customer_credit_transfer_initiation`

## Structure Definition System

### Reusable Definitions

The `sepa/definitions/` directory contains functions that generate reusable structure components:

```python
# sepa/definitions/general.py

def party(tag):
    """Generates a party identification structure"""
    return {
        '_self': tag,
        '_sorting': ['Nm', 'PstlAdr', 'Id', 'CtryOfRes', 'CtctDtls'],
        'name': 'Nm',
        'postal_address': address('PstlAdr'),
        'identification': {
            '_self': 'Id',
            'organisation_id': organisation_id('OrgId'),
            'private_id': private_id('PrvtId')
        }
    }
```

**Benefits:**
- **DRY Principle** - Define once, use everywhere
- **Consistency** - Same structure across different message types
- **Maintainability** - Update in one place

### Definition Categories

| Module | Structures | Used In |
|--------|-----------|---------|
| `general.py` | party, account, address, agent | All messages |
| `payment.py` | transaction, payment, type_information | PAIN messages |
| `mandate.py` | mandate, original_message | Mandate messages |
| `statement.py` | statement, entry, balance | CAMT statements |
| `notification.py` | notification | CAMT notifications |

## Parser Structure Reversal

### The Challenge

Builder structures map data keys → XML tags:
```python
{'message_id': 'MsgId'}  # data['message_id'] → <MsgId>
```

Parser structures need the reverse mapping (XML tags → data keys):
```python
{'MsgId': 'message_id'}  # <MsgId> → data['message_id']
```

### The Solution: Automatic Reversal

The `reverse()` function automatically converts builder structures to parser structures:

```python
def reverse(structure, name=''):
    new_structure = {'_self': name}

    for child in structure:
        if not child.startswith('_'):
            sub = structure[child]

            if isinstance(sub, list):
                # Reverse list structures
                if isinstance(sub[0], dict):
                    new_structure[sub[0]['_self']] = [reverse(sub[0], child)]
                else:
                    new_structure[sub[0]] = [child]

            elif isinstance(sub, dict):
                # Reverse nested dicts
                new_structure[sub['_self']] = reverse(sub, child)

            else:
                # Reverse simple mappings
                new_structure[sub] = child

        elif child != '_self':
            # Copy special keys unchanged
            new_structure[child] = structure[child]

    return new_structure
```

**Example:**

Builder structure:
```python
{
    '_self': 'GrpHdr',
    'message_id': 'MsgId',
    'creation_date_time': 'CreDtTm'
}
```

Reversed parser structure:
```python
{
    '_self': '',
    'MsgId': 'message_id',
    'CreDtTm': 'creation_date_time'
}
```

## Namespace Handling

### XML Namespaces

ISO 20022 uses XML namespaces to identify message types:

```xml
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.009.001.05">
```

### Auto-Detection from Namespace

The `get_structure()` function extracts the namespace and looks up the message:

```python
def get_structure(tree):
    if etree.QName(tree).localname == "Document":
        # Extract namespace: "urn:iso:std:iso:20022:tech:xsd:pain.009.001.05"
        xmlns = etree.QName(tree).namespace.split(':')

        # Get message type: "pain.009.001.05"
        doctype = xmlns[-1]

        # Look up in registered messages
        for group_name, group in sepa_messages.items():
            for name, message in group.items():
                if doctype == message.standard or doctype in message.compatible_standards:
                    return globals()[message.name]

    raise UnsupportedDocumentType(doctype)
```

### Compatible Standards

Messages can support multiple versions:

```python
# In pain009.py
standard = 'pain.009.001.05'
compatible_standards = ['pain.009.001.04', 'pain.009.001.06']
```

This allows parsing older/newer versions with the same structure.

## Validation Architecture

### XSD Schema Validation

The library includes XSD schemas for all supported message types.

**Schema Loading:**
```python
def get_schema(schema_name):
    schema_path = os.path.join(os.path.dirname(__file__), 'schemas', schema_name)
    return etree.XMLSchema(etree.parse(schema_path))
```

**Validation:**
```python
def validate(schema_name, tree):
    return get_schema(schema_name).validate(tree)
```

### Validation Levels

1. **XSD Validation** (Structural)
   - Element presence and order
   - Data types
   - Required vs optional fields

2. **Business Rule Validation** (Not Yet Implemented)
   - IBAN validation
   - BIC validation
   - Amount calculations
   - Date logic

## Extension Points

### Adding Custom Definitions

Create your own definition functions:

```python
# my_definitions.py

def custom_party(tag):
    return {
        '_self': tag,
        'name': 'Nm',
        'custom_field': 'CstmFld'
    }
```

Use in your message definitions:

```python
from my_definitions import custom_party

definition = {
    '_self': 'MyMessage',
    'party': custom_party('Pty')
}
```

### Custom Message Types

Create custom ISO 20022 messages:

```python
# sepa/messages/custom/mymsg001.py

name = 'my_custom_message'
standard = 'mymsg.001.001.01'

definition = {
    '_self': 'MyCustomMsg',
    '_namespaces': {'': 'urn:custom:namespace'},
    'header': {'_self': 'Hdr', 'id': 'Id'}
}
```

### Custom Validation

Add business rule validation:

```python
from sepa import validator

def validate_with_rules(tree, data):
    # XSD validation
    if not validator.validate(validator.customer_direct_debit_initiation, tree):
        return False

    # Custom business rules
    if data['amount'] < 0:
        raise ValueError("Amount must be positive")

    return True
```

## Design Patterns

### 1. **Template Method Pattern**

The `build_tree()` and `parse_tree()` functions use a template approach:
- Structure defines the template
- Data provides the values
- Algorithm remains constant

### 2. **Strategy Pattern**

Different message types are different strategies:
- Same interface (`build()`, `parse()`)
- Different structures (strategies)
- Runtime selection via auto-detection

### 3. **Registry Pattern**

`sepa_messages` acts as a registry:
- Messages register themselves on import
- Lookup by name or standard identifier
- Auto-discovery via `pkgutil`

### 4. **Adapter Pattern**

`reverse()` adapts builder structures for parsing:
- Same data structure
- Different access pattern
- Automatic adaptation

### 5. **Facade Pattern**

High-level modules (`builder`, `parser`, etc.) provide simple facades:
- Hide complex lxml operations
- Provide domain-specific API
- Simplify common operations

## Performance Considerations

### Structure Caching

- Structures defined once at module load time
- Parser structures generated once via `reverse()`
- XSD schemas loaded and cached on first use

### XML Processing

- Uses lxml (C library) for speed
- Minimal Python object creation
- Direct tree manipulation

### Optimization Opportunities

**Current:**
- Sequential processing
- No batch operations
- Full tree traversal

**Future improvements:**
- Batch processing for multiple messages
- Lazy evaluation for large messages
- Streaming parser for huge files

### Memory Usage

**Per message:**
- Structure definition: ~1-10 KB (shared)
- lxml tree: ~size of XML
- Parsed dict: ~size of XML
- XSD schema: ~50-200 KB (cached)

**For 1000 messages:**
- Structures: ~10 KB (shared)
- Trees: ~1000 × message size
- Schemas: ~200 KB (cached)

## Summary

The python-sepa architecture achieves:

✅ **Simplicity** - Data-driven structures are easy to understand
✅ **Extensibility** - New messages added with minimal code
✅ **Maintainability** - Single source of truth for structure
✅ **Performance** - Leverages fast lxml library
✅ **Correctness** - XSD validation ensures compliance

The declarative approach makes ISO 20022 message handling accessible while maintaining the flexibility needed for complex financial messaging systems.
