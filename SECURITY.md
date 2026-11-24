# Security policy

Please do **not** open a public issue for a security problem.

Report it privately through GitHub: **Security → Report a vulnerability** on this repository.
Include what you found, how to reproduce it, and the version or commit.

We aim to answer within 7 days. Nostek Status is in its design phase, so no released version is supported yet.

## What the design protects

- The status page holds **no secret that opens anything else**: it keeps only public verification keys.
- Optional detail pushed to the page must be **signed (Ed25519)** and bound to the page (`aud`), a known key id
  (`kid`), a strictly increasing sequence (`seq`) and a short expiry. Anything else is refused and the last good
  snapshot stays on screen.
- Missing or old data is shown as **delayed**, never as healthy.
