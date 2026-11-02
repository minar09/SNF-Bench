import csv
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from summarize_existing_t2v import MODELS, build


def test_duplicate_prompt_identifiers_are_excluded_even_if_scores_agree(tmp_path):
    path = tmp_path / 'scores.csv'
    fields = ['track', 'duration', 'model', 'metric', 'prompt_id', 'value']
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for model in MODELS:
            for prompt in ['p', 'q']:
                row = dict(track='t2v', duration='60s', model=model, metric='fBD_mean', prompt_id=prompt, value='1')
                writer.writerow(row)
                if model == 'rolling_forcing' and prompt == 'p':
                    writer.writerow(row)
    metric = build(path)['metrics']['fBD_mean']
    assert metric['prompt_ids'] == ['q']
    assert metric['ambiguous_excluded'][0]['row_count'] == 2
