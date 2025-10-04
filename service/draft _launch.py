import subprocess

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
draft_url = "https://www.ipcl-jp.com/awsystem/order/drafts"

subprocess.Popen([chrome_path, draft_url])