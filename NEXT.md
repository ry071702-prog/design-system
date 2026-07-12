# design-system — 進捗ボード
<!-- statusline / session-start / /board がこのファイルを読みます。自由に編集してOK。 -->

## 状態
進行中

## いま
tokens.css を単一の真実とする 127.0.0.1 ローカル専用デザインシステム。2026-07-12 に **scout inbox の還元 (promote) を一括適用** (106 → 278 トークン) し、続けて**還元の副作用だった重複レシピを名寄せ**した。tokens.css 末尾に「名寄せ (dedupe)」セクションを置き、同名レシピの正本を1本だけ定義する形にしてある。`.slide` ベースの**本番デッキ雛形** (`decks/template.html` + `decks/deck.css`) も用意し、export_pptx で pptx 化を実測確認済み。HTTP サーバー (launchd `com.designsystem.server`) は port 4173 で常時稼働。

## 次にやること
- [ ] 残 inbox 16 件 + 提案済 2 件　うち 2 件 (claudiu-angheloni / from-years-of-client-work) は additive_css が空で適用対象外
- [ ] index.html (スタイルガイド) に名寄せ後のレシピ (`.ds-section` / `.ds-section-divider` / `.ds-divider-label` / `.ds-texture-overlay`) の見本を足すと、使う前に確認できて便利
- [ ] デッキ雛形は 5 枚の型 (表紙 / アジェンダ / 3カラム / 数値 / まとめ) だけ　実案件で使いながら型を増やす

## 完了 (直近)
- [x] **重複レシピの名寄せ + トークンのエイリアス化** (2026-07-12)
      → `.ds-section` x5 → 1本 (計算値は据え置き　流体版は `.ds-section--fluid` にリネーム)
      → `.ds-section-divider` x5 → 役割で2系統に分離: 線のみ = `.ds-section-divider` (+ --medium/--accent/--soft/--wide/--ornament) / ラベル付き = 既存の `.ds-divider-label` (+ --plain) に統合
      → `.ds-texture-overlay` x3 → 1本 (背景色版と noise 画像版を統合) / `.ds-scroll-section` x2 → 1本
      → トークン: `--divider-thin|medium|thick` と `--divider-weight` を `--divider-width-*` のエイリアスに、`--section-gap` を `--section-gap-md` のエイリアスに (値は不変)　幅系は値が違う (780/800/860px) のでエイリアス化せず据え置き
      → 検証: 278 トークンの計算値が全て一致 (消失・変化ゼロ)・既存レシピの computed style も一致・4ページ 200・console エラー無し
- [x] **`promote_design.py` に重複チェックを追加** (2026-07-12)　追記予定の CSS が既存レシピ / 既存トークンとぶつかると `--apply` を中止する (`--allow-dup` で強行可)　@media 文脈は区別するのでレスポンシブ上書きは誤検知しない
- [x] **本番デッキ雛形 `decks/template.html` + `decks/deck.css`** (2026-07-12)　1600x900・5枚 (表紙/アジェンダ/3カラム/数値/まとめ)　テーマは class 付け替えだけ (studio / editorial / focus / dark)　export_pptx で 5 枚の編集可能 pptx を生成できることを実測確認
      → ハマり: html2pptx は「class 名に slide を含む要素」をスライドとして数える　子要素を `slide-*` にすると 5 枚が 44 枚と判定されて無料枠 (20枚/ジョブ) に当たる → デッキ用クラスは `deck-` prefix に統一
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
