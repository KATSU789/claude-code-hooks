# AI-TEST Project

## セットアップ

### Claude Code 最小セットアップ

`setup_claude_minimal.py` を使用してClaude Code環境を自動セットアップできます。

```bash
python3 setup_claude_minimal.py
```

#### 機能

- **自動環境構築**: `.claude`ディレクトリと必要なスクリプトを自動作成
- **依存関係チェック**: 必要なパッケージとツールの存在確認・インストール
- **設定ファイル生成**: セキュリティ設定を含む`settings.local.json`を自動作成

#### 作成されるファイル

- `.claude/scripts/git_pr_create.sh` - 自動PR作成スクリプト
- `.claude/scripts/ruff_gate_post.sh` - Pythonコードチェックスクリプト  
- `.claude/settings.local.json` - Claude Code設定ファイル

#### 必要なツール

**Pythonパッケージ:**
- `ruff` - Pythonコードリンター

**システムツール:**
- `gh` - GitHub CLI（PR作成に必要）
- `jq` - JSONプロセッサ（スクリプト内で使用）

#### セキュリティ設定

危険なコマンドの実行を防ぐため、以下が自動的に禁止されます：
- システムファイルの削除（`rm -rf /`等）
- パイプ経由でのスクリプト実行（`curl | bash`等）
- システム管理コマンド（`sudo`, `shutdown`等）

#### 自動化機能

- **PostToolUse Hook**: ファイル編集時にruffでPythonコードをチェック
- **Stop Hook**: 会話終了時に変更があれば自動でPR作成
  - ブランチ名形式: `claude-auto-YYYYMMDD-HHMMSS` (例: `claude-auto-20250713-143045`)
