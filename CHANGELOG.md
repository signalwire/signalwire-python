# Changelog
All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.4] - 2021-11-29
### Updated
- Update compatibility SDK versions.

## [2.0.2] - 2020-03-10
### Fixed
- Delete the `_request` dict key once the request has been completed.

## [2.0.1] - 2019-12-05
### Fixed
- Call prompt `media_list` parameter without nested _params_ property.

## [2.0.0] - 2019-11-25
### Added
- Call `disconnect()` method.

### Fixed
- Check signals supported by the environment. On Windows there is no `SIGHUP`.
- Detect half-open connection and force close connection to update Client/Consumer properly.

## [2.0.0rc1] - 2019-10-28
### Added
- Support for Calling `tap`, `tap_async` methods.
- Support for Calling `send_digits`, `send_digits_async` methods.
- Support to send/receive faxes on the Call: `fax_receive`, `fax_receive_async`, `fax_send`, `fax_send_async`.
- Methods to start detectors on the Call: `detect`, `detect_async`, `detect_answering_machine`, `detect_answering_machine_async`, `detect_digit`, `detect_digit_async`, `detect_fax`, `detect_fax_async`.
- Set logging level via LOG_LEVEL env variable.
- Add `playRingtone` and `playRingtoneAsync` methods to simplify play a ringtone.

## [2.0.0b3] - 2019-10-14
### Added
- Support for Relay Messaging
- Support for Calling `connect` and `play` methods.
- Support for Calling `record` methods.
- Methods to wait some events on the Call object: `wait_for_ringing`, `wait_for_answered`, `wait_for_ending`, `wait_for_ended`.

## [2.0.0b2] - 2019-10-03
### Fixed
- Minor fix if using wrong SignalWire number.

### Changed
- Default log level to INFO

## [2.0.0b1] - 2019-10-03
### Added
- Beta version of `Relay Client`
- `Relay Consumer` and `Tasks`

### Fixed
- Possible issue on WebSocket reconnect due to a race condition on the EventLoop.

## [1.5.0] - 2019-04-12
### Fixed
- Allow initialization via ENV variable

## [1.4.2] - 2019-02-02
### Added
- Python 2 support
### Fixed
- Importing LaML subclasses

## [1.4.0] - 2019-01-16
### Added
- Fax REST API

## [1.0.0] - 2018-10-04

Initial release

<!---
### Added
### Changed
### Removed
### Fixed
### Security
-->
