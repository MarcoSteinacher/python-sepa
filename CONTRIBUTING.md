# Contributing to Python-SEPA

Thank you for your interest in contributing to python-sepa! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [How to Contribute](#how-to-contribute)
- [Adding New Message Types](#adding-new-message-types)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Pull Requests](#submitting-pull-requests)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

This project follows a standard code of conduct:

- Be respectful and inclusive
- Welcome newcomers and be patient
- Focus on constructive feedback
- Respect differing viewpoints and experiences
- Accept responsibility and apologize for mistakes

## Getting Started

### Prerequisites

- Python 3.6 or higher
- Git
- Basic understanding of ISO 20022 standards (helpful but not required)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:

```bash
git clone https://github.com/YOUR-USERNAME/python-sepa.git
cd python-sepa
```

3. Add the upstream repository:

```bash
git remote add upstream https://github.com/VerenigingCampusKabel/python-sepa.git
```

## Development Environment

### Install Dependencies

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e .[test]

# Or install manually
pip install nose deep xmltodict
```

### Verify Installation

```bash
# Run tests to verify setup
python -m nose tests/

# Try importing the library
python -c "from sepa import builder, parser; print('Success!')"
```

## How to Contribute

There are many ways to contribute:

### 1. Code Contributions

- Add support for new ISO 20022 message types
- Improve existing message definitions
- Fix bugs
- Optimize performance
- Improve error handling

### 2. Documentation

- Fix typos or unclear explanations
- Add examples
- Improve API documentation
- Translate documentation

### 3. Testing

- Add test cases
- Report bugs
- Test on different Python versions
- Validate against real bank implementations

### 4. Community

- Answer questions in issues
- Review pull requests
- Share usage examples
- Improve project tooling

## Adding New Message Types

One of the most valuable contributions is adding support for new ISO 20022 message types.

### Step-by-Step Guide

#### 1. Research the Message Type

- Download the XSD schema from [ISO 20022 website](https://www.iso20022.org/)
- Study the message structure and required fields
- Check SEPA implementation guidelines if applicable

#### 2. Create the Message Definition File

Create a new file in the appropriate directory:

```bash
# For PAIN messages
touch sepa/messages/pain/pain001.py

# For CAMT messages
touch sepa/messages/camt/camt052.py

# For PACS messages (create directory first)
mkdir -p sepa/messages/pacs
touch sepa/messages/pacs/pacs008.py
```

#### 3. Define the Message Structure

```python
# sepa/messages/pain/pain001.py

from sepa.definitions import payment, general

# Required metadata
name = 'customer_credit_transfer_initiation'
standard = 'pain.001.001.08'
compatible_standards = ['pain.001.001.03', 'pain.001.001.09']  # Optional

# Message structure definition
definition = {
    '_self': 'CstmrCdtTrfInitn',
    '_namespaces': {
        '': 'urn:iso:std:iso:20022:tech:xsd:pain.001.001.08',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    },
    '_sorting': ['GrpHdr', 'PmtInf'],

    'group_header': payment.payment_group_header('GrpHdr'),
    'payment_information': [{
        '_self': 'PmtInf',
        '_sorting': ['PmtInfId', 'PmtMtd', 'PmtTpInf', 'ReqdExctnDt', 'Dbtr', 'DbtrAcct', 'DbtrAgt', 'CdtTrfTxInf'],

        'payment_information_id': 'PmtInfId',
        'payment_method': 'PmtMtd',
        'payment_type_information': payment.type_information('PmtTpInf'),
        'requested_execution_date': 'ReqdExctnDt',
        'debtor': general.party('Dbtr'),
        'debtor_account': general.account('DbtrAcct'),
        'debtor_agent': general.agent('DbtrAgt'),
        'credit_transfer_transaction': [payment.transaction('CdtTrfTxInf')]
    }]
}
```

#### 4. Add the XSD Schema

Place the XSD schema file in `sepa/schemas/`:

```bash
cp pain.001.001.08.xsd sepa/schemas/
```

#### 5. Create Tests

Create a test file in `tests/`:

```python
# tests/test_pain001.py

from sepa import builder, parser, validator
from lxml import etree

def test_pain001_build():
    """Test building a pain.001 message"""
    data = {
        'group_header': {
            'message_id': 'MSG001',
            'creation_date_time': '2024-01-15T10:30:00',
            'number_of_transactions': 1,
            'initiating_party': {'name': 'Test Company'}
        },
        'payment_information': [{
            'payment_information_id': 'PMT001',
            'payment_method': 'TRF',
            'requested_execution_date': '2024-01-20',
            'debtor': {'name': 'Debtor Name'},
            'debtor_account': {
                'identification': {'iban': 'DE89370400440532013000'}
            }
        }]
    }

    xml_tree = builder.build(builder.customer_credit_transfer_initiation, data)
    assert xml_tree is not None

def test_pain001_validate():
    """Test validation of pain.001 message"""
    # Build a complete valid message
    data = { /* complete data */ }
    xml_tree = builder.build(builder.customer_credit_transfer_initiation, data)

    # Should validate successfully
    assert validator.validate(validator.customer_credit_transfer_initiation, xml_tree)

def test_pain001_round_trip():
    """Test build and parse round-trip"""
    data = { /* data */ }

    # Build
    xml_tree = builder.build(builder.customer_credit_transfer_initiation, data)

    # Parse back
    parsed_data = parser.parse(None, xml_tree)

    # Verify key fields match
    assert parsed_data['group_header']['message_id'] == data['group_header']['message_id']
```

#### 6. Run Tests

```bash
python -m nose tests/test_pain001.py
```

#### 7. Update Documentation

Add your new message type to:
- `README.md` - Supported messages section
- `docs/EXAMPLES.md` - Usage examples

### Adding Reusable Definitions

If you need to create reusable structure components:

```python
# sepa/definitions/mycategory.py

def my_structure(tag):
    """
    Generates a reusable structure definition.

    Args:
        tag (str): The XML tag name

    Returns:
        dict: Structure definition
    """
    return {
        '_self': tag,
        '_sorting': ['Field1', 'Field2'],
        'field1': 'Field1',
        'field2': {
            '_self': 'Field2',
            'subfield': 'Subfield'
        }
    }
```

## Code Style Guidelines

### Python Style

Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide:

```python
# Good
def payment_group_header(tag):
    """Generate payment group header structure."""
    return {
        '_self': tag,
        'message_id': 'MsgId'
    }

# Bad
def PaymentGroupHeader(Tag):
    return {'_self':Tag,'message_id':'MsgId'}
```

### Structure Definitions

**Consistent formatting:**

```python
definition = {
    '_self': 'ElementName',
    '_namespaces': {
        '': 'urn:iso:std:iso:20022:tech:xsd:pain.008.001.07'
    },
    '_sorting': ['Field1', 'Field2', 'Field3'],

    'field_one': 'Field1',
    'field_two': 'Field2',
    'nested_field': {
        '_self': 'Field3',
        'subfield': 'Subfield'
    }
}
```

**Key conventions:**

- Use snake_case for data keys
- Use exact ISO 20022 tag names for XML tags
- Group special keys (`_self`, `_sorting`, etc.) at the top
- Add blank lines between major sections
- Include `_sorting` for all elements with multiple children

### Docstrings

Use descriptive docstrings:

```python
def party(tag):
    """
    Generate a party identification structure.

    This structure is used to identify individuals or organizations
    in SEPA messages, including name, address, and identification details.

    Args:
        tag (str): The XML tag name for the party element

    Returns:
        dict: Structure definition for a party

    Example:
        >>> creditor = party('Cdtr')
        >>> data = {'name': 'Company Ltd'}
        >>> xml = builder.build_tree(creditor, data)
    """
    return {
        '_self': tag,
        'name': 'Nm',
        'postal_address': address('PstlAdr')
    }
```

### Comments

Add comments for complex logic:

```python
# Sort children according to ISO 20022 specification
if '_sorting' in structure:
    tag[:] = sorted(tag, key=lambda el: structure['_sorting'].index(el.tag))

# Handle list elements - can be single item or array
if isinstance(subdata, list):
    for d in subdata:
        tag.append(build_child(structure[child][0], d))
else:
    tag.append(build_child(structure[child][0], subdata))
```

## Testing

### Running Tests

```bash
# Run all tests
python -m nose tests/

# Run specific test file
python -m nose tests/test_parser.py

# Run with coverage
python -m nose --with-coverage --cover-package=sepa tests/

# Run specific test
python -m nose tests/test_builder.py:TestBuilder.test_simple_build
```

### Writing Tests

Tests should cover:

1. **Building** - Can structures be converted to XML?
2. **Parsing** - Can XML be converted back to data?
3. **Validation** - Does the XML pass XSD validation?
4. **Round-trip** - Build → Parse → Compare with original
5. **Edge cases** - Empty fields, optional fields, lists

Example test structure:

```python
import unittest
from sepa import builder, parser, validator
from lxml import etree

class TestMyMessage(unittest.TestCase):

    def setUp(self):
        """Set up test data"""
        self.valid_data = {
            'group_header': {'message_id': 'MSG001'}
        }

    def test_build(self):
        """Test building message"""
        xml_tree = builder.build(builder.my_message, self.valid_data)
        self.assertIsNotNone(xml_tree)
        self.assertEqual(xml_tree.tag, 'Document')

    def test_parse(self):
        """Test parsing message"""
        xml_tree = builder.build(builder.my_message, self.valid_data)
        parsed = parser.parse(None, xml_tree)
        self.assertEqual(parsed['group_header']['message_id'], 'MSG001')

    def test_validate(self):
        """Test validation"""
        xml_tree = builder.build(builder.my_message, self.valid_data)
        self.assertTrue(validator.validate(validator.my_message, xml_tree))

    def test_round_trip(self):
        """Test build → parse → compare"""
        xml_tree = builder.build(builder.my_message, self.valid_data)
        parsed = parser.parse(None, xml_tree)

        # Rebuild from parsed data
        xml_tree2 = builder.build(builder.my_message, parsed)

        # Should produce identical XML
        xml1 = etree.tostring(xml_tree, encoding='unicode')
        xml2 = etree.tostring(xml_tree2, encoding='unicode')
        self.assertEqual(xml1, xml2)
```

## Documentation

### Code Documentation

- Add docstrings to all public functions
- Include parameter types and descriptions
- Provide usage examples
- Document exceptions

### User Documentation

When adding features, update:

- `README.md` - If it affects the API or adds major features
- `docs/API_REFERENCE.md` - For new functions or modules
- `docs/EXAMPLES.md` - Add practical examples
- `docs/ARCHITECTURE.md` - For architectural changes

### Commit Messages

Write clear commit messages:

```
Add support for pain.001.001.08 (Customer Credit Transfer)

- Created message definition in sepa/messages/pain/pain001.py
- Added XSD schema to sepa/schemas/
- Implemented comprehensive tests
- Updated documentation with examples

Resolves #123
```

Format:
- First line: Brief summary (50 chars or less)
- Blank line
- Detailed description
- Reference issues with `Resolves #123` or `Fixes #456`

## Submitting Pull Requests

### Before Submitting

1. **Test your changes:**
   ```bash
   python -m nose tests/
   ```

2. **Check code style:**
   ```bash
   # Install flake8 if needed
   pip install flake8

   # Check your code
   flake8 sepa/ --max-line-length=120
   ```

3. **Update documentation:**
   - Add docstrings
   - Update relevant docs
   - Add examples if needed

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Your descriptive commit message"
   ```

### Creating the Pull Request

1. **Push to your fork:**
   ```bash
   git push origin your-feature-branch
   ```

2. **Open a pull request** on GitHub

3. **Fill out the PR template:**
   - Description of changes
   - Related issues
   - Testing done
   - Breaking changes (if any)

4. **Wait for review:**
   - Address feedback
   - Update as needed
   - Be patient and respectful

### PR Checklist

- [ ] Tests pass locally
- [ ] New features have tests
- [ ] Documentation updated
- [ ] Code follows style guidelines
- [ ] Commit messages are clear
- [ ] No merge conflicts
- [ ] XSD schemas included (for new message types)

## Reporting Issues

### Bug Reports

When reporting bugs, include:

1. **Python version:** `python --version`
2. **Library version:** Check `setup.py` or installed version
3. **Minimal reproducible example**
4. **Expected behavior**
5. **Actual behavior**
6. **Error messages and stack traces**

Example:

```markdown
### Bug Description
Parser fails with UnsupportedDocumentType for valid camt.053.001.08

### Environment
- Python 3.9.7
- python-sepa 0.5.3
- lxml 4.9.1

### Minimal Example
\`\`\`python
from sepa import parser

xml = """<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.053.001.08">
  ...
</Document>"""

parser.parse_string(None, xml)
\`\`\`

### Expected
Should parse successfully

### Actual
Raises UnsupportedDocumentType: camt.053.001.08

### Stack Trace
\`\`\`
Traceback (most recent call last):
  ...
\`\`\`
```

### Feature Requests

When requesting features:

1. **Describe the feature** clearly
2. **Explain the use case**
3. **Provide examples** if possible
4. **Check if it aligns** with project goals

## Getting Help

If you need help:

- **Check documentation:** Start with README and docs/
- **Search issues:** Your question may have been answered
- **Ask in issues:** Open a new issue with your question
- **Be specific:** Provide context and examples

## Recognition

Contributors will be recognized:

- In release notes
- In project documentation
- In commit history

Thank you for contributing to python-sepa!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
