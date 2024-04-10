# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> This changelog was generated some commits after the [v1.0.0 tag](https://github.com/Naapperas/zon/releases/tag/v1.0.0), so the changelog will have some inconsistencies until the next release.

## [Unreleased]

### Added
- Added more string validation methods.
- `parse` and `safe_parse` methods.
- Added `opts` arg to `ZonString.regex` method to allow defining custom error messages.
- Added `opts` arg to `ZonString.ip` method to allow defining custom error messages and specify the IP version to check against. 
- Added `unwrap` method to `ZonOptional`.

### Changed
- `optional` is now a method inside every `Zon` object.
- Moved `ZonCollection` and `ZonString` to the base file.
- Deprecated `validate` (and its private variant `_validate`) in favor of `parse` and `safe_parse` methods.
- Deprecated `ValidationError` in favor of `ZonError`.

### Removed
- Removed `between`, `__eq__` and `equals` methods from `ZonNumber`.

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