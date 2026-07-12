# 共通デザインシステム

`tokens.css` を単一の真実 (single source of truth) とする、**127.0.0.1 ローカル専用**のデザインシステム
純粋な CSS カスタムプロパティなので、Tailwind のバージョン差やビルド構成に依存せず、どのプロジェクトからでも使える

やることは大きく3つ

1. **配る** — `tokens.css` をトークン/テーマ/レシピの正本として各プロジェクトへ
2. **集める** — 世の中のデザインを RSS + Dify で自動収集し `data/references.json` の inbox に貯める (scout)
3. **還元する** — inbox の良いパターンを `tokens.css` への**追記専用**トークン提案に変換し、人がレビューして適用する (promote)

`tokens.css` は聖域なので、自動適用は行わない　`--apply` は既存値を壊さない追記だけを行い、既存値の変更提案は人が手動で判断する

---

## 起動

HTTP サーバーは launchd (`com.designsystem.server`) でログイン時から常駐している　ブラウザで開くだけでよい

```
open http://127.0.0.1:4173/
```

手動で立てる場合 (launchd を使わないとき)

```
cd ~/design-system
python3 -m http.server 4173 --bind 127.0.0.1
```

`--bind 127.0.0.1` は必須　LAN には公開しない

### ページ

| URL | ファイル | 中身 |
|---|---|---|
| `/index.html` | `index.html` | スタイルガイド　`tokens.css` のトークン・テーマ・レシピの一覧 |
| `/library.html` | `library.html` | デザインライブラリ　収集した参照デザイン (inbox / promoted) の閲覧・選別 |
| `/proposals.html` | `proposals.html` | 骨子ジェネレーター　Dify「スライド構成ジェネレーター」を呼んでスライド構成を作る |
| `/slides.html` | `slides.html` | 作成済みスライド一覧　`data/slides.json` のサムネから全ページ PDF を開ける |

`app.css` / `app.js` は全ページ共通シェル　背景・topbar・テーマ切替 (studio / editorial / focus) と明暗 (light / dark) を注入し、選択を localStorage に永続化する

---

## セットアップ

```
cp config.example.json config.local.json
# config.local.json に各キーを記入する (gitignore 済み・commit されない)
```

`config.local.json` のキー

| キー | 使うツール |
|---|---|
| `difyBaseUrl` | Dify を呼ぶ全ツール共通のベース URL |
| `difyAppKey` | `proposals.html` / `build_pptx.py` / `build_marp.py` (スライド構成ジェネレーター) |
| `difyScoutAppKey` | `scout_designs.py` (デザイン収集スカウト) |
| `difyPromoteAppKey` | `promote_design.py` (デザイン還元キュレーター) |
| `pptxTemplate` | `build_pptx.py` のベースにする公式テンプレ pptx のパス |
| `html2pptxApiKey` | `export_pptx.py` (html2pptx.app の API キー) |
| `scoutSources` | 任意　scout の収集元 RSS 配列 (未指定なら minimal.gallery / Codrops / One Page Love) |
| `slidesRoots` | 任意　`index_slides.py` の走査ルート配列 (未指定なら `~/Downloads`) |

### 外部依存

| 依存 | 必要なツール |
|---|---|
| Dify (`flows/*.yml` の 3 ワークフローをインポートしておく) | scout / promote / 構成ジェネレーター |
| python-pptx | `build_pptx.py` / `index_slides.py` |
| LibreOffice (`/Applications/LibreOffice.app`) | `deck_to_pdf.py` |
| marp-cli (`npx @marp-team/marp-cli`) | `build_marp.py` のレンダリング |
| html2pptx.app のアカウント | `export_pptx.py` |
| macOS の `qlmanage` | `index_slides.py` のサムネ生成 |

---

## ツール

すべて `python3 tools/<name>.py` で実行する (リポジトリルートから)

### 収集・還元

**`scout_designs.py`** — デザイン系 RSS を取得 → Dify「デザイン収集スカウト」で観点・抽出トークン・タグを付与 → microlink でスクリーンショット URL を取得 → `data/references.json` の inbox に URL 重複排除つきで追記

```
python3 tools/scout_designs.py                 # 既定ソースから収集 (既定 6 件)
python3 tools/scout_designs.py --limit 4 --dry-run
python3 tools/scout_designs.py --no-shot       # スクショ取得をスキップ
python3 tools/scout_designs.py --digest        # 直近7日の未選別を Obsidian Inbox に要約
```

**`promote_design.py`** — inbox の参照を Dify「デザイン還元キュレーター」に渡し、`tokens.css` に整合する**追記専用**の提案を `data/promotions/<id>.md` (レビュー用) と `<id>.json` (適用用) に書き出す　`--apply` はレビュー済みの json をそのまま `tokens.css` に追記し、`references.md` に採用ログを1行残す

```
python3 tools/promote_design.py --list         # ref 一覧と状態 (inbox / 提案済 / 還元)
python3 tools/promote_design.py <ref-id>       # 1件の還元案を生成 (提案のみ・tokens.css は触らない)
python3 tools/promote_design.py <ref-id> --apply   # 提案を tokens.css へ追記
python3 tools/promote_design.py --weekly       # 直近7日の inbox をまとめて提案 (適用しない)
```

適用後の差分は `git diff tokens.css` で確認・取り消しできる

### スライド生成

PPTX には 2 ルートある

**`build_pptx.py`** — 公式テンプレ pptx を開き、作例スライド (表紙 / AGENDA / 本文) を複製して文字を差し替え、元のガイドラインスライドを削除して保存する　テーマ色・フォント・ロゴ・レイアウトをそのまま継承できる

```
python3 tools/build_pptx.py --topic "社内ナレッジ検索へのRAG導入" \
    --theme editorial --audience 経営層 --goal 予算承認 --open
python3 tools/build_pptx.py --from out/structure.md --open   # Dify を呼ばない
```

