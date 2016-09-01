# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) 
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]
### Added
- testing utility `test.unit.util.redirect` to capture stdout, stderr and
  `sys.exit` code for CLI testing
- initial prototype framework for optimizations in adapters with the head proc
  being optimized in the elastic and stdio adapters.

### Changed
- stdio tests to use the new `redirect` utility to capture stdout, stderr and
  intercept the `sys.exit` exit code.

## [0.3.8] - 2015-08-27

### Added
- checking all examples for syntax errors in travis

### Changed
- speed up unit tests with a few small tweaks
- moved where we process the `time` field for adapters down to the adapter class
  and out of the `read` base class

## [0.3.7] - 2015-08-21

### Changed
- bumping `dici` dependency

## [0.3.6] - 2015-08-21

### Changed
- bumping `dici` dependency

## [0.3.5] - 2015-08-21

### Added
- added documentation for `math` and `date` reducers
- added new thirdparty utilities that are documented at https://rlgomes.github.io/flume/thirdparty/

### Fixed
- coverage report was not reporting for all files, is now.

## [0.3.4] - 2015-08-14

### Added
- exposed `timefmt` format for gnuplot
- new `seq` proc, used to sequential pipeline execution
- compression option for stdio which allows you to read and write files with
  gzip, zlib and deflate compression

## [0.3.3] - 2015-08-10

### Fixed
- assorted documentation fixes and code clean up

## [0.3.2] - 2015-08-07

### Fixed
- fixed the way were handling input data through stdin so that we actually
  stream data and don't block until we've read everything

## [0.3.1] - 2015-08-07

### Fixed
- fix version reporting on the CLI to pull from a single file in source, this
  means `flume --version` works as expected for every release

## [0.3.0] - 2015-08-07

### Added
- support for nested field in `reduce` ie `reduce(max=maximum('author.count'))`
- enabled automatic travis builds
- enabled coveralls reporting (coverage checking)

### Fixed
- now works in Python 3

## [0.2.0] - 2015-08-02
### Changed
- first release of flume!

[Unreleased]: https://github.com/rlgomes/flume/compare/v0.3.8...HEAD
[0.3.8]: https://github.com/rlgomes/flume/compare/v0.3.7...v0.3.8
[0.3.7]: https://github.com/rlgomes/flume/compare/v0.3.6...v0.3.7
[0.3.6]: https://github.com/rlgomes/flume/compare/v0.3.5...v0.3.6
[0.3.5]: https://github.com/rlgomes/flume/compare/v0.3.4...v0.3.5
[0.3.4]: https://github.com/rlgomes/flume/compare/v0.3.3...v0.3.4
[0.3.3]: https://github.com/rlgomes/flume/compare/v0.3.2...v0.3.3
[0.3.2]: https://github.com/rlgomes/flume/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/rlgomes/flume/compare/v0.3...v0.3.1
[0.3.0]: https://github.com/rlgomes/flume/compare/v0.2...v0.3
[0.2.0]: https://github.com/rlgomes/flume/commits/v0.2
