import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def main() -> int:
    # 项目根目录
    root = Path(__file__).parent.resolve()
    os.chdir(root)

    # 环境检查
    load_dotenv()
    missing = []
    for k in ["JIRA_BASE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN", "JIRA_PROJECT_KEY"]:
        if not os.getenv(k):
            missing.append(k)

    cfg_ok = Path("config.yml").exists()
    data_ok = Path("sample_requirements.csv").exists()

    print("=== Peak3 Demo (Python Runner) ===")
    print(f"Python: {sys.version.split()[0]}")
    print(f".env loaded: {Path('.env').exists()}")
    print(f"config.yml: {cfg_ok}")
    print(f"sample_requirements.csv: {data_ok}")
    if missing:
        print(f"Missing env keys in .env: {', '.join(missing)}")

    # Dry-run preview
    from src.convert import run as convert_run

    print("\n[1/2] Dry-run preview...")
    try:
        convert_run(
            excel_path=str(root / "sample_requirements.csv"),
            config_path=str(root / "config.yml"),
            dry_run=True,
        )
        print("[OK] Dry-run completed")
    except Exception as e:
        print("[ERROR] Dry-run failed:", e)
        return 1

    # Real creation
    print("\n[2/2] Creating real Jira tickets...")
    try:
        convert_run(
            excel_path=str(root / "sample_requirements.csv"),
            config_path=str(root / "config.yml"),
            dry_run=False,
        )
        print("[OK] Creation completed")
    except Exception as e:
        print("[ERROR] Creation failed:", e)
        print("Please check Jira credentials, network, or project permissions")
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


