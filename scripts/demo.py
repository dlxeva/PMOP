#!/usr/bin/env python3
"""Create a synthetic sandbox, validate it and print its read-only owner inbox."""
import json
import sys
import tempfile
from pathlib import Path
from orchestration_state import validate_root, collect_owner_gates, render_markdown


def create_example(root: Path) -> None:
    templates = Path(__file__).resolve().parent.parent / 'templates'
    for name in ['PROJECT_MASTER.json', 'ORCHESTRATION.json']:
        data = json.loads((templates / name).read_text(encoding='utf-8'))
        if name == 'PROJECT_MASTER.json':
            data['governance_root'] = str(root)
            data['code_roots'] = [str(root)]
            data['state_backend']['orchestration_file'] = str(root / 'ORCHESTRATION.json')
            data['project_name'] = 'Fictional Documentation Project'
        else:
            data['owner_gates'] = [{
                'gate_id': 'DEMO-001', 'type': 'owner_decision', 'status': 'open',
                'blocking': True, 'request': 'Choose a license after rights review',
                'why_owner_only': 'Copyright ownership is not established by tests',
                'recommendation': 'Keep the prototype local until reviewed',
                'risk': 'Publishing without rights may disclose protected material',
                'estimated_minutes': 10, 'resume_action': 'Review the release candidate',
                'related_outcome_key': None}]
        (root / name).write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    # CLI output is UTF-8 even on legacy Windows locales or redirected pipes.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix='orchestration-demo-') as name:
        root = Path(name)
        create_example(root)
        result = validate_root(str(root))
        if not result.valid:
            raise SystemExit(str(result.errors))
        print('Synthetic demo validated. No real projects or host settings read.\n')
        print(render_markdown(collect_owner_gates([result])))
