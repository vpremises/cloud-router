"""Source-only admission for compiled routing examples; never deploy or connect."""
import re
from urllib.parse import urlsplit


def validate(config):
    for name, service in config['services'].items():
        image = service.get('image', '')
        if not re.fullmatch(r'[A-Za-z0-9:./_-]+@sha256:[0-9a-f]{64}', image):
            raise ValueError(f'{name}: a reviewed immutable image digest is required')
        if service.get('privileged') or service.get('network_mode') == 'host':
            raise ValueError(f'{name}: privileged/host networking is outside routing scope')
        for mount in service.get('volumes', []):
            if 'docker.sock' in mount.get('source', ''):
                raise ValueError(f'{name}: direct Docker socket authority is unsupported')
        for key, value in service.get('environment', {}).items():
            if key.endswith('_ENDPOINT'):
                parsed = urlsplit(value)
                if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
                    raise ValueError(f'{name}: an authenticated restricted HTTPS API owner is required')
        if any(port.get('target') == 8080 for port in service.get('ports', [])):
            raise ValueError(f'{name}: dashboard API must not be published')
        for command in (service.get('command') or []):
            if command == '--api.insecure=true':
                raise ValueError(f'{name}: insecure API is unsupported')


def main():
    import argparse
    import json
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('compiled_config', type=Path)
    args = parser.parse_args()
    try:
        with args.compiled_config.open('rb') as source:
            data = source.read(1024 * 1024 + 1)
        if len(data) > 1024 * 1024:
            raise ValueError('compiled configuration exceeds the source admission bound')
        validate(json.loads(data))
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        parser.exit(1, 'Routing source configuration refused; review the declared owner inputs.\n')
    print('Routing source configuration admitted; no deployment or connection performed.')


if __name__ == '__main__':
    main()
