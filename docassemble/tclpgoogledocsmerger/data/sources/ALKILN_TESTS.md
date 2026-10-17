# ALKiln end-to-end coverage

The scenario starts search_and_download.yml directly (homepage.yml only redirects), selects Commercial from the bundled Grid_view.csv taxonomy, and expects the merged download. The full path needs Google Drive OAuth/service-account configuration and `drive doc bank` pointing to the clause folder; optional `docs airtable` refreshes the bundled CSV and `cloud convert api key` enables conversion. Supply ALKILN_DOCASSEMBLE_CONFIG. Without access to the configured Google Drive clause bank this enabled test cannot pass; the PR is a draft.

Fixture review: seeded with ALDashboard static generator and reviewed against interview YAML, local includes, allowed choices, branching, and final screen. Browser and isolated CI results are reported separately; source review alone is not a passing browser test. The workflow runs automatically on pull requests and supports manual dispatch.
