# Comprehensive Examples

This guide provides detailed, practical examples for using the python-sepa library.

## Table of Contents

- [Basic Examples](#basic-examples)
  - [Building a Simple Mandate](#building-a-simple-mandate)
  - [Parsing a Statement](#parsing-a-statement)
  - [Validating a Message](#validating-a-message)
- [PAIN Messages](#pain-messages)
  - [Customer Direct Debit Initiation (pain.008)](#customer-direct-debit-initiation-pain008)
  - [Mandate Initiation Request (pain.009)](#mandate-initiation-request-pain009)
  - [Mandate Amendment Request (pain.010)](#mandate-amendment-request-pain010)
  - [Mandate Cancellation Request (pain.011)](#mandate-cancellation-request-pain011)
- [CAMT Messages](#camt-messages)
  - [Bank to Customer Statement (camt.053)](#bank-to-customer-statement-camt053)
  - [Debit/Credit Notification (camt.054)](#debitcredit-notification-camt054)
- [Advanced Usage](#advanced-usage)
  - [Batch Processing](#batch-processing)
  - [Error Handling](#error-handling)
  - [Custom Namespaces](#custom-namespaces)
  - [Working with Files](#working-with-files)
- [Digital Signatures](#digital-signatures)
- [Integration Patterns](#integration-patterns)

---

## Basic Examples

### Building a Simple Mandate

Create a basic mandate initiation request:

```python
from sepa import builder

# Define the mandate data
data = {
    'group_header': {
        'message_id': 'MSG-2024-001',
        'creation_date_time': '2024-01-15T10:30:00',
        'number_of_mandates': 1,
        'initiating_party': {
            'name': 'Creditor Company Ltd'
        }
    },
    'mandate': [{
        'id': 'MNDT-2024-001',
        'request_id': 'REQ-2024-001',
        'authentication': {
            'date': '2024-01-15',
            'channel': {
                'code': 'ONLN'
            }
        },
        'type': {
            'service_level': {
                'code': 'SEPA'
            },
            'local_instrument': {
                'code': 'CORE'
            }
        },
        'creditor': {
            'name': 'Creditor Company Ltd',
            'identification': {
                'organisation_id': {
                    'other': {
                        'id': 'DE98ZZZ09999999999',
                        'scheme_name': {
                            'code': 'CUST'
                        }
                    }
                }
            }
        },
        'debtor': {
            'name': 'John Doe',
            'postal_address': {
                'country': 'DE',
                'address_line': ['Hauptstrasse 123', '10115 Berlin']
            }
        },
        'debtor_account': {
            'identification': {
                'iban': 'DE89370400440532013000'
            }
        }
    }]
}

# Build the XML
xml_tree = builder.build(builder.mandate_initiation_request, data)

# Convert to formatted string
from lxml import etree
xml_string = etree.tostring(
    xml_tree,
    pretty_print=True,
    xml_declaration=True,
    encoding='UTF-8'
)

print(xml_string.decode('utf-8'))
```

### Parsing a Statement

Parse a bank statement XML:

```python
from sepa import parser

xml_data = """<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.053.001.06">
    <BkToCstmrStmt>
        <GrpHdr>
            <MsgId>STMT-001</MsgId>
            <CreDtTm>2024-01-15T09:00:00</CreDtTm>
        </GrpHdr>
        <Stmt>
            <Id>STMT-2024-001</Id>
            <CreDtTm>2024-01-15T09:00:00</CreDtTm>
            <Acct>
                <Id>
                    <IBAN>DE89370400440532013000</IBAN>
                </Id>
            </Acct>
            <Bal>
                <Tp>
                    <CdOrPrtry>
                        <Cd>OPBD</Cd>
                    </CdOrPrtry>
                </Tp>
                <Amt Ccy="EUR">1000.00</Amt>
                <CdtDbtInd>CRDT</CdtDbtInd>
                <Dt>
                    <Dt>2024-01-15</Dt>
                </Dt>
            </Bal>
        </Stmt>
    </BkToCstmrStmt>
</Document>"""

# Parse with auto-detection
statement = parser.parse_string(None, xml_data)

# Access parsed data
print(f"Message ID: {statement['group_header']['message_id']}")
print(f"Statement ID: {statement['statement'][0]['id']}")
print(f"Account IBAN: {statement['statement'][0]['account']['identification']['iban']}")

balance = statement['statement'][0]['balance'][0]
print(f"Balance: {balance['amount']['_value']} {balance['amount']['_attribs']['currency']}")
```

### Validating a Message

Validate a message against XSD schema:

```python
from sepa import builder, validator
from lxml.etree import DocumentInvalid

# Build a message
data = {
    'group_header': {
        'message_id': 'MSG001',
        'creation_date_time': '2024-01-15T10:30:00',
        'number_of_mandates': 1,
        'initiating_party': {'name': 'Company'}
    },
    'mandate': [{
        'id': 'MNDT001',
        'request_id': 'REQ001'
    }]
}

xml_tree = builder.build(builder.mandate_initiation_request, data)

# Validate - boolean result
is_valid = validator.validate(validator.mandate_initiation_request, xml_tree)
print(f"Valid: {is_valid}")

# Validate with detailed errors
try:
    validator.validate_or_error(validator.mandate_initiation_request, xml_tree)
    print("✓ Message is valid!")
except DocumentInvalid as e:
    print("✗ Validation failed!")
    for error in e.error_log:
        print(f"  Line {error.line}: {error.message}")
```

---

## PAIN Messages

### Customer Direct Debit Initiation (pain.008)

Create a SEPA direct debit payment file:

```python
from sepa import builder
from datetime import datetime, timedelta

# Payment collection date (must be at least 5 business days in future for CORE)
collection_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')

data = {
    'group_header': {
        'message_id': f'MSG-{datetime.now().strftime("%Y%m%d-%H%M%S")}',
        'creation_date_time': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        'number_of_transactions': 2,
        'control_sum': 150.00,
        'initiating_party': {
            'name': 'Your Company GmbH',
            'identification': {
                'organisation_id': {
                    'other': {
                        'id': 'DE98ZZZ09999999999'
                    }
                }
            }
        }
    },
    'payment': [{
        'payment_id': 'PMT-001',
        'payment_method': 'DD',
        'batch_booking': False,
        'number_of_transactions': 2,
        'control_sum': 150.00,
        'payment_type_information': {
            'service_level': {
                'code': 'SEPA'
            },
            'local_instrument': {
                'code': 'CORE'
            },
            'sequence_type': 'RCUR'  # FRST, RCUR, OOFF, FNAL
        },
        'requested_collection_date': collection_date,
        'creditor': {
            'name': 'Your Company GmbH',
            'postal_address': {
                'country': 'DE',
                'address_line': ['Businessstr. 1', '10115 Berlin']
            }
        },
        'creditor_account': {
            'identification': {
                'iban': 'DE89370400440532013000'
            },
            'currency': 'EUR'
        },
        'creditor_agent': {
            'financial_institution_identification': {
                'bic': 'COBADEFFXXX'
            }
        },
        'creditor_scheme_identification': {
            'identification': {
                'private_id': {
                    'other': {
                        'id': 'DE98ZZZ09999999999',
                        'scheme_name': {
                            'proprietary': 'SEPA'
                        }
                    }
                }
            }
        },
        'transaction': [
            {
                'payment_id': {
                    'end_to_end_id': 'TXN-001'
                },
                'amount': {
                    '_value': '100.00',
                    '_attribs': {'currency': 'EUR'}
                },
                'direct_debit_transaction': {
                    'mandate_related_information': {
                        'mandate_id': 'MNDT-001',
                        'date_of_signature': '2023-06-15'
                    },
                    'creditor_scheme_identification': {
                        'identification': {
                            'private_id': {
                                'other': {
                                    'id': 'DE98ZZZ09999999999'
                                }
                            }
                        }
                    }
                },
                'debtor_agent': {
                    'financial_institution_identification': {
                        'bic': 'MARKDEF1100'
                    }
                },
                'debtor': {
                    'name': 'Customer One',
                    'postal_address': {
                        'country': 'DE',
                        'address_line': ['Street 1', '12345 City']
                    }
                },
                'debtor_account': {
                    'identification': {
                        'iban': 'DE89370400440532013001'
                    }
                },
                'remittance_information': {
                    'unstructured': ['Invoice 2024-001']
                }
            },
            {
                'payment_id': {
                    'end_to_end_id': 'TXN-002'
                },
                'amount': {
                    '_value': '50.00',
                    '_attribs': {'currency': 'EUR'}
                },
                'direct_debit_transaction': {
                    'mandate_related_information': {
                        'mandate_id': 'MNDT-002',
                        'date_of_signature': '2023-08-20'
                    }
                },
                'debtor_agent': {
                    'financial_institution_identification': {
                        'bic': 'DEUTDEFF500'
                    }
                },
                'debtor': {
                    'name': 'Customer Two'
                },
                'debtor_account': {
                    'identification': {
                        'iban': 'DE89370400440532013002'
                    }
                },
                'remittance_information': {
                    'unstructured': ['Subscription fee January 2024']
                }
            }
        ]
    }]
}

# Build and save
xml_tree = builder.build(builder.customer_direct_debit_initiation, data)

from lxml import etree
with open('direct_debit_payment.xml', 'wb') as f:
    f.write(etree.tostring(xml_tree, pretty_print=True, xml_declaration=True, encoding='UTF-8'))

print("Direct debit payment file created successfully!")
```

### Mandate Initiation Request (pain.009)

Request a new mandate from a debtor:

```python
from sepa import builder
from datetime import datetime

data = {
    'group_header': {
        'message_id': f'MNDT-REQ-{datetime.now().strftime("%Y%m%d%H%M%S")}',
        'creation_date_time': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        'number_of_mandates': 1,
        'initiating_party': {
            'name': 'Your Company GmbH',
            'identification': {
                'organisation_id': {
                    'other': {
                        'id': 'DE98ZZZ09999999999',
                        'scheme_name': {
                            'code': 'SEPA'
                        }
                    }
                }
            }
        }
    },
    'mandate': [{
        'id': 'MNDT-2024-12345',
        'request_id': f'REQ-{datetime.now().strftime("%Y%m%d%H%M%S")}',
        'authentication': {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'channel': {
                'code': 'ONLN'  # Online channel
            }
        },
        'occurrence': {
            'sequence_type': 'RCUR',  # Recurring
            'frequency': 'MNTH'  # Monthly
        },
        'type': {
            'service_level': {
                'code': 'SEPA'
            },
            'local_instrument': {
                'code': 'CORE'
            }
        },
        'creditor': {
            'name': 'Your Company GmbH',
            'postal_address': {
                'country': 'DE',
                'address_line': ['Businessstr. 1', '10115 Berlin']
            },
            'identification': {
                'organisation_id': {
                    'other': {
                        'id': 'DE98ZZZ09999999999',
                        'scheme_name': {
                            'code': 'SEPA'
                        }
                    }
                }
            }
        },
        'creditor_account': {
            'identification': {
                'iban': 'DE89370400440532013000'
            },
            'currency': 'EUR',
            'name': 'Your Company GmbH'
        },
        'debtor': {
            'name': 'John Doe',
            'postal_address': {
                'country': 'DE',
                'address_line': ['Hauptstrasse 123', '10115 Berlin']
            },
            'identification': {
                'private_id': {
                    'date_and_place_of_birth': {
                        'birth_date': '1985-03-15',
                        'city_of_birth': 'Berlin',
                        'country_of_birth': 'DE'
                    }
                }
            },
            'contact_details': {
                'email_address': 'john.doe@example.com',
                'mobile_number': '+49 160 12345678'
            }
        },
        'debtor_account': {
            'identification': {
                'iban': 'DE89370400440532013001'
            }
        },
        'reason': {
            'proprietary': 'Subscription Service'
        }
    }]
}

xml_tree = builder.build(builder.mandate_initiation_request, data)

from lxml import etree
print(etree.tostring(xml_tree, pretty_print=True, encoding='unicode'))
```

### Mandate Amendment Request (pain.010)

Amend an existing mandate:

```python
from sepa import builder
from datetime import datetime

data = {
    'group_header': {
        'message_id': f'AMND-{datetime.now().strftime("%Y%m%d%H%M%S")}',
        'creation_date_time': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        'number_of_mandates': 1,
        'initiating_party': {
            'name': 'Your Company GmbH'
        }
    },
    'mandate': [{
        'id': 'MNDT-2024-12345',  # Original mandate ID
        'request_id': f'AMND-REQ-{datetime.now().strftime("%Y%m%d%H%M%S")}',
        'authentication': {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'channel': {
                'code': 'ONLN'
            }
        },
        'original_message': {
            'message_id': 'MNDT-REQ-20240115103000',
            'message_name_id': 'pain.009.001.05',
            'creation_date_time': '2024-01-15T10:30:00'
        },
        'amendment': {
            'amendment_reason': {
                'reason': {
                    'code': 'MD01'  # Mandate-related information changed
                }
            },
            'original_creditor': {
                'name': 'Old Company Name Ltd'
            },
            'original_creditor_account': {
                'identification': {
                    'iban': 'DE89370400440532013000'
                }
            },
            'original_debtor': {
                'name': 'John Doe'
            },
            'original_debtor_account': {
                'identification': {
                    'iban': 'DE89370400440532013001'
                }
            }
        },
        'creditor': {
            'name': 'Your Company GmbH (New Name)',  # Updated
            'postal_address': {
                'country': 'DE',
                'address_line': ['New Address 456', '10115 Berlin']
            }
        },
        'creditor_account': {
            'identification': {
                'iban': 'DE89370400440532013000'  # Same IBAN
            }
        },
        'debtor': {
            'name': 'John Doe'
        },
        'debtor_account': {
            'identification': {
                'iban': 'DE89370400440532013001'
            }
        }
    }]
}

xml_tree = builder.build(builder.mandate_amendment_request, data)
```

### Mandate Cancellation Request (pain.011)

Cancel a mandate:

```python
from sepa import builder
from datetime import datetime

data = {
    'group_header': {
        'message_id': f'CANC-{datetime.now().strftime("%Y%m%d%H%M%S")}',
        'creation_date_time': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        'number_of_mandates': 1,
        'initiating_party': {
            'name': 'Your Company GmbH'
        }
    },
    'mandate': [{
        'id': 'MNDT-2024-12345',
        'request_id': f'CANC-REQ-{datetime.now().strftime("%Y%m%d%H%M%S")}',
        'cancellation_reason': {
            'reason': {
                'code': 'CUST'  # Requested by customer
            }
        },
        'original_message': {
            'message_id': 'MNDT-REQ-20240115103000',
            'message_name_id': 'pain.009.001.05',
            'creation_date_time': '2024-01-15T10:30:00'
        },
        'creditor': {
            'name': 'Your Company GmbH'
        },
        'debtor': {
            'name': 'John Doe'
        }
    }]
}

xml_tree = builder.build(builder.mandate_cancellation_request, data)

from lxml import etree
print("Mandate cancellation request created.")
print(etree.tostring(xml_tree, pretty_print=True, encoding='unicode'))
```

---

## CAMT Messages

### Bank to Customer Statement (camt.053)

Parse a bank statement:

```python
from sepa import parser
from lxml import etree

# Load statement from file
with open('bank_statement.xml', 'rb') as f:
    tree = etree.parse(f)

# Parse with auto-detection
statement = parser.parse(None, tree)

# Extract information
print(f"Statement from: {statement['group_header']['message_id']}")
print(f"Date: {statement['group_header']['creation_date_time']}")

for stmt in statement.get('statement', []):
    print(f"\nStatement ID: {stmt['id']}")
    print(f"Account: {stmt['account']['identification']['iban']}")

    # Print balances
    for balance in stmt.get('balance', []):
        bal_type = balance['type']['code_or_proprietary']['code']
        amount = balance['amount']['_value']
        currency = balance['amount']['_attribs']['currency']
        direction = balance['credit_debit_indicator']

        print(f"{bal_type} Balance: {amount} {currency} ({direction})")

    # Print entries
    for entry in stmt.get('entry', []):
        amt = entry['amount']['_value']
        ccy = entry['amount']['_attribs']['currency']
        direction = entry['credit_debit_indicator']
        booking_date = entry.get('booking_date', {}).get('date', 'N/A')

        print(f"\n  Entry: {amt} {ccy} ({direction}) on {booking_date}")

        # Transaction details
        for tx_detail in entry.get('transaction_details', []):
            refs = tx_detail.get('references', {})
            end_to_end = refs.get('end_to_end_id', 'N/A')

            parties = tx_detail.get('related_parties', {})
            debtor = parties.get('debtor', {}).get('name', 'N/A')
            creditor = parties.get('creditor', {}).get('name', 'N/A')

            remit_info = tx_detail.get('remittance_information', {})
            unstructured = remit_info.get('unstructured', [''])[0] if 'unstructured' in remit_info else 'N/A'

            print(f"    {end_to_end}: {debtor} → {creditor}")
            print(f"    Purpose: {unstructured}")
```

### Debit/Credit Notification (camt.054)

Parse payment notifications:

```python
from sepa import parser

xml_data = """<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.054.001.06">
    <BkToCstmrDbtCdtNtfctn>
        <GrpHdr>
            <MsgId>NOTIF-001</MsgId>
            <CreDtTm>2024-01-15T14:30:00</CreDtTm>
        </GrpHdr>
        <Ntfctn>
            <Id>NTFID-001</Id>
            <CreDtTm>2024-01-15T14:30:00</CreDtTm>
            <Acct>
                <Id>
                    <IBAN>DE89370400440532013000</IBAN>
                </Id>
            </Acct>
            <Ntry>
                <Amt Ccy="EUR">100.00</Amt>
                <CdtDbtInd>CRDT</CdtDbtInd>
                <Sts>BOOK</Sts>
                <BookgDt>
                    <Dt>2024-01-15</Dt>
                </BookgDt>
            </Ntry>
        </Ntfctn>
    </BkToCstmrDbtCdtNtfctn>
</Document>"""

notification = parser.parse_string(None, xml_data)

print(f"Notification ID: {notification['group_header']['message_id']}")

for notif in notification.get('notification', []):
    print(f"\nNotification: {notif['id']}")
    print(f"Account: {notif['account']['identification']['iban']}")

    for entry in notif.get('entry', []):
        amount = entry['amount']['_value']
        currency = entry['amount']['_attribs']['currency']
        direction = entry['credit_debit_indicator']
        status = entry['status']

        print(f"  {direction} {amount} {currency} - Status: {status}")
```

---

## Advanced Usage

### Batch Processing

Process multiple messages efficiently:

```python
from sepa import builder, validator
from datetime import datetime

def create_mandate_request(customer_data):
    """Create a mandate request for a single customer"""
    return {
        'group_header': {
            'message_id': f'MNDT-{customer_data["id"]}-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'creation_date_time': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            'number_of_mandates': 1,
            'initiating_party': {'name': 'Your Company GmbH'}
        },
        'mandate': [{
            'id': f'MNDT-{customer_data["id"]}',
            'request_id': f'REQ-{customer_data["id"]}',
            'authentication': {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'channel': {'code': 'ONLN'}
            },
            'creditor': {
                'name': 'Your Company GmbH',
                'identification': {
                    'organisation_id': {
                        'other': {'id': 'DE98ZZZ09999999999'}
                    }
                }
            },
            'debtor': {
                'name': customer_data['name'],
                'postal_address': {
                    'country': customer_data['country'],
                    'address_line': [customer_data['address']]
                }
            },
            'debtor_account': {
                'identification': {
                    'iban': customer_data['iban']
                }
            }
        }]
    }

# Batch process customers
customers = [
    {'id': '001', 'name': 'Customer One', 'iban': 'DE89370400440532013001', 'country': 'DE', 'address': 'Street 1'},
    {'id': '002', 'name': 'Customer Two', 'iban': 'DE89370400440532013002', 'country': 'DE', 'address': 'Street 2'},
    {'id': '003', 'name': 'Customer Three', 'iban': 'DE89370400440532013003', 'country': 'DE', 'address': 'Street 3'},
]

results = {'success': [], 'failed': []}

for customer in customers:
    try:
        # Build message
        data = create_mandate_request(customer)
        xml_tree = builder.build(builder.mandate_initiation_request, data)

        # Validate
        if validator.validate(validator.mandate_initiation_request, xml_tree):
            results['success'].append(customer['id'])

            # Save to file
            from lxml import etree
            filename = f'mandate_{customer["id"]}.xml'
            with open(filename, 'wb') as f:
                f.write(etree.tostring(xml_tree, pretty_print=True, xml_declaration=True, encoding='UTF-8'))
        else:
            results['failed'].append((customer['id'], 'Validation failed'))

    except Exception as e:
        results['failed'].append((customer['id'], str(e)))

print(f"Successfully processed: {len(results['success'])}")
print(f"Failed: {len(results['failed'])}")
for customer_id, error in results['failed']:
    print(f"  {customer_id}: {error}")
```

### Error Handling

Comprehensive error handling:

```python
from sepa import builder, validator, parser
from lxml.etree import DocumentInvalid, XMLSyntaxError

def safe_build_and_validate(structure, data, schema):
    """Safely build and validate a SEPA message with detailed error reporting"""
    try:
        # Build the message
        xml_tree = builder.build(structure, data)

        # Validate
        validator.validate_or_error(schema, xml_tree)

        return {'success': True, 'tree': xml_tree}

    except KeyError as e:
        return {
            'success': False,
            'error_type': 'Missing Data',
            'message': f'Required field missing: {e}'
        }

    except DocumentInvalid as e:
        return {
            'success': False,
            'error_type': 'Validation Error',
            'message': 'XML does not match schema',
            'details': [f"Line {err.line}: {err.message}" for err in e.error_log]
        }

    except Exception as e:
        return {
            'success': False,
            'error_type': type(e).__name__,
            'message': str(e)
        }

def safe_parse(xml_data):
    """Safely parse SEPA XML with error handling"""
    try:
        data = parser.parse_string(None, xml_data)
        return {'success': True, 'data': data}

    except parser.UnsupportedDocumentType as e:
        return {
            'success': False,
            'error_type': 'Unsupported Document',
            'message': f'Unknown document type: {e}'
        }

    except XMLSyntaxError as e:
        return {
            'success': False,
            'error_type': 'XML Syntax Error',
            'message': f'Invalid XML: {e}'
        }

    except Exception as e:
        return {
            'success': False,
            'error_type': type(e).__name__,
            'message': str(e)
        }

# Usage
mandate_data = {'group_header': {'message_id': 'MSG001'}}

result = safe_build_and_validate(
    builder.mandate_initiation_request,
    mandate_data,
    validator.mandate_initiation_request
)

if result['success']:
    print("✓ Message built and validated successfully")
else:
    print(f"✗ {result['error_type']}: {result['message']}")
    if 'details' in result:
        for detail in result['details']:
            print(f"  - {detail}")
```

### Custom Namespaces

Override default namespaces:

```python
from sepa import builder

data = {
    'group_header': {'message_id': 'MSG001'},
    'mandate': [{'id': 'MNDT001', 'request_id': 'REQ001'}]
}

# Custom namespace mapping
custom_namespaces = {
    '': 'urn:iso:std:iso:20022:tech:xsd:pain.009.001.05',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'custom': 'http://example.com/custom'
}

# Build with custom namespaces
xml_tree = builder.build(
    builder.mandate_initiation_request,
    data,
    document=True,
    namespaces=custom_namespaces
)

from lxml import etree
print(etree.tostring(xml_tree, pretty_print=True, encoding='unicode'))
```

### Working with Files

Read from and write to files:

```python
from sepa import builder, parser, validator
from lxml import etree
import os

# Build and save
def save_sepa_message(structure, data, filename):
    """Build a SEPA message and save to file"""
    xml_tree = builder.build(structure, data)

    with open(filename, 'wb') as f:
        f.write(etree.tostring(
            xml_tree,
            pretty_print=True,
            xml_declaration=True,
            encoding='UTF-8'
        ))

    print(f"Saved: {filename}")

# Load and parse
def load_sepa_message(filename):
    """Load and parse a SEPA message from file"""
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File not found: {filename}")

    with open(filename, 'rb') as f:
        tree = etree.parse(f)

    data = parser.parse(None, tree)
    return data

# Load, modify, and save
def modify_message_id(input_file, output_file, new_message_id):
    """Load a message, modify its ID, and save"""
    # Parse existing file
    data = load_sepa_message(input_file)

    # Modify
    data['group_header']['message_id'] = new_message_id

    # Determine structure type from document_type
    doc_type = data.get('document_type', '')
    structure = parser.get_structure(etree.parse(input_file).getroot())

    # Build and save
    xml_tree = builder.build(structure, data)

    with open(output_file, 'wb') as f:
        f.write(etree.tostring(xml_tree, pretty_print=True, xml_declaration=True, encoding='UTF-8'))

    print(f"Modified message saved to: {output_file}")

# Usage
mandate_data = {
    'group_header': {'message_id': 'MSG001'},
    'mandate': [{'id': 'MNDT001', 'request_id': 'REQ001'}]
}

save_sepa_message(builder.mandate_initiation_request, mandate_data, 'mandate.xml')
loaded_data = load_sepa_message('mandate.xml')
print(f"Loaded message ID: {loaded_data['group_header']['message_id']}")
```

---

## Digital Signatures

### Signing Messages

Sign a SEPA message with a digital certificate:

```python
from sepa import builder, signer
from lxml import etree

# Build message
data = {
    'group_header': {'message_id': 'MSG001'},
    'mandate': [{'id': 'MNDT001', 'request_id': 'REQ001'}]
}

xml_tree = builder.build(builder.mandate_initiation_request, data)

# Load certificate and private key
with open('certificate.pem', 'r') as f:
    certificate = f.read()

with open('private_key.pem', 'r') as f:
    private_key = f.read()

# Sign the message
signed_tree = signer.sign(xml_tree, key=private_key, cert=certificate)

# Save signed message
with open('mandate_signed.xml', 'wb') as f:
    f.write(etree.tostring(signed_tree, pretty_print=True, xml_declaration=True, encoding='UTF-8'))

print("Message signed and saved!")
```

### Verifying Signatures

Verify a signed message:

```python
from sepa import signer
from lxml import etree

# Load signed message
with open('mandate_signed.xml', 'rb') as f:
    signed_tree = etree.parse(f).getroot()

# Verify signature
is_valid = signer.verify(signed_tree)

if is_valid:
    print("✓ Signature is valid!")
else:
    print("✗ Signature verification failed!")
```

---

## Integration Patterns

### REST API Integration

Expose SEPA functionality via REST API:

```python
from flask import Flask, request, jsonify, send_file
from sepa import builder, parser, validator
from lxml import etree
import tempfile

app = Flask(__name__)

@app.route('/api/mandate/create', methods=['POST'])
def create_mandate():
    """Create a SEPA mandate from JSON"""
    try:
        data = request.json

        # Build XML
        xml_tree = builder.build(builder.mandate_initiation_request, data)

        # Validate
        if not validator.validate(validator.mandate_initiation_request, xml_tree):
            return jsonify({'error': 'Validation failed'}), 400

        # Convert to string
        xml_bytes = etree.tostring(xml_tree, pretty_print=True, xml_declaration=True, encoding='UTF-8')

        # Save to temp file and return
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.xml') as f:
            f.write(xml_bytes)
            temp_path = f.name

        return send_file(temp_path, mimetype='application/xml', as_attachment=True, download_name='mandate.xml')

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/statement/parse', methods=['POST'])
def parse_statement():
    """Parse a SEPA statement XML to JSON"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        xml_content = file.read()

        # Parse
        data = parser.parse_string(None, xml_content)

        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

### Database Integration

Store and retrieve SEPA messages:

```python
import sqlite3
from sepa import builder, parser
from lxml import etree
from datetime import datetime

class SEPADatabase:
    def __init__(self, db_path='sepa_messages.db'):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT UNIQUE,
                message_type TEXT,
                xml_content TEXT,
                created_at TIMESTAMP,
                status TEXT
            )
        ''')
        self.conn.commit()

    def store_message(self, structure, data, message_type):
        """Build and store a SEPA message"""
        xml_tree = builder.build(structure, data)
        xml_string = etree.tostring(xml_tree, encoding='unicode')

        message_id = data['group_header']['message_id']

        self.conn.execute('''
            INSERT INTO messages (message_id, message_type, xml_content, created_at, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (message_id, message_type, xml_string, datetime.now(), 'pending'))

        self.conn.commit()
        return message_id

    def retrieve_message(self, message_id):
        """Retrieve and parse a stored message"""
        cursor = self.conn.execute('''
            SELECT xml_content FROM messages WHERE message_id = ?
        ''', (message_id,))

        row = cursor.fetchone()
        if row:
            xml_string = row[0]
            data = parser.parse_string(None, xml_string)
            return data
        return None

    def update_status(self, message_id, status):
        """Update message status"""
        self.conn.execute('''
            UPDATE messages SET status = ? WHERE message_id = ?
        ''', (status, message_id))
        self.conn.commit()

# Usage
db = SEPADatabase()

mandate_data = {
    'group_header': {'message_id': 'MSG-DB-001'},
    'mandate': [{'id': 'MNDT001', 'request_id': 'REQ001'}]
}

# Store
msg_id = db.store_message(builder.mandate_initiation_request, mandate_data, 'pain.009')
print(f"Stored message: {msg_id}")

# Retrieve
retrieved = db.retrieve_message('MSG-DB-001')
print(f"Retrieved: {retrieved['group_header']['message_id']}")

# Update status
db.update_status('MSG-DB-001', 'sent')
```

---

## See Also

- [API Reference](API_REFERENCE.md) - Detailed API documentation
- [Architecture Guide](ARCHITECTURE.md) - Design patterns and internals
- [README](../README.md) - Quick start and overview
