# Python SEPA Library

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE.md)
[![Python 3.x](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/)

A comprehensive Python library for parsing, building, validating, and signing SEPA (Single Euro Payments Area) Direct Debit and eMandate schemas based on ISO 20022 standards.

## Features

- **Build** SEPA XML messages from Python dictionaries
- **Parse** SEPA XML messages into Python dictionaries
- **Validate** messages against XSD schemas
- **Sign and verify** XML messages with digital certificates
- **Auto-detect** document types from XML namespaces
- **Support** for multiple compatible versions of each standard

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Supported Messages](#supported-messages)
- [Usage](#usage)
  - [Building Messages](#building-messages)
  - [Parsing Messages](#parsing-messages)
  - [Validating Messages](#validating-messages)
  - [Signing Messages](#signing-messages)
  - [Auto-detecting Message Types](#auto-detecting-message-types)
- [Documentation](#documentation)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Installation

### From PyPI (when available)

```bash
pip install sepa
```

### From Source

```bash
git clone https://github.com/VerenigingCampusKabel/python-sepa.git
cd python-sepa
pip install -e .
```

### Dependencies

**Required:**
- `lxml >= 3.5.0` - XML processing and validation

**Optional:**
- `signxml` - For XML digital signing and verification

**Development:**
- `nose` - Test runner
- `deep` - Deep comparison utilities
- `xmltodict` - XML to dictionary conversion for testing

## Quick Start

### Building a SEPA Message

```python
from sepa import builder

# Define payment data
payment_data = {
    'group_header': {
        'message_id': 'MSG001',
        'creation_date_time': '2024-01-15T10:30:00',
        'number_of_transactions': 1,
        'control_sum': 100.00,
        'initiating_party': {
            'name': 'Your Company Name'
        }
    },
    'payment': [{
        'payment_id': 'PMT001',
        'payment_method': 'DD',
        'requested_collection_date': '2024-01-20',
        'creditor': {
            'name': 'Your Company',
            'iban': 'DE89370400440532013000'
        },
        'transaction': [{
            'end_to_end_id': 'TXN001',
            'amount': {
                '_value': '100.00',
                '_attribs': {'currency': 'EUR'}
            },
            'debtor': {
                'name': 'Customer Name',
                'iban': 'GB82WEST12345698765432'
            }
        }]
    }]
}

# Build XML message
xml_tree = builder.build(builder.customer_direct_debit_initiation, payment_data)

# Or get as string
xml_string = builder.build_string(builder.customer_direct_debit_initiation, payment_data)
```

### Parsing a SEPA Message

```python
from sepa import parser

xml_data = """
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.009.001.05">
    <MndtInitnReq>
        <GrpHdr>
            <MsgId>MSG123</MsgId>
            <CreDtTm>2024-01-15T10:30:00</CreDtTm>
        </GrpHdr>
        <Mndt>
            <MndtId>MNDT001</MndtId>
            <MndtReqId>REQ001</MndtReqId>
        </Mndt>
    </MndtInitnReq>
</Document>
"""

# Parse with auto-detection
parsed_data = parser.parse_string(None, xml_data)
print(parsed_data)

# Or parse with explicit structure
parsed_data = parser.parse_string(parser.mandate_initiation_request, xml_data)
```

## Supported Messages

The library aims to support all [ISO 20022 Payments messages](https://www.iso20022.org/payments_messages.page), with focus on SEPA-relevant messages.

### Cash Management (CAMT)

| Message | Status | Description |
|---------|--------|-------------|
| camt.052.001.06 | ⬜ Planned | Bank To Customer Account Report v6 |
| **camt.053.001.06** | ✅ **Supported** | **Bank To Customer Statement v6** |
| **camt.054.001.06** | ✅ **Supported** | **Bank To Customer Debit Credit Notification v6** |
| camt.060.001.03 | ⬜ Planned | Account Reporting Request v3 |

**Compatible versions:**
- camt.053: 001.04, 001.06, 001.08
- camt.054: 001.04, 001.06, 001.08

### Payments Initiation (PAIN)

| Message | Status | Description |
|---------|--------|-------------|
| pain.001.001.08 | ⬜ Planned | Customer Credit Transfer Initiation v8 |
| pain.002.001.08 | ⬜ Planned | Customer Payment Status Report v8 |
| pain.007.001.07 | ⬜ Planned | Customer Payment Reversal v7 |
| **pain.008.001.07** | ✅ **Supported** | **Customer Direct Debit Initiation v7** |
| **pain.009.001.05** | ✅ **Supported** | **Mandate Initiation Request v5** |
| **pain.010.001.05** | ✅ **Supported** | **Mandate Amendment Request v5** |
| **pain.011.001.05** | ✅ **Supported** | **Mandate Cancellation Request v5** |
| pain.012.001.05 | ⬜ Planned | Mandate Acceptance Report v5 |
| pain.013.001.06 | ⬜ Planned | Creditor Payment Activation Request v6 |
| pain.014.001.06 | ⬜ Planned | Creditor Payment Activation Request Status Report v6 |
| pain.017.001.01 | ⬜ Planned | Mandate Copy Request v1 |
| pain.018.001.01 | ⬜ Planned | Mandate Suspension Request v1 |

## Usage

### Building Messages

The library converts Python dictionaries into ISO 20022 compliant XML messages.

```python
from sepa import builder

# Simple mandate initiation
mandate_data = {
    'group_header': {
        'message_id': 'MSG001',
        'creation_date_time': '2024-01-15T10:30:00',
        'initiating_party': {
            'name': 'Your Company'
        }
    },
    'mandate': [{
        'id': 'MNDT123',
        'request_id': 'REQ456',
        'authentication': {
            'date': '2024-01-15',
            'channel': {
                'code': 'ONLN'
            }
        },
        'creditor': {
            'name': 'Your Company',
            'identification': {
                'organisation_id': {
                    'other': {
                        'id': 'DE98ZZZ09999999999'
                    }
                }
            }
        },
        'debtor': {
            'name': 'Customer Name',
            'postal_address': {
                'country': 'DE',
                'address_line': ['Street 123', '12345 City']
            }
        }
    }]
}

# Build as lxml etree
xml_tree = builder.build(builder.mandate_initiation_request, mandate_data)

# Build as formatted byte string
xml_bytes = builder.build_string(
    builder.mandate_initiation_request,
    mandate_data,
    pretty_print=True,
    xml_declaration=True,
    encoding='UTF-8'
)

print(xml_bytes.decode('utf-8'))
```

### Parsing Messages

Parse XML messages back into Python dictionaries:

```python
from sepa import parser
from lxml import etree

# Parse from string with auto-detection
xml_string = """<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.053.001.06">
    <!-- Your XML content -->
</Document>"""

data = parser.parse_string(None, xml_string)

# Parse from file
with open('statement.xml', 'rb') as f:
    tree = etree.parse(f)
    data = parser.parse(None, tree)

# Parse with explicit structure (faster if you know the type)
data = parser.parse_string(parser.bank_to_customer_statement, xml_string)

# Access parsed data
print(f"Message ID: {data['group_header']['message_id']}")
print(f"Document Type: {data.get('document_type')}")
```

### Validating Messages

Validate XML messages against XSD schemas:

```python
from sepa import builder, validator

# Build a message
payment_data = { /* your payment data */ }
xml_tree = builder.build(builder.customer_direct_debit_initiation, payment_data)

# Validate - returns True/False
is_valid = validator.validate(validator.customer_direct_debit_initiation, xml_tree)
print(f"Valid: {is_valid}")

# Validate with error details
from lxml.etree import DocumentInvalid
try:
    validator.validate_or_error(validator.customer_direct_debit_initiation, xml_tree)
    print("Message is valid!")
except DocumentInvalid as e:
    print(f"Validation error: {e}")
```

### Signing Messages

Sign and verify XML messages with digital certificates:

```python
from sepa import builder, signer
from lxml import etree

# Build your message
payment_data = { /* your payment data */ }
xml_tree = builder.build(builder.customer_direct_debit_initiation, payment_data)

# Load your certificate and key
with open('certificate.pem', 'r') as cert_file:
    cert = cert_file.read()

with open('private_key.pem', 'r') as key_file:
    key = key_file.read()

# Sign the message
signed_tree = signer.sign(xml_tree, key=key, cert=cert)

# Save signed message
with open('signed_payment.xml', 'wb') as f:
    f.write(etree.tostring(signed_tree, pretty_print=True))

# Verify a signed message
is_verified = signer.verify(signed_tree)
print(f"Signature verified: {is_verified}")
```

### Auto-detecting Message Types

The parser can automatically detect the message type from the XML namespace:

```python
from sepa import parser

# Parser automatically detects the message type
xml_with_namespace = """
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.008.001.07">
    <!-- Content -->
</Document>
"""

# Pass None as structure for auto-detection
data = parser.parse_string(None, xml_with_namespace)

# The document_type is included in parsed data
print(f"Detected type: {data['document_type']}")
```

## Documentation

Comprehensive documentation is available:

- **[API Reference](docs/API_REFERENCE.md)** - Detailed API documentation
- **[Architecture Guide](docs/ARCHITECTURE.md)** - Design patterns and internals
- **[Examples](docs/EXAMPLES.md)** - Comprehensive usage examples
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute

## Testing

Run the test suite:

```bash
# Install test dependencies
pip install -e .[test]

# Run tests
python -m nose tests/

# Or with coverage
python -m nose --with-coverage --cover-package=sepa tests/
```

## Contributing

Contributions are welcome! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:

- Setting up the development environment
- Code style guidelines
- How to submit pull requests
- Adding support for new message types

## Roadmap

- [ ] Complete support for all PAIN message types
- [ ] Add support for PACS (Payments Clearing and Settlement) messages
- [ ] Improve digital signing/verification features
- [ ] Add more comprehensive validation beyond XSD
- [ ] Performance optimizations for large message batches
- [ ] Command-line interface for common operations

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Authors

**Vereniging Campus Kabel**
- Email: info@vck.utwente.nl
- Website: https://github.com/VerenigingCampusKabel/python-sepa

## Acknowledgments

- Based on [ISO 20022 Standards](https://www.iso20022.org/)
- Uses [lxml](https://lxml.de/) for XML processing
- Uses [signxml](https://github.com/XML-Security/signxml) for digital signatures

## Support

For bug reports and feature requests, please use the [GitHub issue tracker](https://github.com/VerenigingCampusKabel/python-sepa/issues).

## Related Projects

- [ISO 20022 Message Definitions](https://www.iso20022.org/iso-20022-message-definitions)
- [SEPA for Germany](https://www.sepadeutschland.de/)
- [European Payments Council](https://www.europeanpaymentscouncil.eu/)
