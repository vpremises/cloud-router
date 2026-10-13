import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('routing', ROOT / 'scripts/validate_config.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
INPUTS = {'TRAEFIK_IMAGE': 'example.invalid/traefik@sha256:' + '1' * 64,
          'WHOAMI_IMAGE': 'example.invalid/whoami@sha256:' + '2' * 64,
          'DOCKER_API_ENDPOINT': 'https://restricted-api.invalid:2376',
          'ACME_EMAIL': 'operator@example.invalid', 'APP_HOST': 'application.example.invalid',
          'ADMIN_AUTH_USERS': 'synthetic:$apr1$fixture$synthetic-hash'}


def compile_config(files, missing=None):
    env = dict(os.environ)
    env.update(INPUTS)
    if missing:
        env.pop(missing, None)
    command = ['docker', 'compose', '--env-file', '/dev/null']
    for file in files:
        command += ['-f', str(ROOT / file)]
    return subprocess.run(command + ['config', '--format', 'json'], env=env,
                          capture_output=True, text=True, timeout=20, check=False)


class RoutingSource(unittest.TestCase):
    def test_supported_proxy_configurations(self):
        for folder, filename in [('file-swarm', 'compose.http.yaml'),
                                 ('swarm-only', 'compose.http.yaml'),
                                 ('domain-tsl', 'compose.https.yaml')]:
            with self.subTest(folder=folder):
                result = compile_config([f'{folder}/{filename}'])
                self.assertEqual(result.returncode, 0, result.stderr)
                MODULE.validate(json.loads(result.stdout))
                config = tomllib.loads((ROOT / folder / 'config/traefik.toml').read_text())
                self.assertFalse(config['api']['insecure'])
                self.assertFalse(config['api']['dashboard'])
                for provider in ('docker', 'swarm'):
                    if provider in config['providers']:
                        self.assertFalse(config['providers'][provider]['exposedByDefault'])

    def test_required_owner_inputs_fail_closed(self):
        for required in ('TRAEFIK_IMAGE', 'DOCKER_API_ENDPOINT', 'ACME_EMAIL'):
            with self.subTest(required=required):
                result = compile_config(['domain-tsl/compose.https.yaml'], missing=required)
                self.assertNotEqual(result.returncode, 0)

    def test_declared_application_samples(self):
        for folder in ('file-swarm', 'swarm-only'):
            result = compile_config([f'{folder}/stack-samples/compose.sample.yaml'])
            self.assertEqual(result.returncode, 0, result.stderr)
            config = json.loads(result.stdout)
            MODULE.validate(config)
            labels = config['services']['whoami']['deploy']['labels']
            self.assertEqual(labels['traefik.http.routers.sample-whoami.rule'],
                             'Host(`application.example.invalid`)')

    def test_optional_auth_has_no_shared_credential(self):
        files = ['file-swarm/compose.http.yaml', 'addon/override.basic-auth.yaml']
        self.assertNotEqual(compile_config(files, missing='ADMIN_AUTH_USERS').returncode, 0)
        result = compile_config(files)
        self.assertEqual(result.returncode, 0, result.stderr)
        labels = json.loads(result.stdout)['services']['proxy']['labels']
        # Compose emits escaped dollars for a round-trippable config document.
        self.assertEqual(labels['traefik.http.middlewares.admin-auth.basicauth.users'].replace('$$', '$'), INPUTS['ADMIN_AUTH_USERS'])

    def test_untrusted_configuration_is_refused(self):
        result = compile_config(['file-swarm/compose.http.yaml'])
        self.assertEqual(result.returncode, 0, result.stderr)
        initial = json.loads(result.stdout)
        for change in (lambda s: s.update(image='traefik:latest'),
                       lambda s: s.update(privileged=True),
                       lambda s: s.update(volumes=[{'source': '/var/run/docker.sock'}]),
                       lambda s: s['environment'].update(TRAEFIK_PROVIDERS_SWARM_ENDPOINT='http://api.invalid:2375'),
                       lambda s: s.update(command=['--api.insecure=true'])):
            config = copy.deepcopy(initial)
            change(config['services']['proxy'])
            with self.assertRaises(ValueError):
                MODULE.validate(config)


if __name__ == '__main__':
    unittest.main()
