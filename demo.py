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

    # Dry-run 预览
    from src.convert import run as convert_run

    print("\n[1/2] Dry-run 预览...")
    try:
        convert_run(
            excel_path=str(root / "sample_requirements.csv"),
            config_path=str(root / "config.yml"),
            dry_run=True,
        )
        print("✓ Dry-run 完成")
    except Exception as e:
        print("✗ Dry-run 失败:", e)
        return 1

    # 实际创建
    print("\n[2/2] 创建真实 Jira 工单...")
    try:
        convert_run(
            excel_path=str(root / "sample_requirements.csv"),
            config_path=str(root / "config.yml"),
            dry_run=False,
        )
        print("✓ 创建完成")
    except Exception as e:
        print("✗ 创建失败:", e)
        print("请检查 Jira 凭证、网络 或 项目权限")
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


