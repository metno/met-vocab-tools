# Met Vocabulary Tools

[![flake8](https://github.com/metno/met-vocab-tools/actions/workflows/syntax.yml/badge.svg)](https://github.com/metno/met-vocab-tools/actions/workflows/syntax.yml)
[![pytest](https://github.com/metno/met-vocab-tools/actions/workflows/pytest.yml/badge.svg)](https://github.com/metno/met-vocab-tools/actions/workflows/pytest.yml)
[![codecov](https://codecov.io/gh/metno/met-vocab-tools/branch/main/graph/badge.svg?token=ArC7kOj59U)](https://codecov.io/gh/metno/met-vocab-tools)

Toolbox for caching and interfacing with [vocab.met.no](https://vocab.met.no/).

## Config

A desired path to be used for caching can be provided by the environment variable
`METVOCAB_CACHEPATH`, otherwise a system-specific fallback will be used.

## Debugging

To increase logging level to include info and debug messages, set the environment variable
`METVOCAB_LOGLEVEL` to the desired level. Valid levels are `CRITICAL`, `ERROR`, `WARNING`, `INFO`,
and `DEBUG`.

## Tests

The tests use `pytest`. To run all tests for all modules, run:

```bash
python -m pytest -vv
```

To add coverage, and to optionally generate a coverage report in XML, run:

```bash
python -m pytest -vv --cov=metvocab --cov-report=term --cov-report=xml
```

Coverage requires the `pytest-cov` package.

Some of the tests will call the live vocab.met.no API. To disable those tests, add `-m 'not live'`
to the pytest command, like for so:

```bash
python -m pytest -vv -m 'not live'
```
