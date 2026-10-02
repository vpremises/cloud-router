# Cloud Router

Finding the best practice of edge routing with docker swarm &amp; traefik.

## Status

The structure is changed for each directory.

### file-swarm 

Use File provider and Swarm provider.

Run a standalone docker container with file provider to proxy swarm overlay network.

### swarm-only (wip)

Use Swarm provider only.

Swarm cluster include traefik container routing all service.

Work in progress but this structure may not work in traefik V3 yet...

## Image source and deployment inputs

Image build sources are maintained independently in [port-office](https://github.com/vpremises/port-office). Before using these examples, set `TRAEFIK_IMAGE` to an available, inspected image digest. The planned `ghcr.io/vpremises` namespace is not populated by this source migration. Compose refuses a missing image setting. Registry publication, Swarm deployment, host names, credentials, and TLS configuration remain explicit operator inputs.

## Security defaults

Traefik dashboard exposure is disabled, the insecure API port is not published, and debug logging is disabled. Routing requires explicit labels. Traefik examples require `DOCKER_API_ENDPOINT` for an operator-managed restricted Docker API proxy; they do not mount the host Docker socket. Configure endpoint authorization and TLS before deployment. The separate Swarmpit/Portainer examples are management applications with elevated Docker privileges and require a restricted administrative network and explicit operator approval. Historical image versions must undergo a full vulnerability review before any production release.
