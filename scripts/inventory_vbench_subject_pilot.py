"""Inventory pre-screened VBench-I2V subject candidates; no benchmark admission."""
import hashlib
import json
from pathlib import Path

ROOT = Path('/home/minar/ar-image-animation')
OOS = ROOT / 'prompts/oos'
SOURCES = OOS / 'vbench_i2v_download'
CROPS = OOS / 'oos_v2_60s'
VIDEOS = ROOT / 'results/research/oos_samples_oct27/scenetether_seed42_60s_oos_v2'
OUTPUT = Path('manifest/vbench_subject_pilot_inventory_2026_10_30.json')
CANDIDATES = {
    'ovb05': 'perched bird; shallow focus challenges support registration',
    'ovb11': 'bear with water and fish; subject/material separation',
    'ovb12': 'grazing hippopotamus; facial and mouth motion',
    'ovb13': 'otter beside water; subject/material and contact',
    'ovb14': 'standing cow; low-amplitude head and body motion',
    'ovb15': 'red panda feeding; close-up articulation and occlusion',
    'ovb16': 'panda feeding; mouth, paw and bamboo interaction',
    'ovb17': 'frog on lily pads; near-static and small subject',
    'ovb20': 'squirrel feeding; fine paw motion and food contact',
    'ovb21': 'two grazing sheep; multi-subject tracking and occlusion',
    'ovb22': 'perched butterfly; small articulated subject and shallow focus',
    'ovb27': 'adult saxophonist; hands, instrument and background people',
    'ovb29': 'adult holding a flower; face and hand consistency',
    'ovb30': 'adult guitarist; repeated articulated action and contact',
}


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def inventory():
    crops = {x['id']: x for x in json.loads((CROPS / 'target_crop_info_26-15.json').read_text())}
    originals = {x['file']: x for x in json.loads((SOURCES / 'manifest.json').read_text()) if 'file' in x}
    videos = list(VIDEOS.glob('*.mp4'))
    rows = []
    for sid, reason in CANDIDATES.items():
        item = crops[sid]
        original = SOURCES / item['source_file']
        crop = CROPS / '26-15' / item['file_name']
        original_meta = originals[original.name]
        matches = [v for v in videos if v.stem == item['caption'][:100]]
        if sha(original) != item['source_sha256'] or sha(original) != original_meta['sha256']:
            raise ValueError(f'{sid}: source image hash mismatch')
        if len(matches) != 1:
            raise ValueError(f'{sid}: expected one render, got {len(matches)}')
        rows.append(dict(id=sid, track='human' if item['type'] == 'person' else 'animal',
                         visual_screen_reason=reason, original_caption=original_meta['caption'],
                         evaluation_prompt=item['caption'], source_file=item['source_file'],
                         source_sha256=item['source_sha256'], crop_file=item['file_name'],
                         crop_sha256=sha(crop), crop_box=item['crop_box'],
                         render_filename=matches[0].name, render_sha256=sha(matches[0]),
                         origin_url=original_meta.get('origin_url'), mirror=original_meta.get('mirror'),
                         selection_status='exploratory_previously_seen_requires_annotation_and_rights_review'))
    return dict(status='complete', scope='exploratory subject-track candidates, not a held-out benchmark',
                source_metadata_sha256=sha(SOURCES / 'manifest.json'),
                crop_metadata_sha256=sha(CROPS / 'target_crop_info_26-15.json'),
                selection_method='manual visual screening of 30 local VBench-I2V crops, based on localized sustained-action plausibility; no generated-video quality selection',
                independent_source_or_model_blinding=False,
                limitations=['not independently sampled or preregistered', 'source rights and applicable releases not verified',
                             'fixed-camera behavior cannot be established from an image alone', 'source role masks and human validation absent',
                             'existing SceneTether samples are exploratory; no matched baseline or seeds'],
                rows=rows)


if __name__ == '__main__':
    if OUTPUT.exists():
        raise SystemExit('output exists; preserve the existing inventory')
    result = inventory()
    OUTPUT.write_text(json.dumps(result, indent=2) + '\n')
    print(f"inventoried {len(result['rows'])} sources: {OUTPUT}")
