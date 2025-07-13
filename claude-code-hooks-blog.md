# Claude Code Hooksについて：開発ワークフローを自動化する強力な仕組み

## はじめに

Claude Codeは、開発者の生産性を向上させるAIアシスタントとして知られていますが、その中でも「Hooks」機能は特に強力な仕組みです。本記事では、Claude Code Hooksの技術的な詳細と、実際の活用方法について解説します。

## Claude Code Hooksとは

Claude Code Hooksは、Claude Codeのツール実行時に自動的にトリガーされるシェルコマンドやスクリプトを定義できる機能です。これにより、開発ワークフローにカスタムの自動化処理を組み込むことができます。

### 主な特徴

- **イベントドリブン**: 特定のツールが実行される前後にコマンドを実行
- **柔軟な設定**: `settings.local.json`でJSON形式で簡単に設定可能
- **セキュリティ**: 実行結果に基づいてツールの実行をブロック可能
- **カスタマイズ性**: 任意のシェルコマンドやスクリプトを実行可能
- **マッチャーベース**: ツール名のパターンマッチングで適用対象を指定

## Hooksの種類

Claude Code Hooksは以下の3種類のタイミングで実行されます：

### 1. PreToolUse（事前フック）
ツールが実行される**前**に実行されるフックです。以下のような用途に使用できます：

- 前提条件のチェック
- 環境の準備
- セキュリティスキャン（例：シークレットの検出）
- ログの記録

### 2. PostToolUse（事後フック）
ツールが実行された**後**に実行されるフックです。以下のような用途に使用できます：

- コード品質チェック（Linter、Formatter）
- テストの実行
- 結果の検証
- 追加の処理の実行

### 3. Stop（セッション終了時）
Claude Codeセッションが終了する際に実行されるフックです。以下のような用途に使用できます：

- プルリクエストの自動作成
- 作業内容のサマリー生成
- クリーンアップ処理
- 最終的な検証

## 設定方法

Hooksの設定は、`.claude/settings.local.json`ファイルで行います。以下は実際の設定例です：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash(*)",
        "hooks": [
          {
            "type": "command",
            "command": "detect-secrets scan --all-files --baseline .secrets.baseline"
          }
        ]
      }
    ],
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
```

### 設定の詳細

各フックは以下の構造を持ちます：

```json
{
  "matcher": "ツール名のパターン（正規表現やワイルドカード）",
  "hooks": [
    {
      "type": "command",
      "command": "実行するシェルコマンドまたはスクリプトパス"
    }
  ]
}
```

### Hookのブロック機能

PostToolUseフックでは、JSON形式で`{"decision":"block","reason":"理由"}`を出力することで、ツールの実行を事後的にブロックできます。以下は実際の例です：

```bash
#!/usr/bin/env bash
# ruff_gate_post.sh の例
set -euo pipefail

# ruffでPythonコードをチェック
R="$(python3 -m ruff check . 2>&1)" || status=$? || true

if [[ "${status:-0}" -ne 0 ]]; then
  # エラーがある場合、ブロックする
  jq -n --arg reason "$R" '{"decision":"block","reason":$reason}'
  exit 0  # exit 0でもdecision:blockが効く
fi

exit 0
```

## 実践的な使用例

### 1. Pythonコードの品質管理

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 -m ruff check . --fix"
          },
          {
            "type": "command",
            "command": "python3 -m black ."
          }
        ]
      }
    ]
  }
}
```

### 2. シークレット検出による情報漏洩防止

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash(git push*)",
        "hooks": [
          {
            "type": "command",
            "command": "detect-secrets scan --all-files"
          }
        ]
      }
    ]
  }
}
```

### 3. 自動テストの実行

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "pytest -xvs ${file_path}"
          }
        ]
      }
    ]
  }
}
```

### 4. 複雑なワークフローの自動化

