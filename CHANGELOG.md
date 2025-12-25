# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

### Added
- Path population on ZonIssue instances for better tracking what caused an error.

## [3.0.0] - 2025-05-16

### Changed
- Updated contribution guidelines.
- Updated CI workflow to run on Pull Request.
- Updated README.md to include more information and examples of code usage as well as corrected some old examples.
- Added contributors to the CONTRIBUTORS file.

### Deleted
- Removed `uuid` as a dependency.

### Added
- Added explanation about chaining API to README.md.

## [2.0.1] - 2024-07-16

### Changed
- Fixed the return type of `validate`

## [2.0.0] - 2024-06-20

### Added
- Added `ValidationContext` class to keep track of current validation path and errors up until a certain point.
- Added `examples` folder
- Added explanation regarding `ZonString.datetime()` decisions.
- Added `ZonLiteral`, `ZonTuple` and `ZonEnum` classes
- Added more `ZonRecord` methods
- Added coverage

### Changed
- Moved everything into a single file to combat circular reference issues
- Deprecated `ValidationError` in favor of `ZonError`.
- Simplified validation logic
- Now returns a (deep-) copy of the original data after validation. This is more useful for `ZonRecord` and `ZonString` validators that can transform, while transformers are not added.

### Removed
- Removed `between`, `__eq__` and `equals` methods from `ZonNumber`.
- Removed `ZonInteger` and `ZonFloat` in favor of new validation rules in `ZonNumber`
- Removed `true` and `false` methods from `ZonBoolean`

## [1.1.0] - 2024-04-10

### Added
- `zon` now has a changelog.
- Added `zon.traits` module for common functionality that is specific to no validator.
- Added the `zon.traits.collection` file which contains the `ZonCollection` class: this is the base class for all collection types.
- Added testing for `ZonCollection` and added more tests for `ZonString`.
- Scripts that automate the building and publishing of the package to PyPI.
- Added `refine` method to the base `Zon` class.

### Changed
- `ZonString` now inherits from `ZonCollection` instead of `Zon`.
- `ZonList` now inherits from `ZonCollection` instead of `Zon`.
- Updated `README.md` to include more information and examples of code usage.
  
### Removed
- Removed the `len` function from `ZonString` and `ZonList` as it was not being used and did too much.

## [1.0.0] - 2023-11-26

### Added
- Added base source code files for the project.
- Base `README.md` file.

[Unreleased]: https://github.com/Naapperas/zon/compare/v3.0.0...HEAD
[3.0.0]: https://github.com/Naapperas/zon/compare/v2.0.1...v3.0.0
[2.0.1]: https://github.com/Naapperas/zon/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/Naapperas/zon/compare/v1.1.0...v2.0.0
[1.1.0]: https://github.com/Naapperas/zon/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Naapperas/zon/releases/tag/v1.0.0