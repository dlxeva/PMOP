import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / 'scripts'))
from demo import create_example
from orchestration_state import validate_root, collect_owner_gates
from capability_index import build_index


class StateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        create_example(self.root)

    def edit(self, name, mutate):
        p = self.root / name
        value = json.loads(p.read_text())
        mutate(value)
        p.write_text(json.dumps(value))

    def test_example_valid(self):
        self.assertTrue(validate_root(str(self.root)).valid)

    def test_owner_inbox_readonly(self):
        before = {p.name: p.read_bytes() for p in self.root.iterdir()}
        result = validate_root(str(self.root))
        self.assertEqual(len(collect_owner_gates([result])), 1)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.root.iterdir()})

    def test_mismatched_identity(self):
        self.edit('ORCHESTRATION.json', lambda d: d.update(project_id='different'))
        self.assertFalse(validate_root(str(self.root)).valid)

    def test_invalid_revision(self):
        for value in [True, 0, -1, '1', [], {}]:
            with self.subTest(value=value):
                self.edit('ORCHESTRATION.json', lambda d: d.update(revision=value))
                self.assertFalse(validate_root(str(self.root)).valid)

    def test_malformed_enum_and_schema(self):
        for value in [[], {}, True, '2']:
            with self.subTest(value=value):
                create_example(self.root)
                self.edit('PROJECT_MASTER.json', lambda d: d.update(schema_version=value))
                self.assertFalse(validate_root(str(self.root)).valid)
        for key in ['visible_child_threads', 'local_commit']:
            create_example(self.root)
            self.edit('PROJECT_MASTER.json', lambda d: d['policy'].update({key: []}))
            self.assertFalse(validate_root(str(self.root)).valid)

    def test_invalid_gate_reference(self):
        self.edit('ORCHESTRATION.json', lambda d: d['owner_gates'][0].update(related_outcome_key=[]))
        self.assertFalse(validate_root(str(self.root)).valid)

    def test_invalid_not_aggregated(self):
        self.edit('ORCHESTRATION.json', lambda d: d.update(revision=0))
        self.assertEqual(collect_owner_gates([validate_root(str(self.root))]), [])

    def test_timezone_required(self):
        self.edit('ORCHESTRATION.json', lambda d: d.update(updated_at='2026-01-01'))
        self.assertFalse(validate_root(str(self.root)).valid)

    def test_missing_file_and_bad_json(self):
        p = self.root / 'ORCHESTRATION.json'
        p.unlink()
        self.assertFalse(validate_root(str(self.root)).valid)
        p.write_text('{bad')
        self.assertFalse(validate_root(str(self.root)).valid)
        p.write_bytes(b'\xff\xfe')
        self.assertFalse(validate_root(str(self.root)).valid)

    def test_gate_cannot_override_project_identity(self):
        self.edit('ORCHESTRATION.json', lambda d: d['owner_gates'][0].update(
            project_id='spoof', project_name='spoof', project_root='/spoof'))
        result = validate_root(str(self.root))
        self.assertTrue(result.valid)
        gate = collect_owner_gates([result])[0]
        self.assertEqual(gate['project_id'], result.manifest['project_id'])
        self.assertEqual(gate['project_name'], result.manifest['project_name'])
        self.assertEqual(gate['project_root'], str(self.root.resolve()))

    def test_route_invariants(self):
        base = {'outcome_key': 'synthetic-outcome', 'title': 'Synthetic task',
                'priority': 1, 'route': 'isolated_task', 'status': 'running',
                'thread': {'thread_id': 'synthetic-child', 'host_id': 'local', 'title': 'Synthetic'},
                'scope': {'allowed': [str(self.root)], 'protected': []},
                'last_verified': {'at': '2026-01-01T00:00:00Z', 'claim': 'Fixture only', 'evidence': ['synthetic']},
                'next_action': 'Verify synthetic fixture'}
        self.edit('ORCHESTRATION.json', lambda d: d.update(active_outcomes=[base]))
        self.assertTrue(validate_root(str(self.root)).valid)
        cases = []
        for count in [2, 4]:
            cases.append([copy.deepcopy(base) for _ in range(count)])
        for key, value in [('priority', 2), ('status', []), ('route', {})]:
            item = copy.deepcopy(base); item[key] = value; cases.append([item])
        item = copy.deepcopy(base); item['thread']['thread_id'] = 'current-thread-id'; cases.append([item])
        for outcomes in cases:
            with self.subTest(outcomes=outcomes):
                self.edit('ORCHESTRATION.json', lambda d: d.update(active_outcomes=outcomes))
                self.assertFalse(validate_root(str(self.root)).valid)

    def test_capability_explicit_roots(self):
        p = self.root / 'skills'; p.mkdir()
        for child in ['a', 'b']:
            (p / child).mkdir(); (p / child / 'SKILL.md').write_text('synthetic')
        (self.root / 'SKILL.md').write_text('outside')
        (p / 'escape').mkdir(); (p / 'escape' / 'SKILL.md').symlink_to(self.root / 'SKILL.md')
        index = build_index([p])
        self.assertEqual(len(index['skills']), 2)
        self.assertTrue(all(row['exact_duplicate'] for row in index['skills']))
        self.assertNotIn(str(self.root), json.dumps(index))

    def test_cli_errors_without_traceback(self):
        self.edit('ORCHESTRATION.json', lambda d: d['governance'].update(status=[]))
        result = subprocess.run([sys.executable, str(BASE/'scripts/orchestration_state.py'),
                                 'validate', '--root', str(self.root), '--json'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)['valid'])
        self.assertNotIn('Traceback', result.stderr)

    def test_demo_uses_utf8_with_legacy_output_encoding(self):
        result = subprocess.run(
            [sys.executable, str(BASE / 'scripts/demo.py')],
            env=dict(os.environ, PYTHONIOENCODING='ascii'), capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr.decode('utf-8'))
        self.assertIn('需要我拍板', result.stdout.decode('utf-8'))

    def test_cli_requires_inventory_scope(self):
        result = subprocess.run([sys.executable, str(BASE/'scripts/capability_index.py')], capture_output=True)
        self.assertEqual(result.returncode, 2)


if __name__ == '__main__':
    unittest.main()
