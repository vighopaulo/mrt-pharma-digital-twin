# Build 9.0 — Patient Entity

## Added

- Initial `Patient` domain entity.
- UUID-based patient identity.
- Required internal patient reference and patient name.
- Optional date-of-birth and sex metadata.
- Active and inactive patient-record state.
- User-facing patient display label.
- Age calculation for a supplied reference date.
- Unit tests for identity, validation, normalization, display behavior, age calculation, and state changes.
