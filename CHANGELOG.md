# Changelog

## [2.0.0](https://github.com/roquerodrigo/tplink-deco-api/compare/v1.2.2...v2.0.0) (2026-08-07)


### ⚠ BREAKING CHANGES

* Python 3.11, 3.12 and 3.13 are no longer supported. Consumers on those interpreters must stay on 1.2.2.

### Build System

* require Python 3.14 ([29b8cad](https://github.com/roquerodrigo/tplink-deco-api/commit/29b8cada6ae1f0d3a305a2e1189e3ab620dd37b9))

## [1.2.2](https://github.com/roquerodrigo/tplink-deco-api/compare/v1.2.1...v1.2.2) (2026-08-07)


### Bug Fixes

* keep payload decoding failures inside the SDK exception hierarchy ([d3d6530](https://github.com/roquerodrigo/tplink-deco-api/commit/d3d65300ccbdf86a29f13a9bd0ffb73cfb1046ab))


### Code Refactoring

* bind exception messages to a local before raising ([9151fd9](https://github.com/roquerodrigo/tplink-deco-api/commit/9151fd9c9c8400e67eb4d915e8ecbee36a5f9203))
* drop dead protocol helpers and deduplicate the .env loader ([3ce83d0](https://github.com/roquerodrigo/tplink-deco-api/commit/3ce83d0ccdf3861428e9585531c66d0b3d2effa5))


### Dependencies

* **deps:** bump the python-deps group across 1 directory with 2 updates ([55287ba](https://github.com/roquerodrigo/tplink-deco-api/commit/55287ba3f346ca3588b2ee797aaa1db0257c162d))


### Documentation

* align protocol docs, style guide and README with the implementation ([315a4ff](https://github.com/roquerodrigo/tplink-deco-api/commit/315a4ffe183dafa9e904b925aeec0686e5c71371))
* update CLAUDE.md ([bdfb9e9](https://github.com/roquerodrigo/tplink-deco-api/commit/bdfb9e95dca31808004443baf79e45620a9699c6))


### Continuous Integration

* assign open issues and pull requests to the repository owner ([cf273a4](https://github.com/roquerodrigo/tplink-deco-api/commit/cf273a400ca5b03b0e37089b6d09ee9803e04f41))
* call the shared auto-assign workflow instead of duplicating it ([2862c7b](https://github.com/roquerodrigo/tplink-deco-api/commit/2862c7b9913dd86af1f60c71c28f620bbbe8b444))
* refresh the lockfile through the release workflow ([e13a631](https://github.com/roquerodrigo/tplink-deco-api/commit/e13a63188bcb5fe9c07f34b2b3ee4ece2f9d0d8c))
* run checks on pull requests targeting any branch ([e8a4155](https://github.com/roquerodrigo/tplink-deco-api/commit/e8a41551660ce7e4e0349f80233d31758c405db9))
* run code scanning on pull requests targeting any branch ([4531f5c](https://github.com/roquerodrigo/tplink-deco-api/commit/4531f5c1bc7a3888bc988aed0c17ce70e2cde06c))
* split the CI workflow into one file per concern ([e01ed27](https://github.com/roquerodrigo/tplink-deco-api/commit/e01ed273aaa541dfb680cce14a88d6de770d2d4c))


### Miscellaneous Chores

* **deps-dev:** bump ruff in the python-deps group ([fcd4920](https://github.com/roquerodrigo/tplink-deco-api/commit/fcd492047ddb8a73f4fee2fa69a9a28797cd6136))
* **deps-dev:** bump ruff in the python-deps group across 1 directory ([598ee8d](https://github.com/roquerodrigo/tplink-deco-api/commit/598ee8d83d3a7dac8672360eec3f40f7049d3997))
* **deps:** bump the python-deps group with 4 updates ([dca5e94](https://github.com/roquerodrigo/tplink-deco-api/commit/dca5e9452981cfdcf9a1bc142805b6aeb750b651))
* **deps:** bump the python-deps group with 4 updates ([cbd822a](https://github.com/roquerodrigo/tplink-deco-api/commit/cbd822ad7a9bf4f722331f1617dca6361a41689a))
* enforce docstrings with ruff and drop the unused pytest-asyncio ([451cad9](https://github.com/roquerodrigo/tplink-deco-api/commit/451cad9e7795b8198f9f786d81b02db0b1e2c759))
* keep the ruff formatter out of Markdown files ([89c8643](https://github.com/roquerodrigo/tplink-deco-api/commit/89c8643a226e1196dea5377ae3e8fa22359a1148))
* lint against the full ruff rule set ([7e1f9be](https://github.com/roquerodrigo/tplink-deco-api/commit/7e1f9bef7dc3be35b437c459ad78392ec5fe3397))
* move CI to the shared workflows repository ([7f48537](https://github.com/roquerodrigo/tplink-deco-api/commit/7f485372d731c4eda460cb500a55b1a5476ff5a7))
* release on every conventional commit type ([6948c4c](https://github.com/roquerodrigo/tplink-deco-api/commit/6948c4c7da9b52c9015d2377c4bc057c4d534c57))
* ship the MIT license text with the distribution ([b986e4d](https://github.com/roquerodrigo/tplink-deco-api/commit/b986e4d08d6fe2616cb2832ad12a242b944b4ba5))

## [1.2.1](https://github.com/roquerodrigo/tplink-deco-api/compare/v1.2.0...v1.2.1) (2026-07-06)


### Documentation

* document the Deco local HTTP API and protocol ([fa49ba9](https://github.com/roquerodrigo/tplink-deco-api/commit/fa49ba926bc378689be434a23987ed2f549ec787))

## [1.2.0](https://github.com/roquerodrigo/tplink-deco-api/compare/v1.1.2...v1.2.0) (2026-06-15)


### Features

* add network, wireless, time and log endpoints + HTTPS transport ([6832d0b](https://github.com/roquerodrigo/tplink-deco-api/commit/6832d0b239082f5327fa7fbdd001202dd3e03631))
* release 1.2.0 (network/wireless/time/log endpoints + HTTPS) ([0761428](https://github.com/roquerodrigo/tplink-deco-api/commit/0761428150847f434b184850842be154d5e06e2d))

## [1.1.2](https://github.com/roquerodrigo/tplink-deco-api/compare/v1.1.1...v1.1.2) (2026-05-25)


### Documentation

* add CI and PyPI badges ([b6dd7d1](https://github.com/roquerodrigo/tplink-deco-api/commit/b6dd7d16b744e09a4c44bc3d2f9780253782574d))
* add CI and PyPI badges ([c1b6deb](https://github.com/roquerodrigo/tplink-deco-api/commit/c1b6debac7f8145b4f6a244f98e84988c5d06085))

## [1.1.1](https://github.com/roquerodrigo/tplink-deco-api/compare/v1.1.0...v1.1.1) (2026-05-14)


### Documentation

* translate README, auth-protocol and pyproject description to English ([da74081](https://github.com/roquerodrigo/tplink-deco-api/commit/da7408178b28f7d609965cd785c00f7a423bd462))

## [1.1.0](https://github.com/roquerodrigo/tplink-deco-api/compare/v1.0.1...v1.1.0) (2026-05-11)


### Features

* add NetworkTotals for aggregated client speeds ([041c8b6](https://github.com/roquerodrigo/tplink-deco-api/commit/041c8b6ebf394067ec3ea767c73efaab998d24c9))


### Dependencies

* bump cryptography 47 → 48 ([b5917ca](https://github.com/roquerodrigo/tplink-deco-api/commit/b5917cacde1c4772c2d7293ccdb150b83dfdc364))


### Documentation

* standardize CODE_STYLE.md and switch CLAUDE.md to English ([b216c23](https://github.com/roquerodrigo/tplink-deco-api/commit/b216c23480c61407a9227a38d3050b2666c8b36a))
