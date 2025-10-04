from service.automation_service import IPCLOrderAutomation
from service.draft_launch import launch_draft_page


def main():
    automation = IPCLOrderAutomation()
    automation.process_all_csv_files()
    launch_draft_page()


if __name__ == "__main__":
    main()
