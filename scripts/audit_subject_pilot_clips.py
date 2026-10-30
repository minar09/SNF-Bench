"""Verify media readiness of the exploratory VBench subject render inventory."""
import json
from pathlib import Path

import cv2
from inventory_vbench_subject_pilot import OUTPUT as INPUT, VIDEOS, sha

OUTPUT = Path('manifest/vbench_subject_clip_audit_2026_10_30.json')


def audit():
    inventory = json.loads(INPUT.read_text())
    rows = []
    for item in inventory['rows']:
        p = VIDEOS / item['render_filename']
        cap = cv2.VideoCapture(str(p))
        fps = cap.get(cv2.CAP_PROP_FPS)
        n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        decodes = []
        for idx in (0, max(0, n // 2), max(0, n - 1)):
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ok, frame = cap.read()
            decodes.append(bool(ok and frame is not None))
        cap.release()
        hash_ok = sha(p) == item['render_sha256']
        valid = all(decodes) and hash_ok and fps > 0 and n > 0
        rows.append({'id': item['id'], 'status': 'PASS' if valid else 'FAIL', 'sha256_matches': hash_ok,
                     'fps': fps, 'frame_count': n, 'duration_seconds_estimate': n / fps if fps else None,
                     'width': width, 'height': height, 'first_middle_last_decoded': decodes})
    return {'status': 'complete' if all(x['status'] == 'PASS' for x in rows) else 'failed',
            'scope': 'container metadata and three-frame decode smoke check; no video quality or motion evaluation',
            'inventory_sha256': sha(INPUT), 'rows': rows}


if __name__ == '__main__':
    if OUTPUT.exists():
        raise SystemExit('output exists')
    data = audit()
    OUTPUT.write_text(json.dumps(data, indent=2, allow_nan=False) + '\n')
    print(data['status'], len(data['rows']), OUTPUT)
    raise SystemExit(0 if data['status'] == 'complete' else 1)
