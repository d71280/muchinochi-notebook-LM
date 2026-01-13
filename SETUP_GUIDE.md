# セットアップガイド - Notebook LM Report Automation

このガイドでは、Notebook LMレポート自動化システムのセットアップ手順を詳しく説明します。

## 📋 目次

1. [前提条件](#前提条件)
2. [Claude Code OAuth トークンの設定](#claude-code-oauth-トークンの設定)
3. [Notebook LM API の設定](#notebook-lm-api-の設定)
4. [GitHub Secrets の設定](#github-secrets-の設定)
5. [テスト実行](#テスト実行)
6. [トラブルシューティング](#トラブルシューティング)

## 前提条件

以下が必要です：

- ✅ GitHub アカウント
- ✅ Claude Code (Pro または Max プラン)
- ✅ Google Cloud Platform アカウント（Notebook LM Enterprise使用時）
- ✅ Git がインストールされたローカル環境

## Claude Code OAuth トークンの設定

### ステップ 1: Claude Code CLI のインストール

```bash
# macOS/Linux
curl -fsSL https://cdn.anthropic.com/install.sh | bash

# または Homebrew
brew install anthropics/claude/claude
```

### ステップ 2: Claude にログイン

```bash
claude login
```

ブラウザが開き、Anthropicアカウントでログインします。

### ステップ 3: GitHub App のインストール

```bash
cd /path/to/muchinochi-notebook-LM
claude /install-github-app
```

このコマンドを実行すると：
1. ブラウザでGitHub App インストールページが開きます
2. リポジトリへのアクセスを許可します
3. `CLAUDE_CODE_OAUTH_TOKEN` が自動的にリポジトリのSecretsに追加されます

### ステップ 4: 確認

GitHubリポジトリの設定で確認：

```
Settings > Secrets and variables > Actions
```

`CLAUDE_CODE_OAUTH_TOKEN` が存在することを確認してください。

## Notebook LM API の設定

### オプション A: Notebook LM Enterprise（推奨）

#### 1. Google Cloud Project の作成

```bash
# gcloud CLI のインストール
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# ログイン
gcloud auth login

# プロジェクトの作成
gcloud projects create YOUR-PROJECT-ID --name="Notebook LM Automation"

# プロジェクトの選択
gcloud config set project YOUR-PROJECT-ID
```

#### 2. Notebook LM Enterprise API の有効化

```bash
# Discovery Engine API（Notebook LMの基盤）を有効化
gcloud services enable discoveryengine.googleapis.com

# 必要に応じて課金を有効化
gcloud beta billing accounts list
gcloud beta billing projects link YOUR-PROJECT-ID --billing-account=BILLING_ACCOUNT_ID
```

#### 3. サービスアカウントの作成

```bash
# サービスアカウント作成
gcloud iam service-accounts create notebooklm-automation \
    --display-name="Notebook LM Automation Service Account"

# サービスアカウントのメールアドレスを取得
SERVICE_ACCOUNT_EMAIL=$(gcloud iam service-accounts list \
    --filter="displayName:'Notebook LM Automation Service Account'" \
    --format='value(email)')

# 必要な権限を付与
gcloud projects add-iam-policy-binding YOUR-PROJECT-ID \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/discoveryengine.admin"

# キーファイルのダウンロード
gcloud iam service-accounts keys create ~/notebooklm-key.json \
    --iam-account=${SERVICE_ACCOUNT_EMAIL}
```

#### 4. キーファイルの内容を取得

```bash
cat ~/notebooklm-key.json
```

このJSON全体を後でGitHub Secretsに設定します。

### オプション B: サードパーティAPI（Apify）

1. [Apify](https://apify.com/)でアカウントを作成
2. [NotebookLM API](https://apify.com/clearpath/notebooklm-api)のページでAPIキーを取得
3. APIキーをメモしておく

## GitHub Secrets の設定

### 1. GitHubリポジトリのSecretsページを開く

```
https://github.com/YOUR-USERNAME/muchinochi-notebook-LM/settings/secrets/actions
```

### 2. 以下のSecretsを追加

#### 必須（Claude Code用）
- **CLAUDE_CODE_OAUTH_TOKEN**: `/install-github-app` で自動設定済み

#### Notebook LM Enterprise を使用する場合

**NOTEBOOKLM_PROJECT_ID**
```
YOUR-PROJECT-ID
```

**NOTEBOOKLM_LOCATION**
```
us-central1
```

**GOOGLE_APPLICATION_CREDENTIALS_JSON**
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "notebooklm-automation@your-project-id.iam.gserviceaccount.com",
  ...
}
```

#### Apify APIを使用する場合

**NOTEBOOKLM_API_KEY**
```
your-apify-api-key-here
```

#### Google Chat通知を使用する場合（毎日の振り返り機能）

**GOOGLE_CHAT_WEBHOOK_URL**

1. Google Chatのスペースを開く
2. スペース名の横の「▼」をクリック
3. 「アプリとインテグレーションを管理」を選択
4. 「Webhook」を追加
5. Webhook名を入力（例: "Daily Reflection Bot"）
6. アバター画像を選択（任意）
7. 「保存」をクリックして Webhook URL を取得
8. URLをコピーして以下の形式でGitHub Secretsに追加：

```
https://chat.googleapis.com/v1/spaces/AAAA1234567/messages?key=AIzaSy...&token=abcd1234...
```

### 3. Secretsの確認

すべてのSecretsが正しく設定されていることを確認：

```
Settings > Secrets and variables > Actions > Repository secrets
```

## テスト実行

### 1. サンプルドキュメントの配置

```bash
# sourcesディレクトリの作成
mkdir -p sources

# サンプルドキュメントの作成
cat > sources/sample.md << 'EOF'
# サンプルドキュメント

これはテスト用のサンプルドキュメントです。

## 概要
Notebook LMレポート自動化システムのテストを行います。

## 詳細
このドキュメントはレポート生成のソースとして使用されます。
EOF
```

### 2. GitHub へのプッシュ

```bash
git add .
git commit -m "Add initial setup with sample document"
git push origin main
```

### 3. ワークフローの手動実行

1. GitHubリポジトリの「Actions」タブを開く
2. 「Generate Notebook LM Report」ワークフローを選択
3. 「Run workflow」をクリック
4. パラメータを入力（デフォルトでOK）
5. 「Run workflow」をクリックして実行

### 4. 実行結果の確認

- ワークフローが正常に完了することを確認
- Artifacts セクションで生成されたレポートをダウンロード
- `reports/` ディレクトリにレポートファイルが作成されていることを確認

### 5. ローカルでのテスト

```bash
# Python環境のセットアップ
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install requests google-auth google-auth-oauthlib

# 環境変数の設定
export NOTEBOOKLM_PROJECT_ID="YOUR-PROJECT-ID"
export NOTEBOOKLM_LOCATION="us-central1"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/notebooklm-key.json"

# スクリプトの実行
python .claude/skills/scripts/notebooklm_reporter.py \
  --source-dir ./sources \
  --output-dir ./reports \
  --format markdown
```

## トラブルシューティング

### 問題: `CLAUDE_CODE_OAUTH_TOKEN` が見つからない

**解決策:**
```bash
# GitHub Appを再インストール
claude /install-github-app

# または手動でトークンを作成
# https://github.com/settings/tokens から
```

### 問題: Google Cloud 認証エラー

**解決策:**
```bash
# ローカルで認証テスト
gcloud auth application-default login

# サービスアカウントキーの確認
cat ~/notebooklm-key.json | jq .

# 権限の再確認
gcloud projects get-iam-policy YOUR-PROJECT-ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:*notebooklm*"
```

### 問題: ワークフローが失敗する

**解決策:**
1. Actions のログを詳しく確認
2. Secrets が正しく設定されているか確認
3. `.github/workflows/generate-report.yml` の構文を確認
4. Claude Code Actionのバージョンが最新か確認

```yaml
uses: anthropics/claude-code-action@v1  # 最新版を使用
```

### 問題: Skillが認識されない

**解決策:**
1. `.claude/skills/` ディレクトリが存在するか確認
2. スキルファイルが正しい場所にあるか確認
```bash
ls -la .claude/skills/
```
3. ワークフローの `claude_args` に `"Skill"` が含まれているか確認

### 問題: レポートが生成されない

**解決策:**
1. `sources/` ディレクトリにファイルが存在するか確認
2. サポートされているファイル形式か確認（.txt, .md, .pdf, .docx）
3. Python依存関係がインストールされているか確認

### 問題: Google Chat に通知が届かない

**解決策:**
1. Webhook URLが正しく設定されているか確認
```bash
# GitHub Secretsで確認
# Settings → Secrets and variables → Actions
```
2. ローカルでWebhookをテスト
```bash
curl -X POST \
  -H 'Content-Type: application/json' \
  -d '{"text": "テストメッセージ"}' \
  "YOUR-WEBHOOK-URL"
```
3. Webhook URLの有効期限を確認（再生成が必要な場合がある）
4. Google Chatのスペースで「アプリとインテグレーション」からWebhookが有効か確認
5. ワークフローログで curl コマンドの実行結果を確認

### 問題: 毎日の振り返りが実行されない

**解決策:**
1. GitHub Actions が有効になっているか確認（Settings → Actions → General）
2. cron スケジュールが正しいか確認（UTC 21:00 = JST 翌朝6:00）
3. リポジトリがprivateの場合、GitHub Actionsの実行時間制限を確認
4. 手動実行でテスト：
```
Actions → Daily Reflection with Notebook LM → Run workflow
```

## 🔧 高度な設定

### カスタムトリガーの追加

特定のラベルが付いたIssueでレポート生成：

```yaml
on:
  issues:
    types: [labeled]

jobs:
  generate-report:
    if: github.event.label.name == 'generate-report'
    # ... 既存の設定
```

### 複数の出力形式

すべての形式でレポートを生成：

```bash
for format in markdown json html; do
  python .claude/skills/scripts/notebooklm_reporter.py \
    --format $format
done
```

### Slackへの通知

ワークフロー完了時にSlackに通知：

```yaml
- name: Notify Slack
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
    payload: |
      {
        "text": "Notebook LM Report Generated: ${{ steps.claude-report.outputs.result }}"
      }
```

## 📚 次のステップ

セットアップが完了したら：

1. 実際のドキュメントを `sources/` に追加
2. 定期実行のスケジュールを調整
3. レポートフォーマットをカスタマイズ
4. 他のワークフローと統合

## 💡 ベストプラクティス

- ✅ 定期的にAPIキーをローテーション
- ✅ レポート出力を定期的にレビュー
- ✅ ソースドキュメントのバージョン管理
- ✅ エラー通知の設定
- ✅ コスト監視の設定（Google Cloud）

---

問題が解決しない場合は、[Issues](https://github.com/d71280/muchinochi-notebook-LM/issues)でサポートを受けてください。
