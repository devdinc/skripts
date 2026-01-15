# Skripts

Personal Skript files created for various purposes.

## Documentation

All documentation, setup instructions, and usage examples are maintained in the project [wiki](https://github.com/devdinc/skripts/wiki).

## Purpose

The wiki includes:
- Installation and configuration instructions
- Skript usage examples
- Architecture and design notes
- Troubleshooting and FAQs

## Contributing

Most scripts in this repository are developed primarily for personal use and are provided as-is. Contributions and feedback are welcome.

Please note:
- Not all pull requests will be accepted, as changes must align with the project’s direction and use cases.
- Moderately significant bug fixes or meaningful improvements are very likely to be accepted.
- Smaller stylistic or opinion-based changes may be declined.

If you are unsure whether a proposed change would be implemented, please create an issue before submitting a pull request.

## Common Issues

### Load Order

If you encounter errors such as `Can't understand this expression`, the issue is most likely related to load order.

Skript loads files alphabetically, with folders being prioritized. To control load order, prefix the Skript file with a folder or a character such as `0_` or `!`
(e.g., `!testframework.sk`)
