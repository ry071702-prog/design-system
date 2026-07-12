# design-system — 進捗ボード
<!-- statusline / session-start / /board がこのファイルを読みます。自由に編集してOK。 -->

## 状態
進行中

## いま
tokens.css を単一の真実とする 127.0.0.1 ローカル専用デザインシステム。最新コミット (2026-06-16) で `tools/export_pptx.py` を追加し、tokens.css ベースの HTML スライドを html2pptx.app API 経由で PPTX 化する第2ルートを整備。HTTP サーバー (launchd `com.designsystem.server`) が port 4173 で常時稼働。直近では scout が自動収集した参照デザイン (全て inbox / auto) が `data/references.json` に溜まり、tokens.css への還元待ち。

## 次にやること
- [ ] inbox 参照のうち良質なものを `tools/promote_design.py <ref-id> --apply` で tokens.css へ還元 (聖域=追記のみ)
      → 適用可能な候補が **25 件** 溜まっている (提案 json + additive_css あり)　`python3 tools/promote_design.py --list` で一覧
      → キュレーターの risk は 36 件すべて low で判別に使えない　どれを採るかは人が中身を見て決める
- [ ] `.slide` ベースの**本番デッキ HTML が未整備**　tokens.css のテーマ/レシピを使ったデッキ雛形を1本作ると export_pptx が実運用に乗る
      (現状 `.slide` を持つ HTML は動作確認用の out/test-deck.html だけ)

## 完了 (直近)
- [x] README.md を作成 (起動 / ページ / 設定 / ツール群 / launchd / ディレクトリ構成) (2026-07-12)
- [x] launchd 3ジョブの稼働確認 — scout.daily (runs=18) / scout.weekly (月曜・digest) / promote.weekly (火曜・data/promotions 出力) いずれも last exit 0 で稼働中 (2026-07-12)
- [x] `tools/export_pptx.py` を通し検証 → 無料枠のレート制限 (status 3回/分) に対しポーリングが 2 秒間隔で 429 になるバグを修正　21 秒間隔 + 429 自動リトライにして 2 枚の pptx 生成に成功 (2026-07-12)
- [x] scout が自動収集した inbox 参照デザインを data/references.json に追記・コミット (2026-06-28)
- [x] html2pptx.app API 経由の PPTX エクスポートツール `tools/export_pptx.py` を追加 (2026-06-16)
- [x] 全ページ PDF 閲覧 (LibreOffice) + 還元レシピ採用 + スタイルガイド反映
- [x] 発展機能: Marp 出力 / 収集ソース追加 / 還元の選別統合
- [x] ローカル専用デザインツール化 (ライブラリ / 構成ジェネレーター / PPTX / 収集・還元自動化)
- [x] tokens.css に `--glass-highlight` edge-light (Apple Liquid Glass 寄せ) を追加
