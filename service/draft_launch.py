import webbrowser

from utils.config_manager import load_config


def launch_draft_page():
    config = load_config()
    draft_url = config.get('URL', 'draft_url').strip('"')
    webbrowser.open(draft_url)


if __name__ == "__main__":
    launch_draft_page()