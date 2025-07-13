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

## 免責事項

このプロジェクトは教育および研究目的で提供されています。以下の点にご注意ください：

- このソフトウェアは「現状のまま」提供され、明示的または暗示的な保証はありません
- 使用により生じたいかなる損害についても、開発者は責任を負いません
- 本番環境での使用は自己責任で行ってください
- セキュリティ設定やツールの動作を十分理解した上でご使用ください

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

Copyright (c) 2025 KATSU https://github.com/KATSU789

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
