#!/usr/bin/env bash

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
    # 未コミットの変更をチェック
    if git diff --quiet && git diff --cached --quiet && ! git ls-files --others --exclude-standard | grep -q .; then
        echo "[git_pr_create] No changes to commit. Skipping PR creation."
        return 0
    fi
    
    # 変更をステージング
    git add -A

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
