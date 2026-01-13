# Notebook LM 統合ガイド

このドキュメントでは、既存のNotebook LMノートブックをシステムに統合する方法を説明します。

## 既存ノートブックの利用

### ローカルCLIでの使用（参考記事の方法）

既存の [notebooklm-skill](https://github.com/PleasePrompto/notebooklm-skill) を使用する場合：

```bash
# スキルのインストール（フォルダ名は notebooklm にする）
cd ~/.claude/skills
git clone https://github.com/PleasePrompto/notebooklm-skill notebooklm

# Claude Code CLI を起動
claude

# 利用可能なスキルを確認
What skills do i have?

# ノートブックをライブラリに追加
add this notebook to my library: https://notebooklm.google.com/notebook/YOUR-NOTEBOOK-ID

# ノートブックに質問
ask the notebook: "このドキュメントの主要なポイントは何ですか？"
```

### 例: 特定のノートブックとの統合

```bash
# 実際のノートブック例
add this notebook to my library: https://notebooklm.google.com/notebook/6c1ba7cc-2bea-4fc6-a4e1-884e59fa9c5f

# 質問例
ask the notebook: "このノートブックで扱っているトピックを要約してください"
```

## GitHub Actionsでの自動化

当リポジトリのシステムでは、GitHub Actionsを使用して自動化します。

### 方法1: Notebook IDを環境変数として設定

`.github/workflows/generate-report.yml` を編集：

```yaml
env:
  NOTEBOOKLM_NOTEBOOK_ID: "6c1ba7cc-2bea-4fc6-a4e1-884e59fa9c5f"
  NOTEBOOKLM_PROJECT_ID: ${{ secrets.NOTEBOOKLM_PROJECT_ID }}
  NOTEBOOKLM_LOCATION: ${{ secrets.NOTEBOOKLM_LOCATION || 'us-central1' }}
```

### 方法2: スクリプトでノートブックIDを指定

`notebooklm_reporter.py` を拡張してノートブックIDを受け取る：

```python
parser.add_argument(
    '--notebook-id',
    help='Existing Notebook LM notebook ID to use'
)
```

実行時：

```bash
python .claude/skills/scripts/notebooklm_reporter.py \
  --notebook-id "6c1ba7cc-2bea-4fc6-a4e1-884e59fa9c5f" \
  --source-dir ./sources \
  --format markdown
```

### 方法3: GitHub Secrets に保存

複数のノートブックを管理する場合：

```bash
# GitHub CLI を使用
gh secret set NOTEBOOKLM_NOTEBOOK_ID_PRODUCTION --body "6c1ba7cc-2bea-4fc6-a4e1-884e59fa9c5f"
gh secret set NOTEBOOKLM_NOTEBOOK_ID_STAGING --body "another-notebook-id"
```

ワークフローで使用：

```yaml
env:
  NOTEBOOK_ID: ${{ secrets.NOTEBOOKLM_NOTEBOOK_ID_PRODUCTION }}
```

## ノートブックURLからIDを抽出

Notebook LMのURLの構造：

```
https://notebooklm.google.com/notebook/{NOTEBOOK_ID}
```

例：
```
https://notebooklm.google.com/notebook/6c1ba7cc-2bea-4fc6-a4e1-884e59fa9c5f
                                       ↑
                                    Notebook ID
```

### Python での抽出方法

```python
import re
from urllib.parse import urlparse

def extract_notebook_id(url: str) -> str:
    """Extract Notebook ID from NotebookLM URL"""
    # パターン: /notebook/{id}
    pattern = r'/notebook/([a-f0-9-]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    raise ValueError(f"Invalid Notebook LM URL: {url}")

# 使用例
url = "https://notebooklm.google.com/notebook/6c1ba7cc-2bea-4fc6-a4e1-884e59fa9c5f"
notebook_id = extract_notebook_id(url)
print(f"Notebook ID: {notebook_id}")
```

## API経由でのノートブック取得

### Notebook LM Enterprise API

```python
import requests

def get_notebook(project_id: str, location: str, notebook_id: str, access_token: str):
    """Retrieve notebook details via API"""
    url = f"https://{location}-discoveryengine.googleapis.com/v1alpha/projects/{project_id}/locations/{location}/notebooks/{notebook_id}"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

# 使用例
notebook_data = get_notebook(
    project_id="your-project-id",
    location="us-central1",
    notebook_id="6c1ba7cc-2bea-4fc6-a4e1-884e59fa9c5f",
    access_token="your-access-token"
)

print(f"Notebook Name: {notebook_data.get('displayName')}")
print(f"Sources: {len(notebook_data.get('sources', []))}")
```

## 実践例：既存ノートブックからレポート生成

### ステップ1: ノートブックIDを設定

```bash
export NOTEBOOK_ID="6c1ba7cc-2bea-4fc6-a4e1-884e59fa9c5f"
```

### ステップ2: 拡張スクリプトの作成

`scripts/use_existing_notebook.py`:

```python
#!/usr/bin/env python3
"""
既存のNotebook LMノートブックを使用してレポート生成
"""
import os
import sys
import argparse
from notebooklm_reporter import NotebookLMReporter

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--notebook-id', required=True)
    parser.add_argument('--output-dir', default='./reports')
    parser.add_argument('--format', default='markdown')
    args = parser.parse_args()

    project_id = os.getenv('NOTEBOOKLM_PROJECT_ID')
    location = os.getenv('NOTEBOOKLM_LOCATION', 'us-central1')

    reporter = NotebookLMReporter(project_id, location)

    print(f"📚 Using existing notebook: {args.notebook_id}")

    # ノートブックから情報を取得
    # （実装はAPIエンドポイントに依存）

    # レポート生成
    report = reporter.generate_report(args.notebook_id, args.format)

    # 保存
    output_path = f"{args.output_dir}/report_from_notebook.{args.format}"
    with open(output_path, 'w') as f:
        f.write(report)

    print(f"✅ Report generated: {output_path}")

if __name__ == "__main__":
    sys.exit(main())
```

### ステップ3: GitHub Actionsで実行

```yaml
- name: Generate report from existing notebook
  run: |
    python scripts/use_existing_notebook.py \
      --notebook-id "${{ env.NOTEBOOK_ID }}" \
      --format markdown
```

## ハイブリッドアプローチ

ローカルでの対話的使用とGitHub Actionsでの自動化を組み合わせる：

1. **ローカル開発**: notebooklm-skill で対話的に分析
2. **本番自動化**: GitHub Actions で定期レポート生成
3. **ノートブック同期**: 同じNotebook IDを両方で使用

### 設定例

```bash
# ローカル: ~/.claude/skills/notebooklm にスキルをインストール
cd ~/.claude/skills
git clone https://github.com/PleasePrompto/notebooklm-skill notebooklm

# リポジトリ: GitHub Actionsの自動化を設定
cd /path/to/muchinochi-notebook-LM
# 既に設定済み

# 両方で同じノートブックIDを使用
NOTEBOOK_ID="6c1ba7cc-2bea-4fc6-a4e1-884e59fa9c5f"
```

## トラブルシューティング

### ノートブックが見つからない

```python
# ノートブック一覧を取得して確認
def list_notebooks(project_id: str, location: str, access_token: str):
    url = f"https://{location}-discoveryengine.googleapis.com/v1alpha/projects/{project_id}/locations/{location}/notebooks"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    return response.json()
```

### アクセス権限エラー

- Notebook LM Enterpriseの場合: サービスアカウントに適切な権限があるか確認
- 一般ユーザーの場合: ノートブックが公開設定になっているか確認

## 参考リンク

- [Qiita記事: Claude CodeでNotebookLMにアクセス](https://qiita.com/mamoru-ngy/items/a73607a1a0392b5d2c6c)
- [Notebook LM Enterprise API ドキュメント](https://cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/api-notebooks)
- [notebooklm-skill GitHub](https://github.com/PleasePrompto/notebooklm-skill)

---

**注**: このガイドは参考記事の方法と当リポジトリの自動化アプローチを統合したものです。
