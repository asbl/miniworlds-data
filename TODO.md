# TODO: finish the PyPI release

The package builds and passes `twine check` (`dist/miniworlds_data-0.1.0*`),
but it is **not yet published on PyPI**. Remaining steps:

- [ ] Add `.github/workflows/publish_to-pypi.yml` to this repo (same content
      as in `miniworlds-robot`/`miniworlds-turtle`). It already exists
      locally but is untracked because the `gh` CLI token used to push this
      repo lacked the `workflow` scope. Either:
      - run `gh auth refresh -h github.com -s workflow`, then
        `git add .github && git commit -m "Add PyPI publish workflow" && git push`, or
      - upload the file manually via the GitHub web UI.
- [ ] Set the `PYPI_API_TOKEN` secret on this repo (same as the other two):
      `gh secret set PYPI_API_TOKEN -R asbl/miniworlds-data`
- [ ] Tag and push the release to trigger the publish workflow:
      `git tag v0.1.0 && git push origin v0.1.0`
- [ ] Confirm the release landed: https://pypi.org/project/miniworlds-data/

## After it's live

`H5P.PythonQuestion` already pins `miniworlds-data` to `0.1.0` in
`MINIWORLDS_PINNED_VERSIONS`
(`src/scripts/runtime/services/pyodide-precache-service.js`) in anticipation
of this release — no further change needed there once the tag above is
published, as long as the published version is `0.1.0`. If a different
version ends up published first, update the pin to match.
