#!/usr/bin/env python3
"""
.claude内の既存ファイルで必要なパッケージのみをインストールするスクリプト
"""
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """コマンドを実行してエラーをハンドリング"""
    print(f"\n{description}...")
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"✓ {description} 完了")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} 中にエラー: {e}")
        return False

def check_and_install_packages():
    """既存の.claudeディレクトリ内のスクリプトに必要なパッケージをインストール"""
    
    print("🔍 .claude ディレクトリの既存ファイルを確認中...")
    
    claude_dir = Path(".claude")
    scripts_dir = claude_dir / "scripts"
    
    # ディレクトリ作成
    if not claude_dir.exists():
        print("📁 .claude ディレクトリが見つかりません。作成します...")
        claude_dir.mkdir(exist_ok=True)
        print("✓ .claude ディレクトリを作成しました")
    
    if not scripts_dir.exists():
        scripts_dir.mkdir(exist_ok=True)
        print("✓ .claude/scripts ディレクトリを作成しました")
    
    # 必要なスクリプトファイルを作成
    script_files = {
        "git_pr_create.sh": '''#!/usr/bin/env bash

# メイン処理を関数にラップ
main() {
    #-----------------------------
    # 0. Gitリポジトリかチェック
    #-----------------------------
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo "[git_pr_create] Not in a git repository. Skipping."
        return 0
    fi

    # Gitリポジトリ内であることが確認できたらset -euo pipefailを有効化
    set -euo pipefail

    #-----------------------------
    # 1. GitHub CLIがインストールされているかチェック
    #-----------------------------
    if ! command -v gh > /dev/null 2>&1; then
        echo "[git_pr_create] GitHub CLI (gh) is not installed. Skipping."
        return 0
    fi

    #-----------------------------
    # 2. コミットが必要か判定
    #-----------------------------
    git add -A
    if git diff --cached --quiet; then
        echo "[git_pr_create] No changes to commit. Skipping PR creation."
        return 0
    fi

    #-----------------------------
    # 3. コミット
    #-----------------------------
    git commit -m 'auto: passed hooks'

    #-----------------------------
    # 4. ブランチ作成 & プッシュ
    #-----------------------------
    BRANCH="claude-auto-$(date +%s)"
    git switch -c "${BRANCH}"
    git push -u origin "${BRANCH}"

    #-----------------------------
    # 5. PR 作成（GitHub CLI）
    #-----------------------------
    #   - --fill  : コミットメッセージをタイトル/本文に転用
    #   - --draft : 下書きPR。不要なら外す
    #   - --base  : マージ先ブランチ（例: main）
    gh pr create --fill --head "${BRANCH}" --base main --draft

    echo "[git_pr_create] Pull Request created successfully."
}

# エラーを完全に抑制してメイン処理を実行
main 2>/dev/null || true
''',
        "ruff_gate_post.sh": '''#!/usr/bin/env bash
set -euo pipefail

# Check if ruff is installed
if ! python3 -m ruff --version &> /dev/null; then
  # Ruff is not installed, skip linting
  echo "Ruff is not installed. Skipping Python linting."
  echo "To install ruff, run: pip3 install ruff"
  exit 0
fi

# ruff は stdout に警告を、exit=1 で終了する
# python3を使用（多くのシステムでのデフォルト）
R="$(python3 -m ruff check . 2>&1)" || status=$? || true

if [[ "${status:-0}" -ne 0 ]]; then
  # Claude に自動修正させたいので JSON を stdout
  jq -n --arg reason "$R" '{"decision":"block","reason":$reason}'
  exit 0             # ← exit 0 で OK、decision:block が効く
fi

# 警告ゼロなら正常終了
exit 0
'''
    }
    
    print("\n📝 必要なスクリプトファイルを作成中...")
    for filename, content in script_files.items():
        script_path = scripts_dir / filename
        if not script_path.exists():
            script_path.write_text(content)
            script_path.chmod(0o755)
            print(f"  ✓ {filename} を作成しました")
        else:
            print(f"  ✓ {filename} は既に存在します")
    
    # settings.local.json ファイルも作成
    settings_file = claude_dir / "settings.local.json"
    if not settings_file.exists():
        settings_content = {
            "permissions": {
                "allow": [
                    "Bash(*)"
                ],
                "deny": [
                    "Bash(rm -rf*)",
                    "Bash(python3:*)"
                ]
            },
            "hooks": {
                "PostToolUse": [
                    {
                        "matcher": "Write|Edit|Update",
                        "hooks": [
                            {
                                "type": "command",
                                "command": "/bin/bash .claude/scripts/ruff_gate_post.sh"
                            }
                        ]
                    }
                ],
                "Stop": [
                    {
                        "matcher": "*",
                        "hooks": [
                            {
                                "type": "command",
                                "command": "/bin/bash .claude/scripts/git_pr_create.sh"
                            }
                        ]
                    }
                ]
            }
        }
        import json
        settings_file.write_text(json.dumps(settings_content, indent=2))
        print("  ✓ settings.local.json を作成しました")
    else:
        print("  ✓ settings.local.json は既に存在します")
    
    # 必要なパッケージリスト（既存ファイルの分析結果）
    required_packages = {
        "python": [
            "ruff",  # ruff_gate_post.sh で使用
        ],
        "system": [
            "gh",    # git_pr_create.sh で使用 (GitHub CLI)
            "jq",    # ruff_gate_post.sh で使用
        ]
    }
    
    print("\n📦 必要なパッケージ:")
    print("  Python:")
    for pkg in required_packages["python"]:
        print(f"    - {pkg}")
    print("  システムツール:")
    for pkg in required_packages["system"]:
        print(f"    - {pkg}")
    
    # Python パッケージのインストール
    if required_packages["python"]:
        print("\n🐍 Python パッケージをインストール中...")
        for pkg in required_packages["python"]:
            # パッケージがインストール済みかチェック
            check_cmd = f"python3 -m pip show {pkg}"
            try:
                subprocess.run(check_cmd, shell=True, check=True, capture_output=True)
                print(f"  ✓ {pkg} は既にインストール済み")
            except subprocess.CalledProcessError:
                # インストールされていない場合はインストール
                install_cmd = f"python3 -m pip install {pkg}"
                if run_command(install_cmd, f"{pkg} をインストール"):
                    print(f"  ✓ {pkg} をインストールしました")
                else:
                    print(f"  ⚠ {pkg} のインストールに失敗しました")
    
    # システムツールの確認
    print("\n🛠️  システムツールを確認中...")
    for tool in required_packages["system"]:
        check_cmd = f"which {tool}"
        try:
            subprocess.run(check_cmd, shell=True, check=True, capture_output=True)
            print(f"  ✓ {tool} は利用可能")
        except subprocess.CalledProcessError:
            print(f"  ⚠ {tool} がインストールされていません")
            if tool == "gh":
                print("    → GitHub CLI のインストール: https://cli.github.com/")
            elif tool == "jq":
                print("    → jq のインストール: sudo apt-get install jq (Ubuntu/Debian)")
                print("                      brew install jq (macOS)")
    
    # スクリプトの実行権限を設定
    print("\n🔧 スクリプトに実行権限を設定中...")
    scripts_dir = claude_dir / "scripts"
    if scripts_dir.exists():
        for script in scripts_dir.glob("*.sh"):
            try:
                script.chmod(0o755)
                print(f"  ✓ {script.name} に実行権限を付与")
            except Exception as e:
                print(f"  ⚠ {script.name} の権限設定に失敗: {e}")

def main():
    """メイン関数"""
    print("🚀 .claude 最小セットアップスクリプト")
    print("="*50)
    print("既存の .claude ディレクトリ内のファイルに必要なパッケージのみをインストールします")
    
    check_and_install_packages()
    
    print("\n" + "="*50)
    print("✅ セットアップ完了!")
    print("\n既存のスクリプト:")
    print("  - .claude/scripts/git_pr_create.sh : 自動PR作成")
    print("  - .claude/scripts/ruff_gate_post.sh : Pythonコードチェック")

if __name__ == "__main__":
    main()