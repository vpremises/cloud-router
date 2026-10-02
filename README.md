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
