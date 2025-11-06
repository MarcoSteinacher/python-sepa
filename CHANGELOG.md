# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive project documentation
  - Enhanced README with detailed examples and feature overview
  - API Reference with complete function documentation
  - Architecture Guide explaining design patterns and internals
  - Examples Guide with practical usage scenarios
  - Contributing Guide with development guidelines
- Documentation improvements
  - Usage examples for all supported message types
  - Integration patterns for REST APIs and databases
  - Error handling examples
  - Digital signature examples

## [0.5.3] - 2024

### Added
- Support for camt.053 (Bank To Customer Statement) with version compatibility
  - Compatible with camt.053.001.04, 001.06, 001.08
- Support for camt.054 (Bank To Customer Debit Credit Notification)
  - Compatible with camt.054.001.04, 001.06, 001.08
- Auto-detection of document types from XML namespaces
- Document type compatibility system

### Changed
- Updated parser to support automatic document type detection
- Enhanced structure definitions for statement messages

### Fixed
- Parser compatibility with multiple CAMT message versions

## [0.5.2] - Prior Release

### Added
- Support for pain.008.001.07 (Customer Direct Debit Initiation)
- Support for pain.009.001.05 (Mandate Initiation Request)
- Support for pain.010.001.05 (Mandate Amendment Request)
- Support for pain.011.001.05 (Mandate Cancellation Request)

### Changed
- Improved structure definition system
- Enhanced reusable definition functions

## [0.5.1] - Prior Release

### Fixed
- Various bug fixes and improvements
- XSD schema corrections

## [0.5.0] - Prior Release

### Added
- Initial public release
- Core builder functionality for creating XML from Python dicts
- Core parser functionality for parsing XML to Python dicts
- XSD validation support
- Basic signing and verification support (via signxml)
- Reusable structure definitions in sepa/definitions/

### Architecture
- Data-driven structure definition system
- Automatic parser structure reversal
- Message auto-discovery and registration

## Version History Summary

| Version | Date | Key Changes |
|---------|------|-------------|
| 0.5.3 | 2024 | Added CAMT messages, auto-detection |
| 0.5.2 | - | Added PAIN messages (008, 009, 010, 011) |
| 0.5.1 | - | Bug fixes |
| 0.5.0 | - | Initial release |

## Migration Guides

### Upgrading to 0.5.3

**Auto-detection feature:**

Before (0.5.2):
```python
from sepa import parser
data = parser.parse_string(parser.bank_to_customer_statement, xml)
```

After (0.5.3):
```python
from sepa import parser
# Structure parameter can now be None for auto-detection
data = parser.parse_string(None, xml)
# Document type is included in parsed data
print(data['document_type'])  # e.g., 'camt.053.001.06'
```

**Compatible versions:**

The library now automatically handles multiple versions of the same message type:
- camt.053: Supports 001.04, 001.06, 001.08
- camt.054: Supports 001.04, 001.06, 001.08

No code changes needed - just works!

## Roadmap

See [README.md](README.md#roadmap) for planned features.

### Planned for Future Releases

#### v0.6.0 (Planned)
- [ ] Support for pain.001.001.08 (Customer Credit Transfer Initiation)
- [ ] Support for pain.002.001.08 (Customer Payment Status Report)
- [ ] Enhanced validation with business rules
- [ ] Performance optimizations

#### v0.7.0 (Planned)
- [ ] Support for PACS message types (Payments Clearing and Settlement)
- [ ] Batch processing optimizations
- [ ] Streaming parser for large files
- [ ] Command-line interface

#### v1.0.0 (Planned)
- [ ] Complete SEPA message support
- [ ] Comprehensive test coverage
- [ ] Production-ready documentation
- [ ] Performance benchmarks
- [ ] Stable API

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute.

## Support

For bug reports and feature requests, please use the [GitHub issue tracker](https://github.com/VerenigingCampusKabel/python-sepa/issues).

## License

This project is licensed under the MIT License - see [LICENSE.md](LICENSE.md) for details.
