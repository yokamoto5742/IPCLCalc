import logging
import subprocess

from service.automation_service import IPCLOrderAutomation
from service.draft_launch import launch_draft_page
from utils.config_manager import load_config
from utils.log_rotation import setup_logging


def main():
    config = load_config()
    log_directory = config.get('LOGGING', 'log_directory', fallback='logs')
    log_retention_days = config.getint('LOGGING', 'log_retention_days', fallback=7)

    setup_logging(log_directory=log_directory, log_retention_days=log_retention_days)

    logger = logging.getLogger(__name__)
    logger.info("IPCLCalc アプリケーションを開始します")

    try:
        automation = IPCLOrderAutomation()
        automation.process_all_csv_files()
        launch_draft_page()
        subprocess.Popen(['explorer', str(automation.pdf_dir)])
        logger.info("IPCLCalc アプリケーションが正常に完了しました")
    except Exception as e:
        logger.exception(f"アプリケーション実行中にエラーが発生しました: {e}")
        raise


if __name__ == "__main__":
    main()
