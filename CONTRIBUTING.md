# Contributing to Nostek Status

Thanks for your interest. The project is in its design phase; see the roadmap in the README.

- Open an issue first for anything bigger than a typo, so we can agree on the approach.
- Branches: `step/<id>-<slug>` from `main`.
- Never commit secrets: no passwords, tokens, private keys or `.env` files. Test fixtures and examples must be
  obviously fake (`example.com`, `203.0.113.0/24`).
- Run `make ci` before every push (public-repo hygiene check + tests). Put your own host names or ranges in an
  untracked `.hygiene-deny` file (one regular expression per line) so the check refuses them too.
- Do not put real server addresses, monitored URLs or account names in the repository; they belong in settings.
- Use only our own product names in code, UI and docs; do not copy other vendors' names or artwork.
- UI text lives in locale files (English and Indonesian at least).
- Every time shown to a person carries its time zone.

By contributing you agree that your contribution is licensed under the MIT licence. The logos are not
(see [TRADEMARKS.md](TRADEMARKS.md)).
