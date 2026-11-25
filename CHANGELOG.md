# Changelog

All notable changes to Nostek Status. Versions follow [Semantic Versioning](https://semver.org/). Dates in WIB.

## [Unreleased]

### Added
- Public-repo hygiene check `scripts/check_public.py` + tests (`make ci`): fails on private / tailnet / link-local
  addresses, private keys and token shapes in tracked files; site-specific rules from an untracked `.hygiene-deny`.
- Repository start: README, MIT licence, trademark notice, security and contributing guides, brand files
  (Nostek Status logo, same generator as Nostek Panel).
