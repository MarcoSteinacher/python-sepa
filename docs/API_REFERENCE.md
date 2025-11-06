# API Reference

This document provides detailed API documentation for the python-sepa library.

## Table of Contents

- [Module Overview](#module-overview)
- [Builder Module](#builder-module)
- [Parser Module](#parser-module)
- [Validator Module](#validator-module)
- [Signer Module](#signer-module)
- [Messages Module](#messages-module)
- [Definitions Module](#definitions-module)
- [Data Structures](#data-structures)
- [Exceptions](#exceptions)

## Module Overview

The library is organized into the following main modules:

| Module | Purpose | Import |
|--------|---------|--------|
| `builder` | Build XML from Python dictionaries | `from sepa import builder` |
| `parser` | Parse XML to Python dictionaries | `from sepa import parser` |
| `validator` | Validate XML against XSD schemas | `from sepa import validator` |
| `signer` | Sign and verify XML messages | `from sepa import signer` |
| `messages` | ISO 20022 message definitions | `from sepa.messages import sepa_messages` |
| `definitions` | Reusable structure definitions | `from sepa.definitions import general, payment, etc.` |

---

## Builder Module

**Import:** `from sepa import builder`

The builder module converts Python dictionaries into ISO 20022 compliant XML messages.

### Functions

#### `build(structure, data, document=True, namespaces=None)`

Builds an XML tree from a structure definition and data dictionary.

**Parameters:**
- `structure` (dict): The message structure definition
- `data` (dict): The data to populate the message with
- `document` (bool, optional): If True, wraps the message in a `<Document>` root element. Default: `True`
- `namespaces` (dict, optional): Custom namespace mapping. If None, uses the structure's `_namespaces`

**Returns:** `lxml.etree.Element` - The built XML tree

**Example:**
```python
from sepa import builder

data = {
    'group_header': {'message_id': 'MSG001'},
    'mandate': [{'id': 'MNDT123', 'request_id': 'REQ456'}]
}

xml_tree = builder.build(builder.mandate_initiation_request, data)
```

#### `build_string(structure, data, document=True, namespaces=None, **kwargs)`

Builds an XML message and returns it as a byte string.

**Parameters:**
- `structure` (dict): The message structure definition
- `data` (dict): The data to populate the message with
- `document` (bool, optional): If True, wraps in `<Document>` element. Default: `True`
- `namespaces` (dict, optional): Custom namespace mapping
- `**kwargs`: Additional arguments passed to `lxml.etree.tostring()`:
  - `pretty_print` (bool): Format with indentation
  - `xml_declaration` (bool): Include XML declaration
  - `encoding` (str): Character encoding (e.g., 'UTF-8')

**Returns:** `bytes` - The XML as a byte string

**Example:**
```python
xml_bytes = builder.build_string(
    builder.mandate_initiation_request,
    data,
    pretty_print=True,
    xml_declaration=True,
    encoding='UTF-8'
)

# Convert to string if needed
xml_string = xml_bytes.decode('utf-8')
```

#### `build_tree(structure, data)`

Recursively builds an XML tree from structure and data. Used internally by `build()`.

**Parameters:**
- `structure` (dict): Structure definition with special keys (`_self`, `_attribs`, `_sorting`, etc.)
- `data` (dict): Data to populate

**Returns:** `lxml.etree.Element`

#### `build_child(structure, data)`

Builds a child element. Handles both simple text elements and complex nested structures.

**Parameters:**
- `structure` (dict or str): Structure definition
- `data` (any): Data to populate (dict for complex, string for simple)

**Returns:** `lxml.etree.Element`

### Message Structure Attributes

Exported message structures from the builder module:

#### PAIN Messages
- `builder.customer_direct_debit_initiation` - pain.008.001.07
- `builder.mandate_initiation_request` - pain.009.001.05
- `builder.mandate_amendment_request` - pain.010.001.05
- `builder.mandate_cancellation_request` - pain.011.001.05

#### CAMT Messages
- `builder.bank_to_customer_statement` - camt.053.001.06
- `builder.bank_to_customer_debit_credit_notification` - camt.054.001.06

---

## Parser Module

**Import:** `from sepa import parser`

The parser module converts ISO 20022 XML messages into Python dictionaries.

### Functions

#### `parse(structure, tree)`

Parses an XML tree into a Python dictionary.

**Parameters:**
- `structure` (dict or None): The message structure definition. Pass `None` for auto-detection.
- `tree` (lxml.etree.Element): The XML tree to parse

**Returns:** `dict` - Parsed data with `document_type` key if auto-detected

**Example:**
```python
from sepa import parser
from lxml import etree

tree = etree.parse('statement.xml')
data = parser.parse(None, tree)  # Auto-detect
print(data['document_type'])
```

#### `parse_string(structure, xml_string, **kwargs)`

Parses an XML string into a Python dictionary.

**Parameters:**
- `structure` (dict or None): The message structure definition. Pass `None` for auto-detection.
- `xml_string` (str or bytes): The XML string to parse
- `**kwargs`: Additional arguments passed to `lxml.etree.fromstring()`

**Returns:** `dict` - Parsed data

**Example:**
```python
xml = '<Document xmlns="...">...</Document>'
data = parser.parse_string(None, xml)
```

#### `get_structure(tree)`

Auto-detects the message type from the XML namespace and returns the appropriate structure.

**Parameters:**
- `tree` (lxml.etree.Element): The XML tree

**Returns:** `dict` - The appropriate parser structure

**Raises:** `UnsupportedDocumentType` - If the document type is not recognized

**Example:**
```python
from lxml import etree
from sepa import parser

tree = etree.parse('unknown_message.xml')
try:
    structure = parser.get_structure(tree)
    print(f"Detected structure: {structure['_self']}")
except parser.UnsupportedDocumentType as e:
    print(f"Unknown type: {e}")
```

#### `reverse(structure, name='')`

Converts a builder structure definition to a parser structure definition. Used internally.

**Parameters:**
- `structure` (dict): Builder structure definition
- `name` (str, optional): Element name

**Returns:** `dict` - Parser structure definition

#### `parse_tree(structure, tag)`

Recursively parses an XML tree. Used internally by `parse()`.

**Parameters:**
- `structure` (dict): Parser structure definition
- `tag` (lxml.etree.Element): XML element to parse

**Returns:** `dict` - Parsed data

### Message Structure Attributes

Exported parser structures (reversed from builder structures):

#### PAIN Messages
- `parser.customer_direct_debit_initiation`
- `parser.mandate_initiation_request`
- `parser.mandate_amendment_request`
- `parser.mandate_cancellation_request`

#### CAMT Messages
- `parser.bank_to_customer_statement`
- `parser.bank_to_customer_debit_credit_notification`

---

## Validator Module

**Import:** `from sepa import validator`

The validator module validates XML messages against XSD schemas.

### Functions

#### `validate(schema_name, tree)`

Validates an XML tree against an XSD schema.

**Parameters:**
- `schema_name` (str): XSD schema filename (e.g., 'pain.008.001.07.xsd')
- `tree` (lxml.etree.Element): The XML tree to validate

**Returns:** `bool` - True if valid, False otherwise

**Example:**
```python
from sepa import builder, validator

xml_tree = builder.build(builder.customer_direct_debit_initiation, data)
is_valid = validator.validate(validator.customer_direct_debit_initiation, xml_tree)

if is_valid:
    print("Message is valid!")
else:
    print("Message is invalid!")
```

#### `validate_or_error(schema_name, tree)`

Validates an XML tree and raises an exception if invalid.

**Parameters:**
- `schema_name` (str): XSD schema filename
- `tree` (lxml.etree.Element): The XML tree to validate

**Returns:** `None` (returns nothing if valid)

**Raises:** `lxml.etree.DocumentInvalid` - If the XML is invalid

**Example:**
```python
from lxml.etree import DocumentInvalid
from sepa import builder, validator

try:
    xml_tree = builder.build(builder.customer_direct_debit_initiation, data)
    validator.validate_or_error(validator.customer_direct_debit_initiation, xml_tree)
    print("Valid!")
except DocumentInvalid as e:
    print(f"Validation error: {e}")
    print(f"Error log: {e.error_log}")
```

#### `get_schema(schema_name)`

Loads and caches an XSD schema.

**Parameters:**
- `schema_name` (str): XSD schema filename

**Returns:** `lxml.etree.XMLSchema` - The loaded schema

### Schema Attributes

Exported schema names for each message type:

#### PAIN Messages
- `validator.customer_direct_debit_initiation` - 'pain.008.001.07.xsd'
- `validator.mandate_initiation_request` - 'pain.009.001.05.xsd'
- `validator.mandate_amendment_request` - 'pain.010.001.05.xsd'
- `validator.mandate_cancellation_request` - 'pain.011.001.05.xsd'

#### CAMT Messages
- `validator.bank_to_customer_statement` - 'camt.053.001.06.xsd'
- `validator.bank_to_customer_debit_credit_notification` - 'camt.054.001.06.xsd'

---

## Signer Module

**Import:** `from sepa import signer`

The signer module provides XML digital signature functionality using the signxml library.

### Functions

#### `sign(tree, key, cert, **kwargs)`

Signs an XML tree with a digital certificate.

**Parameters:**
- `tree` (lxml.etree.Element): The XML tree to sign
- `key` (str): Private key in PEM format
- `cert` (str): Certificate in PEM format
- `**kwargs`: Additional arguments passed to `signxml.XMLSigner.sign()`

**Returns:** `lxml.etree.Element` - The signed XML tree

**Example:**
```python
from sepa import builder, signer

# Build message
xml_tree = builder.build(builder.customer_direct_debit_initiation, data)

# Load certificate and key
with open('cert.pem', 'r') as f:
    cert = f.read()
with open('key.pem', 'r') as f:
    key = f.read()

# Sign
signed_tree = signer.sign(xml_tree, key=key, cert=cert)
```

#### `verify(tree, **kwargs)`

Verifies the digital signature of an XML tree.

**Parameters:**
- `tree` (lxml.etree.Element): The signed XML tree
- `**kwargs`: Additional arguments passed to `signxml.XMLVerifier.verify()`

**Returns:** `bool` - True if signature is valid, False otherwise

**Example:**
```python
from lxml import etree
from sepa import signer

tree = etree.parse('signed_message.xml')
is_valid = signer.verify(tree)

if is_valid:
    print("Signature is valid!")
else:
    print("Signature is invalid!")
```

---

## Messages Module

**Import:** `from sepa.messages import sepa_messages`

The messages module contains all ISO 20022 message definitions.

### Structure

```python
sepa_messages = {
    'pain': {
        'customer_direct_debit_initiation': Message(...),
        'mandate_initiation_request': Message(...),
        'mandate_amendment_request': Message(...),
        'mandate_cancellation_request': Message(...)
    },
    'camt': {
        'bank_to_customer_statement': Message(...),
        'bank_to_customer_debit_credit_notification': Message(...)
    }
}
```

### Message Object

Each message has the following attributes:

- `name` (str): Canonical name (e.g., 'mandate_initiation_request')
- `standard` (str): ISO 20022 standard identifier (e.g., 'pain.009.001.05')
- `compatible_standards` (list): List of compatible version identifiers
- `definition` (dict): The message structure definition

**Example:**
```python
from sepa.messages import sepa_messages

# Access message info
msg = sepa_messages['pain']['mandate_initiation_request']
print(f"Name: {msg.name}")
print(f"Standard: {msg.standard}")
print(f"Compatible: {msg.compatible_standards}")
```

---

## Definitions Module

The definitions module provides reusable structure definitions for building messages.

### General Definitions

**Import:** `from sepa.definitions import general`

Common structures used across multiple message types:

#### Functions

- `general.code_or_proprietary(tag)` - Code or proprietary identifier structure
- `general.amount_field(tag)` - Amount with currency attribute
- `general.address(tag)` - Full address block
- `general.party(tag)` - Party identification (person/organization)
- `general.party_compat(tag)` - Party with ISO 20022 2019+ compatibility
- `general.agent(tag)` - Financial institution agent
- `general.account(tag)` - Bank account details
- `general.charges(tag)` - Transaction charges

### Payment Definitions

**Import:** `from sepa.definitions import payment`

Payment-specific structures:

#### Functions

- `payment.payment_group_header(tag)` - Payment initiation group header
- `payment.type_information(tag)` - Payment type information
- `payment.transaction(tag)` - Individual payment transaction
- `payment.payment(tag)` - Complete payment instruction

### Mandate Definitions

**Import:** `from sepa.definitions import mandate`

Mandate-specific structures:

#### Functions

- `mandate.mandate_group_header(tag)` - Mandate message group header
- `mandate.original_message(tag)` - Reference to original message
- `mandate.mandate(tag)` - Mandate details

### Statement Definitions

**Import:** `from sepa.definitions import statement`

Bank statement structures:

#### Functions

- `statement.statement_group_header(tag)` - Statement group header
- `statement.balance(tag)` - Account balance
- `statement.transactions_summary(tag)` - Transaction summary
- `statement.entry(tag)` - Bank statement entry
- `statement.interest_record(tag)` - Interest calculation
- `statement.statement(tag)` - Complete bank statement
- `statement.pagination(tag)` - Message pagination

### Notification Definitions

**Import:** `from sepa.definitions import notification`

Debit/credit notification structures:

#### Functions

- `notification.notification(tag)` - Debit or credit notification

---

## Data Structures

### Structure Definition Format

Message structures are defined as nested Python dictionaries with special keys:

#### Special Keys

| Key | Type | Description |
|-----|------|-------------|
| `_self` | str | The XML tag name for this element |
| `_namespaces` | dict | XML namespace mapping (only on root) |
| `_sorting` | list | Order of child elements in XML output |
| `_attribs` | dict | Mapping of data keys to XML attributes |
| `_nochildren` | bool | Indicates text-only element (no children) |

#### Example Structure

```python
{
    '_self': 'GrpHdr',
    '_sorting': ['MsgId', 'CreDtTm', 'InitgPty'],
    'message_id': 'MsgId',
    'creation_date_time': 'CreDtTm',
    'initiating_party': {
        '_self': 'InitgPty',
        'name': 'Nm'
    }
}
```

### Data Format

#### Simple Elements

```python
data = {
    'message_id': 'MSG001',
    'creation_date_time': '2024-01-15T10:30:00'
}
```

#### Elements with Attributes

Use `_value` for text content and `_attribs` for attributes:

```python
data = {
    'amount': {
        '_value': '100.00',
        '_attribs': {'currency': 'EUR'}
    }
}
```

#### Lists of Elements

```python
data = {
    'transaction': [
        {'id': 'TXN001', 'amount': '100.00'},
        {'id': 'TXN002', 'amount': '200.00'}
    ]
}
```

#### Nested Objects

```python
data = {
    'creditor': {
        'name': 'Company Name',
        'postal_address': {
            'country': 'DE',
            'address_line': ['Street 123', '12345 City']
        }
    }
}
```

---

## Exceptions

### `parser.UnsupportedDocumentType`

Raised when the parser encounters an unknown document type in the XML namespace.

**Example:**
```python
from sepa import parser

try:
    data = parser.parse_string(None, xml_with_unknown_type)
except parser.UnsupportedDocumentType as e:
    print(f"Unknown document type: {e}")
```

### `lxml.etree.DocumentInvalid`

Raised by `validator.validate_or_error()` when XML doesn't match the XSD schema.

**Attributes:**
- `error_log`: Detailed validation errors

**Example:**
```python
from lxml.etree import DocumentInvalid
from sepa import validator

try:
    validator.validate_or_error(schema, tree)
except DocumentInvalid as e:
    for error in e.error_log:
        print(f"Line {error.line}: {error.message}")
```

---

## Complete Example

```python
from sepa import builder, parser, validator, signer
from lxml import etree

# 1. Build a message
data = {
    'group_header': {
        'message_id': 'MSG001',
        'creation_date_time': '2024-01-15T10:30:00',
        'initiating_party': {'name': 'My Company'}
    },
    'mandate': [{
        'id': 'MNDT123',
        'request_id': 'REQ456',
        'authentication': {
            'date': '2024-01-15',
            'channel': {'code': 'ONLN'}
        }
    }]
}

# Build
xml_tree = builder.build(builder.mandate_initiation_request, data)

# 2. Validate
try:
    validator.validate_or_error(validator.mandate_initiation_request, xml_tree)
    print("✓ Valid message")
except Exception as e:
    print(f"✗ Invalid: {e}")

# 3. Sign (optional)
with open('cert.pem') as f:
    cert = f.read()
with open('key.pem') as f:
    key = f.read()

signed_tree = signer.sign(xml_tree, key=key, cert=cert)

# 4. Convert to string
xml_bytes = etree.tostring(signed_tree, pretty_print=True, xml_declaration=True, encoding='UTF-8')

# 5. Parse back
parsed_data = parser.parse(None, signed_tree)
print(f"Message ID: {parsed_data['group_header']['message_id']}")

# 6. Verify signature
if signer.verify(signed_tree):
    print("✓ Signature valid")
```

---

## See Also

- [Architecture Guide](ARCHITECTURE.md) - Design patterns and internals
- [Examples](EXAMPLES.md) - Comprehensive usage examples
- [README](../README.md) - Quick start and overview
