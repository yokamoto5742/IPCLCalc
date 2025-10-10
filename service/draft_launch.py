import subprocess

from utils.config_manager import load_config


def launch_draft_page():
    config = load_config()
    chrome_path = config.get('Chrome', 'chrome_path')
    draft_url = config.get('URL', 'draft_url').strip('"')
    subprocess.Popen([chrome_path, draft_url])


if __name__ == "__main__":
    launch_draft_page()