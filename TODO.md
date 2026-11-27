# First PyPI release

The first release attempt from tag `v0.1.0` built both distributions. PyPI
rejected the upload because the `PYPI_API_TOKEN` repository secret was missing.

Set `PYPI_API_TOKEN` on `asbl/miniworlds-data` and run the **Publish to PyPI**
workflow from `main` to publish the corrected `0.1.0` build. The workflow checks
the distributions and tests the installed wheel against Miniworlds `4.4.0.7`
before uploading.

H5P.PythonQuestion already requests `miniworlds-data==0.1.0`. Verify the release
with the [PyPI version endpoint](https://pypi.org/pypi/miniworlds-data/0.1.0/json).
