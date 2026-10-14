# cloud-router

Study how a Swarm deployment can route application traffic through Traefik.

## What you can do

- Review service routing and explicit image references.
- Separate routing from privileged management services.

## Current scope

These are deployment examples. Review the restricted Docker API endpoint, images and management-service privileges before running them; no stack is deployed automatically.

Package distribution is not activated by this documentation. Use the checked-in source and the declared dependency versions; published availability must be verified separately.

## Getting started

Start with the implementation and examples linked below. Review registered configuration and prerequisites before running a command that writes state or contacts a service.

## Documentation and source

[Interface reference](docs/interface-reference.md)

[Usage guide](docs/getting-started.md)

[Contributing](CONTRIBUTING.md) · [Security reporting](SECURITY.md) · [License](LICENSE) · [Attribution notices](NOTICE)

[OSS responsibility and source completion](docs/oss-source-contract.md) defines the supported package boundary and required acceptance. It does not declare unexecuted source, distribution or production checks complete.

## Routing source acceptance

Run `python3 -m unittest discover -s tests -v` with Python 3.12+ and Docker
Compose. Tests use synthetic image digests, hostnames and contact information;
`docker compose config` renders locally without pulling an image, starting a
container or contacting a Docker API. This proves configuration composition and
refusal of missing/unsafe inputs, not a live Traefik or TLS acceptance.

Supported routing templates are `file-swarm/compose.http.yaml`,
`swarm-only/compose.http.yaml` and `domain-tsl/compose.https.yaml`, plus their
explicit whoami samples. Management/WIP examples are historical and outside this
routing acceptance. Use reviewed digest references for `TRAEFIK_IMAGE` and
`WHOAMI_IMAGE`, a restricted HTTPS `DOCKER_API_ENDPOINT`, and an explicit
`APP_HOST`. HTTPS additionally requires operator `ACME_EMAIL` and private ACME
storage; certificate issuance is separate. Optional basic-auth middleware requires
`ADMIN_AUTH_USERS` from the operator's htpasswd generation, has no shared default,
and must be attached to the intended application router explicitly.

Render a chosen template with `docker compose -f <template> config --format json`
and validate its saved JSON with `python3 scripts/validate_config.py <file.json>`
before separately reviewing deployment. Admission checks immutable image digests,
API endpoint scope and privilege exposure; it cannot establish image provenance,
endpoint authorization or actual certificate validity.

Dependency updates: [repository policy](docs/dependency-updates.md).