```bash
#!/usr/bin/env bash
# .claude/scripts/comprehensive_check.sh

# 1. Lint チェック
echo "Running linter..."
ruff check . || { echo "Lint errors found"; exit 1; }

# 2. 型チェック
echo "Running type checker..."
mypy . || { echo "Type errors found"; exit 1; }

# 3. テスト実行
echo "Running tests..."
pytest || { echo "Tests failed"; exit 1; }

# 4. セキュリティチェック
echo "Checking for secrets..."
detect-secrets scan --baseline .secrets.baseline

echo "All checks passed!"
```

## マッチャーパターンの詳細

Hooksのマッチャーは柔軟なパターンマッチングをサポートします：

- `"*"`: すべてのツールにマッチ
- `"Bash(*)"`: Bashツールのすべての実行にマッチ
- `"Write|Edit|MultiEdit"`: 複数のツールにマッチ（OR条件）
- `"Bash(git push*)"`: 特定のコマンドパターンにマッチ
- `"Bash(python3:*)"`: コロンを含むパターンにマッチ

### パーミッションとの連携

`settings.local.json`では、Hooksと連携してパーミッション設定も可能です：

```json
{
  "permissions": {
    "allow": [
      "Bash(ruff*)",
      "Bash(black*)",
      "Bash(detect-secrets*)"
    ],
    "deny": [
      "Bash(rm -rf*)"
    ]
  }
}
```

## ベストプラクティス

### 1. パフォーマンスを考慮する

```bash
#!/usr/bin/env bash
# 高速化のための工夫
if ! command -v ruff &> /dev/null; then
  echo "Ruff not installed, skipping..."
  exit 0
fi

# キャッシュを活用
ruff check . --cache-dir=.ruff_cache
```

### 2. エラーハンドリングとブロック機能

```bash
#!/usr/bin/env bash
set -euo pipefail

# エラーをキャッチしてブロック
result=$(mypy . 2>&1) || status=$?

if [[ "${status:-0}" -ne 0 ]]; then
  # Claude Codeに修正を促す
  jq -n --arg reason "$result" \
    '{"decision":"block","reason":$reason}'
  exit 0
fi
```

### 3. 条件付き実行

```bash
#!/usr/bin/env bash
# ファイルタイプに応じた処理

case "${file_path##*.}" in
  py)
    python3 -m black "$file_path"
    python3 -m ruff check "$file_path" --fix
    ;;
  js|ts)
    prettier --write "$file_path"
    eslint --fix "$file_path"
    ;;
  *)
    echo "No formatter for this file type"
    ;;
esac
```

### 4. 統合されたワークフロー

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/scripts/format_and_lint.sh"
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
            "command": ".claude/scripts/final_checks.sh"
          }
        ]
      }
    ]
  }
}
```

## セキュリティ上の注意点

1. **信頼できるコマンドのみ実行**: 不明なコマンドや外部ソースからのコマンドは避ける
2. **パーミッション設定の活用**: `allow`と`deny`リストで実行可能なコマンドを制限
3. **スクリプトの検証**: Hookで実行するスクリプトは事前に十分にテスト
4. **シークレットの保護**: detect-secretsなどのツールを活用して情報漏洩を防止
5. **エラー出力の管理**: エラーメッセージに機密情報が含まれないよう注意

## トラブルシューティング

### Hookがブロックされる場合

Claude Codeがメッセージを表示する場合：
```
Hook execution blocked by ruff_gate_post.sh
```

対処法：
1. ブロックの理由を確認（通常はエラーメッセージに含まれる）
2. 指摘された問題を修正
3. 必要に応じてHookスクリプトを調整

### デバッグ方法

```bash
#!/usr/bin/env bash
# デバッグ情報を含むHookスクリプト
set -x  # コマンドをエコー表示
exec 2>&1  # stderrをstdoutにリダイレクト

echo "DEBUG: Starting hook execution"
echo "DEBUG: File path: ${file_path:-not set}"

# 実際の処理
result=$(your-command 2>&1) || status=$?
echo "DEBUG: Command exit status: ${status:-0}"
echo "DEBUG: Command output: $result"
```

### パフォーマンスの最適化

```bash
#!/usr/bin/env bash
# 並列実行による高速化
{
  ruff check . &
  mypy . &
  pytest -n auto &
} | cat