**`export_pptx.py`** — `tokens.css` ベースの HTML スライドを html2pptx.app の REST API で編集可能な pptx にする第2ルート

```
python3 tools/export_pptx.py --html out/deck.html --css tokens.css --name 提案資料.pptx --open
```

HTML 規約　1 スライド = `.slide` クラスを持つ要素1つ　幅・高さを px で明示する (`<section class="slide" style="width:1600px;height:900px">`)　script / iframe / form / a は除去される　画像は絶対 URL か base64 データ URI のみ

無料枠の制限　100 件/日・**status 3 リクエスト/分**・50 スライド/ジョブ・ペイロード 1MB
ポーリング間隔はこの 3 req/min に合わせて 21 秒にしてある　429 が返った場合はサーバー指定の待ち時間だけ空けて自動リトライする

**`build_marp.py`** — スライド構成を Marp 形式 (Markdown + テーマ CSS) にする軽量・共有用ルート　`out/` に `.md` と `ds.css` を生成し、レンダリングのコマンドを表示する (レンダリング自体は marp-cli で手動実行)

```
python3 tools/build_marp.py --from out/structure.md --theme editorial
python3 tools/build_marp.py --topic "新規事業の提案" --theme studio --count 8
```

### スライド索引

**`index_slides.py`** — 作成済みの pptx / key を走査して `slides.html` 用の索引 `data/slides.json` とサムネイル (`data/slide-thumbs/`) を生成する

```
python3 tools/index_slides.py             # 既定で ~/Downloads を走査
python3 tools/index_slides.py ~/Desktop   # 走査ルートを指定 (複数可)
```

**`deck_to_pdf.py`** — pptx を全ページ PDF に変換する (LibreOffice headless)　`slides.html` の「全ページ」ボタンから呼ばれる　PDF は `data/slide-pdfs/<id>.pdf` にキャッシュされる

```
python3 tools/deck_to_pdf.py <slides.json の id> --open
python3 tools/deck_to_pdf.py --path "/path/deck.pptx" --open
```

---

## 自動化 (launchd)

plist の原本は `tools/launchd/` にある　有効化は `~/Library/LaunchAgents/` にコピーして `launchctl load` する

```
cp tools/launchd/com.designsystem.scout.daily.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.designsystem.scout.daily.plist
launchctl list | grep designsystem          # 状態確認
```

| ラベル | スケジュール | 中身 | ログ |
|---|---|---|---|
| `com.designsystem.server` | ログイン時 (`RunAtLoad` + `KeepAlive`) | `http.server 4173 --bind 127.0.0.1` | `/tmp/ds-server.log` |
| `com.designsystem.scout.daily` | 毎日 9:30 | `scout_designs.py --limit 6` | `/tmp/ds-scout.log` |
| `com.designsystem.scout.weekly` | 毎週月 9:40 | `scout_designs.py --digest` → Obsidian Inbox | `/tmp/ds-scout.log` |
| `com.designsystem.promote.weekly` | 毎週火 9:45 | `promote_design.py --weekly` → `data/promotions/` | `/tmp/ds-promote.log` |

promote は**提案を書き出すところまで**が自動　`tokens.css` への適用は人が `--apply` で行う

`/tmp` のログは macOS の定期クリーンアップで数日で消えることがある　ログが無いことは実行されていないことを意味しない　実際に走ったかは `launchctl print gui/$(id -u)/<ラベル>` の `runs` / `last exit code` で見る

---

## ディレクトリ構成

```
design-system/
├── tokens.css          # 単一の真実　トークン / ダークモード / テーマ / ds- レシピ / モーション
├── app.css, app.js     # 全ページ共通シェル (背景・topbar・テーマ切替の永続化)
├── index.html          # スタイルガイド
├── library.html        # デザインライブラリ (収集した参照の選別)
├── proposals.html      # 骨子ジェネレーター
├── slides.html         # 作成済みスライド一覧
├── references.md       # 参照デザインと採用ログ (人が読む正本)
├── config.example.json # 設定のひな形　config.local.json にコピーして使う
├── data/
│   ├── references.json # 収集した参照デザイン (status: inbox / promoted)
│   ├── promotions/     # 還元レビューキュー (gitignore)
│   ├── slides.json     # スライド索引 (gitignore)
│   ├── slide-thumbs/   # サムネ (gitignore)
│   └── slide-pdfs/     # 全ページ PDF キャッシュ (gitignore)
├── flows/              # Dify ワークフロー DSL
│   ├── design-scout.yml       # デザイン収集スカウト
│   ├── design-promote.yml     # デザイン還元キュレーター
│   └── proposal-skeleton.yml  # スライド構成ジェネレーター
├── tools/              # CLI ツール群
│   └── launchd/        # plist 原本 (server / scout.daily / scout.weekly / promote.weekly)
└── out/                # 生成物 (gitignore)
```

`config.local.json` と `out/` と `data/` の生成物は gitignore 済み　API キーや社内ファイルのパスは commit されない

---

## tokens.css の構成

| セクション | 中身 |
|---|---|
| ベーストークン | 色 / タイポ / 余白 / 角丸 / 影 / モーション |
| ダークモード | `<html data-theme="dark">` または `<html class="dark">` の両対応 |
| アクセント・テーマ | `theme-studio` / `theme-editorial` / `theme-focus`　構造は共通で色相だけ差し替える |
| コンポーネント・レシピ | `ds-` prefix の任意クラス　Tailwind と併用可 |
| モーション・ユーティリティ | `prefers-reduced-motion` を必ず尊重する |
| 還元 (promoted) ブロック | `promote_design.py --apply` が追記する　出典 URL と日付つき |
