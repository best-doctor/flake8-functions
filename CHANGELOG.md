# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-08-14

### Removed

- Support for Python 3.6, 3.7, 3.8 and 3.9. The minimum supported version is now **Python 3.10**.
- `setuptools` as a runtime dependency.
- The `mr-proper` runtime dependency. **flake8-functions now has zero runtime dependencies.**
  `mr-proper` was unmaintained since 2021 and never declared Python 3.10+ support; the purity
  rules behind `CFQ003` are now vendored into `flake8_functions/function_purity.py`, covering
  exactly the code path this project used (no cross-file recursive checks, no per-error
  messages — `is_function_pure(func_def)` was always called with no other arguments). Verified
  bit-for-bit against `mr-proper==0.0.7` on 46 purpose-built cases (including a dedicated async
  battery — `async with`, `async for`, `await`, nested `async def`) plus both original test
  fixtures: identical verdicts on every one, including a faithfully preserved upstream quirk
  where `async for ... :` loop targets are not recognized as local variables (only plain `for`
  and comprehensions are), which can make an otherwise-clean async generator read as impure.

### Added

- Support for Python 3.11, 3.12, 3.13 and **3.14**.
- Positional-only parameters (PEP 570) are now counted by `CFQ002`.

### Fixed

- **The plugin crashed on Python 3.14** with `AttributeError: module 'ast' has no attribute 'Str'`.
  `ast.Str` was removed in 3.14; docstring detection now uses `ast.Constant`.
- `CFQ002` silently ignored positional-only parameters, so `def f(a, b, c, d, /, e, f, g)` was
  reported as having 3 arguments instead of 7 and never tripped the limit.
- Return type annotations of the check functions claimed a tuple was always returned, while `None`
  is returned when there is no violation. They are now `tuple[int, int, str] | None`.

### Changed

- Packaging moved from `setup.py` / `setup.cfg` to `pyproject.toml` (PEP 621).
- Flake8, mypy, pytest and coverage are configured in `pyproject.toml` as well;
  flake8 reads it through [Flake8-pyproject](https://pypi.org/project/Flake8-pyproject/).
- Dependencies are managed with [uv](https://docs.astral.sh/uv/) and pinned in `uv.lock`.
- `max-line-length` lowered from 120 to 100, matching `.editorconfig` and the styleguide.
- Type aliases `AnyFuncdef` and `FunctionError` moved to `flake8_functions/type_defs.py`
  instead of being redeclared in every module.

### Internal

- CI reworked: a single `ci.yml` replaces the two identical `build.yml` / `build_pr.yml` workflows,
  runs on Python 3.10–3.14, and uses `uv` with caching.
- CodeClimate integration removed, along with its config and README badges.
- `safety` replaced with `pip-audit`; `safety check` has been deprecated since 2024.
- Dropped `flake8-expression-complexity` and `flake8-if-statements`: both are themselves broken on
  Python 3.14 (`ast.Str` and `ast.NameConstant` removals).
- Dropped `flake8-polyfill` (a flake8 2.x compatibility shim) and the `packaging==21.3` pin.
- Removed dead config options that had no matching plugin installed:
  `adjustable-default-max-complexity`, `min-coverage-percents`, `assert_allowed_in_pathes`.
- Removed the `.flake_master` preset file and the Ruby `mdl` setup (`.mdlrc`, `.mdlrc.rb`) in favour
  of `markdownlint-cli2`.
- Added a `.pre-commit-config.yaml`; the project had no pre-commit setup before.
- Tests restructured into `tests/test_unit/` and `tests/test_integration/`, following the
  `test__<function>__<case>` convention. Test count went from 39 to 119, with 100% coverage —
  `add_options` and `parse_options` were previously untested, and the vendored purity rules now
  have direct unit coverage of each of the seven checks they used to delegate to `mr-proper`.
- Added explicit async coverage for all four checks; only `CFQ001` and `CFQ002` were exercised
  against `async def` before.

## [0.0.8] - 2023-04-10

### Fixed

- Typo in the `CFQ001` message: `lenght` → `length`.

## [0.0.7] - 2022-02-24

### Added

- Support for Python 3.10.

### Removed

- `pytest` from the runtime dependencies.

## [0.0.6] - 2021-04-23

### Added

- `CFQ004` — check for the number of `return` statements in a function.

### Changed

- Moved from Travis CI to GitHub Actions.

## [0.0.5] - 2021-01-14

### Added

- `CFQ003` — check that functions with `pure` in their name are actually pure,
  backed by [mr-proper](https://pypi.org/project/mr-proper/).
- Support for Python 3.9.

## [0.0.4] - 2020-02-15

### Fixed

- Detection of the last row of a function.

## [0.0.3] - 2020-02-15

### Added

- Support for Python 3.8.

### Fixed

- Docstrings are no longer counted towards the function length.

## [0.0.2] - 2019-10-28

### Added

- `CFQ002` — check for the number of function arguments.

## [0.0.1] - 2019-10-01

### Added

- Initial release with `CFQ001` — check for function length.

[0.1.0]: https://github.com/best-doctor/flake8-functions/compare/v0.0.8...v0.1.0
[0.0.8]: https://github.com/best-doctor/flake8-functions/compare/v0.0.7...v0.0.8
[0.0.7]: https://github.com/best-doctor/flake8-functions/compare/v0.0.6...v0.0.7
[0.0.6]: https://github.com/best-doctor/flake8-functions/compare/v0.0.2...v0.0.6
[0.0.2]: https://github.com/best-doctor/flake8-functions/releases/tag/v0.0.2