wait  # すべてのバックグラウンドジョブを待機
```

## 高度な活用例

### 1. 環境別の設定管理

```bash
#!/usr/bin/env bash
# .claude/scripts/environment_check.sh

# 環境に応じた設定の切り替え
if [[ -f ".env.development" ]]; then
  source .env.development
elif [[ -f ".env.production" ]]; then
  echo "WARNING: Production environment detected"
  jq -n '{"decision":"block","reason":"Production changes require manual review"}'
  exit 0
fi
```

### 2. 自動PR作成ワークフロー

```bash
#!/usr/bin/env bash
# .claude/scripts/git_pr_create.sh

# 変更があるかチェック
if [[ -z $(git status --porcelain) ]]; then
  echo "No changes to commit"
  exit 0
fi

# ブランチ作成とコミット
branch_name="claude-code-$(date +%Y%m%d-%H%M%S)"
git checkout -b "$branch_name"
git add -A
git commit -m "Claude Code: Automated changes

Co-authored-by: Claude <claude@anthropic.com>"

# PR作成（GitHub CLIを使用）
gh pr create \
  --title "Claude Code: Automated improvements" \
  --body "This PR contains automated changes made by Claude Code." \
  --base main
```

### 3. プロジェクト固有のルール適用

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/scripts/enforce_project_standards.sh"
          }
        ]
      }
    ]
  }
}
```

対応するスクリプト：
```bash
#!/usr/bin/env bash
# .claude/scripts/enforce_project_standards.sh

# プロジェクト固有のルールをチェック
errors=""

# 1. ファイル名の規約チェック
if [[ ! "$file_path" =~ ^[a-z0-9_/-]+\.[a-z]+$ ]]; then
  errors+="File naming convention violated\n"
fi

# 2. 必須ヘッダーのチェック
if [[ "${file_path##*.}" == "py" ]]; then
  if ! grep -q "^# Copyright" "$file_path"; then
    errors+="Missing copyright header\n"
  fi
fi

# エラーがあればブロック
if [[ -n "$errors" ]]; then
  jq -n --arg reason "$errors" '{"decision":"block","reason":$reason}'
fi
```

## まとめ

Claude Code Hooksは、開発ワークフローを大幅に効率化できる強力な機能です。適切に設定することで、以下のようなメリットが得られます：

- **自動化による生産性向上**: 繰り返し作業の削減とヒューマンエラーの防止
- **品質の向上**: 自動チェックによるコード品質の維持とエラーの早期発見
- **セキュリティの強化**: シークレット検出やパーミッション制御による安全性の確保
- **カスタマイズ性**: プロジェクト固有のニーズに応じた柔軟な設定
- **開発フローの最適化**: PreToolUse、PostToolUse、Stopの3つのタイミングでの制御

### 導入のステップ

1. `.claude/`ディレクトリを作成
2. `settings.local.json`でHooksを設定
3. 必要なスクリプトを`.claude/scripts/`に配置
4. パーミッション設定で安全性を確保
5. チームメンバーと設定を共有

### 今後の展望

Claude Code Hooksは、AIアシスタントと開発者の協働をより効果的にする重要な機能です。今後も機能の拡張や改善が期待され、より高度な自動化やインテグレーションが可能になるでしょう。

プロジェクトの要件に応じて適切なHooksを設定し、Claude Codeの能力を最大限に活用することで、より効率的で品質の高い開発を実現できます。

## 参考情報

- [Claude Code公式ドキュメント](https://docs.anthropic.com/claude-code)
- [Bashスクリプティングベストプラクティス](https://google.github.io/styleguide/shellguide.html)
- [jqコマンドリファレンス](https://stedolan.github.io/jq/manual/)

---

*この記事は、Claude Codeの実際の動作と設定ファイルの分析に基づいて作成されました。機能や設定方法は今後のアップデートで変更される可能性があります。*