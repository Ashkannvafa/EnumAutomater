import subprocess
import os
import glob
import shutil
import questionary
import time
import sys
from datetime import datetime

# --- UI & Visuals ---
GREEN = '\033[92m'
BOLD = '\033[1m'
RESET = '\033[0m'

def typing_effect(text, speed=0.03):
    """Prints text line-by-line for an offensive security aesthetic."""
    for line in text.splitlines():
        print(line)
        time.sleep(speed)

def display_banner():
    banner = f"""{GREEN}{BOLD}
  ███████╗███╗   ██╗██╗   ██╗███╗   ███╗
  ██╔════╝████╗  ██║██║   ██║████╗ ████║
  █████╗  ██╔██╗ ██║██║   ██║██╔████╔██║
  ██╔══╝  ██║╚██╗██║██║   ██║██║╚██╔╝██║
  ███████╗██║ ╚████║╚██████╔╝██║ ╚═╝ ██║
  ╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝     ╚═╝
                                        
  █████╗ ██╗   ██╗████████╗ ██████╗ ███╗   ███╗ █████╗ ████████╗███████╗██████╗ 
 ██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗████╗ ████║██╔══██╗╚══██╔══╝██╔════╝██╔══██╗
 ███████║██║   ██║   ██║   ██║   ██║██╔████╔██║███████║   ██║   █████╗  ██████╔╝
 ██╔══██║██║   ██║   ██║   ██║   ██║██║╚██╔╝██║██╔══██║   ██║   ██╔══╝  ██╔══██╗
 ██║  ██║╚██████╔╝   ██║   ╚██████╔╝██║ ╚═╝ ██║██║  ██║   ██║   ███████╗██║  ██║
 ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝

       [+] Orchestrated Reconnaissance Framework v1.0
       [+] Created by Ashkannvafa
{RESET}"""
    typing_effect(banner)

# --- Logic & Automation ---
SEARCH_PATHS = [
    "/usr/share/wordlists",
    "/usr/share/dirb",
    "/usr/share/seclists",
    os.path.expanduser("~")
]

def check_dependencies():
    tools = ["nmap", "gobuster"]
    missing = [t for t in tools if shutil.which(t) is None]
    if missing:
        print(f"\n[!] Missing tools: {', '.join(missing)}")
        print("[!] Install with: sudo apt install nmap gobuster")
        return False
    return True

def get_wordlist(task_type):
    keywords = ["subdomain", "dns"] if task_type == 'dns' else ["dir", "common", "web"]
    found_files = []

    print(f"[*] Searching system for {task_type} wordlists...")
    for path in SEARCH_PATHS:
        if os.path.exists(path):
            files = glob.glob(f"{path}/**/*.txt", recursive=True)
            for f in files:
                if any(kw in f.lower() for kw in keywords):
                    found_files.append(f)

    found_files = sorted(list(set(found_files)))[:15]
    choices = found_files + ["--- Enter Custom Path ---"]

    choice = questionary.select(f"Select {task_type.upper()} Wordlist:", choices=choices).ask()
    return questionary.path("Enter path:").ask() if "Custom" in choice else choice

def run_tool(cmd, target):
    if not os.path.exists("reports"): os.makedirs("reports")
    log_file = f"reports/{target}_{datetime.now().strftime('%H%M')}.txt"
    
    print(f"\n[+] Executing: {' '.join(cmd)}")
    print(f"[+] Output logging to: {log_file}\n" + "="*40)

    with open(log_file, "a") as f:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            print(line, end="")
            f.write(line)
        process.wait()

def main():
    display_banner()
    if not check_dependencies(): return

    target = questionary.text("Enter target (Domain or IP):").ask()
    if not target: return

    task = questionary.select(
        "What is the objective?",
        choices=["Map Ports (Nmap)", "Find Subdomains (Gobuster DNS)", "Scan Directories (Gobuster Dir)"]
    ).ask()

    intensity = questionary.select(
        "Scan Intensity:",
        choices=["Fast/Surface", "Standard", "Deep/Aggressive"]
    ).ask()

    cmd = []
    if "Nmap" in task:
        flags = {"Fast/Surface": ["-F"], "Standard": ["-sV"], "Deep/Aggressive": ["-p-", "-A"]}
        cmd = ["nmap"] + flags[intensity] + [target]
    
    elif "DNS" in task:
        w = get_wordlist('dns')
        # Use --domain to avoid -d (delay) flag collision
        cmd = ["gobuster", "dns", "--domain", target, "-w", w]
    
    elif "Dir" in task:
        w = get_wordlist('dir')
        url = f"http://{target}" if "http" not in target else target
        cmd = ["gobuster", "dir", "-u", url, "-w", w]

    if cmd:
        run_tool(cmd, target)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] User interrupted. Exiting...")
        sys.exit(0)
