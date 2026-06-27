# design-system — 進捗ボード
<!-- statusline / session-start / /board がこのファイルを読みます。自由に編集してOK。 -->

## 状態
進行中

## いま
tokens.css を単一の真実とする 127.0.0.1 ローカル専用デザインシステム。最新コミット (2026-06-16) で `tools/export_pptx.py` を追加し、tokens.css ベースの HTML スライドを html2pptx.app API 経由で PPTX 化する第2ルートを整備。HTTP サーバー (launchd `com.designsystem.server`) が port 4173 で常時稼働。直近では scout が自動収集した参照デザイン (全て inbox / auto) が `data/references.json` に溜まり、tokens.css への還元待ち。

## 次にやること
- [ ] inbox 参照のうち良質なものを `tools/promote_design.py <ref-id> --apply` で tokens.css へ還元 (聖域=追記のみ)
- [ ] `tools/export_pptx.py` を実スライドで一度通し検証し、本番デッキで動作確認
- [ ] launchd ジョブ (scout.daily / scout.weekly / promote.weekly) が意図通りスケジュール実行されているか `launchctl list` で確認 (要確認)
- [ ] README が未作成。起動方法・ツール群 (scout / promote / build_pptx / export_pptx / build_marp / deck_to_pdf) の入口を最低限ドキュメント化するか検討 (要確認)
- [ ] 未 push の `feat: html2pptx PPTX エクスポートツール追加` (f111b70) を push するか判断 (ローカル専用のため push 不要なら据え置き)

## 完了 (直近)
- [x] scout が自動収集した inbox 参照デザインを data/references.json に追記・コミット (2026-06-28)
- [x] html2pptx.app API 経由の PPTX エクスポートツール `tools/export_pptx.py` を追加 (2026-06-16)
- [x] 全ページ PDF 閲覧 (LibreOffice) + 還元レシピ採用 + スタイルガイド反映
- [x] 発展機能: Marp 出力 / 収集ソース追加 / 還元の選別統合
- [x] ローカル専用デザインツール化 (ライブラリ / 構成ジェネレーター / PPTX / 収集・還元自動化)
- [x] tokens.css に `--glass-highlight` edge-light (Apple Liquid Glass 寄せ) を追加
