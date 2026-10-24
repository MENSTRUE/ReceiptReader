from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT / 'models'
REQUIRED_FIELDS = ('company', 'date', 'address', 'total')
