# Module `kimera.store.DummyStore`

Simple singleton used to stash a session identifier or similar token.

## `DummyStore`
- Class attribute `_sid` stores the current value.
- `sid(sid=None)` acts as both setter and getter:
  - Pass a value to update `_sid`.
  - Call with no arguments to retrieve the last stored value.
