#!/usr/bin/env python3
"""
Sync Verification Tool
Checks consistency between Computer A and Computer B.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

from logger import LogiLogger

logger = LogiLogger.get_logger("sync_verify")


class SyncVerifier:
    """Verify sync integrity across computers"""

    def __init__(self):
        self.repo_root = Path(__file__).parent
        self.issues = []
        self.warnings = []
        self.checks_passed = 0
        self.checks_total = 0

    def check(self, name: str, condition: bool, error_msg: str):
        """Run a check and track result"""
        self.checks_total += 1

        if condition:
            self.checks_passed += 1
            logger.info(f"✓ {name}")
            return True
        else:
            self.issues.append(f"✗ {name}: {error_msg}")
            logger.error(f"✗ {name}: {error_msg}")
            return False

    def warn(self, name: str, message: str):
        """Record a warning"""
        self.warnings.append(f"⚠ {name}: {message}")
        logger.warning(f"⚠ {name}: {message}")

    def verify_git_status(self) -> bool:
        """Verify git repository status"""
        import subprocess

        logger.info("\n[Git Status]")

        # Check if on correct branch
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            cwd=self.repo_root
        )

        current_branch = result.stdout.strip()
        expected_branch = "claude/setup-user-profile-9LdRn"

        self.check(
            "Git branch",
            current_branch == expected_branch,
            f"On {current_branch}, expected {expected_branch}"
        )

        # Check if working tree is clean
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=self.repo_root
        )

        if result.stdout.strip():
            self.warn("Working tree", "Uncommitted changes present")
        else:
            self.check("Working tree", True, "")

        # Check if synced with remote
        subprocess.run(
            ["git", "fetch", "origin", expected_branch, "--quiet"],
            cwd=self.repo_root
        )

        local_result = subprocess.run(
            ["git", "rev-parse", "@"],
            capture_output=True,
            text=True,
            cwd=self.repo_root
        )

        remote_result = subprocess.run(
            ["git", "rev-parse", "@{u}"],
            capture_output=True,
            text=True,
            cwd=self.repo_root
        )

        local_commit = local_result.stdout.strip()
        remote_commit = remote_result.stdout.strip()

        self.check(
            "GitHub sync",
            local_commit == remote_commit,
            f"Local: {local_commit[:7]}, Remote: {remote_commit[:7]}"
        )

        return True

    def verify_dependencies(self) -> bool:
        """Verify Python dependencies"""
        logger.info("\n[Dependencies]")

        venv_path = self.repo_root / "venv"

        self.check(
            "Virtual environment",
            venv_path.exists(),
            "venv/ not found"
        )

        requirements_file = self.repo_root / "requirements.txt"

        self.check(
            "requirements.txt",
            requirements_file.exists(),
            "requirements.txt not found"
        )

        return True

    def verify_configuration(self) -> bool:
        """Verify configuration files"""
        logger.info("\n[Configuration]")

        # Check .env
        env_file = self.repo_root / ".env"
        env_example = self.repo_root / ".env.example"

        if env_file.exists():
            self.check(".env file", True, "")
        else:
            self.warn(".env file", "Not found (use .env.example as template)")

        self.check(
            ".env.example",
            env_example.exists(),
            ".env.example not found"
        )

        # Check credentials
        creds_file = self.repo_root / "credentials.json"
        creds_template = self.repo_root / "credentials.json.template"

        if creds_file.exists():
            self.check("credentials.json", True, "")
        else:
            self.warn("credentials.json", "Not found")

        self.check(
            "credentials.json.template",
            creds_template.exists(),
            "Template not found"
        )

        return True

    def verify_8tb_drive(self) -> bool:
        """Verify 8TB drive setup"""
        logger.info("\n[8TB Drive]")

        drive_path = Path("/mnt/8tb_drive")

        if drive_path.exists():
            self.check("8TB drive mount", True, "")

            # Check Legacy AI directories
            legacy_ai_path = drive_path / "legacy_ai"

            if legacy_ai_path.exists():
                self.check("Legacy AI directory", True, "")

                # Check subdirectories
                for subdir in ["datasets", "models", "memory", "cache"]:
                    subdir_path = legacy_ai_path / subdir
                    if subdir_path.exists():
                        self.check(f"  {subdir}/", True, "")
                    else:
                        self.warn(f"  {subdir}/", "Not found (will be created on first use)")
            else:
                self.warn("Legacy AI directory", "Not found")
        else:
            self.warn("8TB drive mount", "Not mounted at /mnt/8tb_drive")

        return True

    def verify_ollama(self) -> bool:
        """Verify Ollama installation"""
        import subprocess

        logger.info("\n[Ollama]")

        try:
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                version = result.stdout.strip()
                self.check("Ollama installed", True, "")
                logger.info(f"  Version: {version}")
            else:
                self.warn("Ollama installed", "Command failed")

        except FileNotFoundError:
            self.warn("Ollama installed", "Not found (install: curl https://ollama.ai/install.sh | sh)")
        except Exception as e:
            self.warn("Ollama installed", f"Check failed: {e}")

        # Check if Ollama is running
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)

            if response.status_code == 200:
                self.check("Ollama running", True, "")

                # List models
                data = response.json()
                models = data.get("models", [])

                if models:
                    logger.info(f"  Models: {len(models)}")
                    for model in models[:5]:  # Show first 5
                        logger.info(f"    - {model['name']}")
                else:
                    self.warn("Ollama models", "No models found")
            else:
                self.warn("Ollama running", "Service not responding")

        except Exception as e:
            self.warn("Ollama running", f"Not running (start: ollama serve)")

        return True

    def verify_file_structure(self) -> bool:
        """Verify expected files exist"""
        logger.info("\n[File Structure]")

        required_files = [
            "google_sheets_sync.py",
            "logibot_core.py",
            "legacy_ai.py",
            "training_data_builder.py",
            "model_trainer.py",
            "health_monitor.py",
            "config.py",
            "logger.py",
            "requirements.txt",
            "setup.sh",
            "sync.sh",
            "README.md",
            "TRAINING.md"
        ]

        for filename in required_files:
            file_path = self.repo_root / filename
            self.check(
                f"  {filename}",
                file_path.exists(),
                "Not found"
            )

        return True

    def generate_report(self) -> Dict[str, Any]:
        """Generate verification report"""
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "computer": self.get_computer_info(),
            "checks_passed": self.checks_passed,
            "checks_total": self.checks_total,
            "success_rate": (self.checks_passed / self.checks_total * 100) if self.checks_total > 0 else 0,
            "issues": self.issues,
            "warnings": self.warnings,
            "status": "PASS" if len(self.issues) == 0 else "FAIL"
        }

        return report

    def get_computer_info(self) -> Dict[str, str]:
        """Get computer information"""
        import platform
        import socket

        return {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "python_version": platform.python_version()
        }

    def print_report(self, report: Dict[str, Any]):
        """Print formatted report"""
        print("\n" + "=" * 60)
        print("SYNC VERIFICATION REPORT")
        print("=" * 60)
        print(f"Computer: {report['computer']['hostname']}")
        print(f"Timestamp: {report['timestamp']}")
        print(f"Status: {report['status']}")
        print(f"Checks: {report['checks_passed']}/{report['checks_total']} passed ({report['success_rate']:.1f}%)")
        print("=" * 60)

        if report['warnings']:
            print(f"\nWarnings ({len(report['warnings'])}):")
            for warning in report['warnings']:
                print(f"  {warning}")

        if report['issues']:
            print(f"\nIssues ({len(report['issues'])}):")
            for issue in report['issues']:
                print(f"  {issue}")

        print("\n" + "=" * 60)

        if report['status'] == "PASS":
            print("✓ VERIFICATION PASSED")
        else:
            print("✗ VERIFICATION FAILED - Fix issues before syncing")

        print("=" * 60 + "\n")

    def run_all_checks(self) -> bool:
        """Run all verification checks"""
        logger.info("Starting sync verification...")

        self.verify_git_status()
        self.verify_dependencies()
        self.verify_configuration()
        self.verify_8tb_drive()
        self.verify_ollama()
        self.verify_file_structure()

        report = self.generate_report()
        self.print_report(report)

        # Save report
        report_file = self.repo_root / "logs" / f"sync_verify_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Report saved: {report_file}")

        return report['status'] == "PASS"


def main():
    """Main execution"""
    verifier = SyncVerifier()
    success = verifier.run_all_checks()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
