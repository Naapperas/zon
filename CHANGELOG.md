# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Added `ValidationContext` class to keep track of current validation path and errors up until a certain point.
- Added `examples` folder
- Added explanation regarding `ZonString.datetime()` decisions.
- Added `ZonLiteral` and `ZonEnum` classes
- Added more `ZonRecord` methods
- Added coverage

### Changed
- Moved everything into a single file to combat circular reference issues
- Deprecated `ValidationError` in favor of `ZonError`.
- Simplified validation logic

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

[unreleased]: https://github.com/Naapperas/zon/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/Naapperas/zon/compare/v1.1.0...v1.1.0
[1.0.0]: https://github.com/Naapperas/zon/releases/tag/v1.0.0