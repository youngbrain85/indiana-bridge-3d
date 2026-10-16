# Hosted Indiana Bridge 3D

The primary application is hosted at https://indiana-bridge-3d.plumibex3.chatgpt.site.
It is an owner-private ChatGPT Site. Sign in with the account that owns the Site.

## Architecture

- **Sites:** serves the existing application through a streaming HTTP gateway. Sites handles visitor authentication. GLB and PDF range requests, JSON, rendered drawing pages, database exports and FEM requests retain their existing paths.
- **Railway / bridge-engine:** one Python 3.12 ASGI process, with the existing isolated native OpenSees subprocess and one active calculation at a time. This is a separate project from Beechwood Web.
- **Persistent volume `/persist`:** holds the SQLite catalog, all saved FEM runs and verified immutable release assets. Initial data is seeded once. Restarts never replace the working database with the original seed.
- **Private object storage:** contains the large release archive. The server verifies its SHA-256 before extracting it. Public access to the engine requires a secret supplied only by the Sites gateway; `/healthz` exposes a minimal readiness response.

The initial release contains 21 crossings, 16 model workspaces, 6,622 components and 75 saved execution records. The existing material assumptions and analysis limitations remain visible. Native solver results are demonstrations, not bridge capacity certifications.

The frontend uses the Sites Vinext build integration. `sites/indiana-bridge-3d` in the authoring workspace is its separate source checkout; the native Sites source repository owns its version history. The backend and all original bridge sources are maintained in this GitHub repository.

## Release workflow

1. Run the existing application and verify the intended catalog and model revisions. Wait for active local calculations to finish.
2. Run `python scripts/prepare_hosted.py ABSOLUTE_EMPTY_RELEASE_DIRECTORY`. This makes a SQLite backup, verifies assets and result hashes, and copies all existing runs. It does not alter the local database.
3. Link Railway CLI to the **indiana-bridge-3d** project, **production** environment, **bridge-engine** service. Upload the private archive with `scripts/upload_hosted_assets.py`, passing the release directory, a new empty compact directory, the CLI executable and the selected bucket ID. The helper passes storage credentials through stdin, never command arguments or files.
4. Configure `BRIDGE_SITE_ORIGIN`, `BRIDGE_GATEWAY_SECRET`, `BRIDGE_STORAGE_JSON`, `BRIDGE_STATE_DIR=/persist` and `PORT=8080`. Set the same origin and gateway secret in Sites, with `BRIDGE_BACKEND_URL` pointing to the engine. Secret values must not enter source control or browser JavaScript.
5. Deploy the compact directory using `railway up ... --path-as-root`. It includes `Dockerfile`, `railway.json` and the immutable archive checksum. One service replica and one ASGI worker are required for the SQLite/job lock design.
6. Build, synchronize and publish the Sites gateway through the native Sites workflow. Preserve its project ID and owner-private access policy.
7. Check the hosted catalog, drawings, GLB range downloads, stored results, an actual native FEM calculation and persistence after a service restart.

The cloud catalog and local catalog are separate after initial deployment. Later structural-data revisions need an explicit catalog migration that preserves cloud analysis history; copying a seed over a live database is not supported. Take a database export and volume backup before such migrations.

## Verification

`test_hosted.py` tests gateway authorization, origin/body checks, model/PDF byte ranges, rendered drawing pages, database export, relocated saved results, repeat initialization and a real native FEM job. Set `BRIDGE_TEST_SEED` to a prepared release's seed directory before running it.

Solver source and drawing/model evidence retain raw bytes in Git because saved results use SHA-256 fingerprints. Do not normalize or reformat those files merely to prepare a release.

The hosting runtime is independent of the user's PC. Railway compute, volume and object storage are billed to the configured Railway account. Sites access is owner-private; publishing the GitHub source does not make the running Site public.
