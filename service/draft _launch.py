import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.config_manager import load_config

config = load_config()
chrome_path = config.get('Chrome', 'chrome_path')
draft_url = config.get('URL', 'draft_url').strip('"')

subprocess.Popen([chrome_path, draft_url])