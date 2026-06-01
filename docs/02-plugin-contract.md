# Plugin Contract

## Compatibility source

The core repo owns protocol schemas and conformance fixtures. The plugin consumes that contract and proves compatibility through tests.

Required compatibility checks:

- daemon reachable;
- daemon protocol version supported;
- required feature flags present;
- command envelope schema supported;
- stream frame schema supported;
- structured error schema supported.

If any required check fails, the plugin fails closed and tells the operator to use the canonical CLI from the core repo.

## Tool handler rules

Hermes tool handlers must:

- accept structured arguments;
- call the Python daemon client, not private storage files;
- return JSON strings;
- preserve daemon `command_id`, `event_id`, `session_id`, and error category fields;
- never turn daemon failure into success;
- avoid raw token/secrets in logs and responses.

## CLI fallback rule

CLI fallback is allowed only when it is equivalent to an operator running `kkachi-agent-network` manually. It must use argv-only subprocess invocation and must never interpolate shell strings.

## Plugin/core equivalence

For every plugin write operation, there must be a documented equivalent daemon/CLI command in the core repo. Equivalence means same state transition, same validation, same idempotency behavior, and compatible structured errors.
