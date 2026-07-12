# design-system — 進捗ボード
<!-- statusline / session-start / /board がこのファイルを読みます。自由に編集してOK。 -->

## 状態
進行中

## いま
tokens.css を単一の真実とする 127.0.0.1 ローカル専用デザインシステム。2026-07-12 に **scout inbox の還元 (promote) を一括適用**し、tokens.css は 496 行 (106 トークン) → 2518 行 (278 トークン) に拡大。ダークサーフェス/データ表示・コンテキストメニュー・コードブロック&diff・ドットグリッド・WebGL 奥行き・テクスチャ・セクション余白などのトークンとレシピが入った。既存トークンは 1 つも消えず値も不変 (ブラウザ実測で検証済み)。HTTP サーバー (launchd `com.designsystem.server`) は port 4173 で常時稼働。

## 次にやること
- [ ] **重複レシピの整理** (還元の副作用)　同名セレクタを複数の還元ブロックが定義しており、後勝ちで解決している
      → `.ds-section` x5 / `.ds-section-divider` x5 / `.ds-texture-overlay` x3 / `.ds-scroll-section` x2
      → 既存ページ (index/library/proposals/slides) はこれらを使っていないので実害は無いが、使う前に1本化する
- [ ] **似た役割のトークンの名寄せ**　`--section-gap*` / `--space-section` / `--space-narrative` / `--space-breath` が併存
      同様に幅系 (`--content-max-width` / `--content-width*` / `--section-content-max`) と区切り線系 (`--divider-width-*` / `--divider-thin|medium|thick` / `--divider-weight`) も乱立気味
- [ ] `.slide` ベースの**本番デッキ HTML が未整備**　tokens.css のテーマ/レシピを使ったデッキ雛形を1本作ると export_pptx が実運用に乗る
      (現状 `.slide` を持つ HTML は動作確認用の out/test-deck.html だけ)
- [ ] 残 inbox 16 件 + 提案済 2 件　うち 2 件 (claudiu-angheloni / from-years-of-client-work) は additive_css が空で適用対象外

## 完了 (直近)
- [x] **inbox 参照 25 件を tokens.css へ還元 (`promote_design.py --apply`)** (2026-07-12)
      → 新規トークン 172 個 (106 → 278)　追記のみで既存 496 行はバイト単位で不変
      → 重複トークンは1本化: `--section-gap` (6rem) / `--section-gap-sm,md,lg,xl` (4/6/8/12rem) / `--space-section` / `--space-12` / z-index スタック (base 0 → tooltip 60)
      → 検証: Chrome で既存 106 トークンの計算値が全て一致・既存レシピ (.ds-card 等) の computed style も一致・console エラー無し・export_pptx.py 通し実行 OK
- [x] README.md を作成 (起動 / ページ / 設定 / ツール群 / launchd / ディレクトリ構成) (2026-07-12)
- [x] launchd 3ジョブの稼働確認 — scout.daily (runs=18) / scout.weekly (月曜・digest) / promote.weekly (火曜・data/promotions 出力) いずれも last exit 0 で稼働中 (2026-07-12)
- [x] `tools/export_pptx.py` を通し検証 → 無料枠のレート制限 (status 3回/分) に対しポーリングが 2 秒間隔で 429 になるバグを修正　21 秒間隔 + 429 自動リトライにして 2 枚の pptx 生成に成功 (2026-07-12)
- [x] scout が自動収集した inbox 参照デザインを data/references.json に追記・コミット (2026-06-28)
- [x] html2pptx.app API 経由の PPTX エクスポートツール `tools/export_pptx.py` を追加 (2026-06-16)
- [x] 全ページ PDF 閲覧 (LibreOffice) + 還元レシピ採用 + スタイルガイド反映
- [x] 発展機能: Marp 出力 / 収集ソース追加 / 還元の選別統合
- [x] ローカル専用デザインツール化 (ライブラリ / 構成ジェネレーター / PPTX / 収集・還元自動化)
- [x] tokens.css に `--glass-highlight` edge-light (Apple Liquid Glass 寄せ) を追加
