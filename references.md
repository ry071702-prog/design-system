# デザイン・リファレンス台帳

世の中の優秀なデザインを継続的に取り込み、`tokens.css` / スタイルガイドへ還元するための台帳。
AIツール活用ナレッジ循環 (`/ai-scout` → `/ai-review`) のデザイン版。

## 循環フロー

1. **収集 (inbox)** — 良いデザインを見つけたら下の「収集候補」に1行追記
   （URL / スクショ / 「何が良いか」/ 抽出したい token・パターン）
2. **選別 (review)** — 定期的に候補を見直し、採用するものを決める
3. **還元 (promote)** — 採用したパターンを `tokens.css` か共通レシピ、各テーマへ反映。
   反映したら「採用済み」へ移動し、何を取り込んだか1行残す

## 抽出の観点（何を盗むか）

- **配色** — アクセントの選び方、コントラスト、ダーク時の沈み込み
- **タイポ** — フォント組み合わせ、スケール比、字間、見出しと本文の対比
- **余白とリズム** — 余白スケール、セクション間隔、行間
- **奥行き** — 影の重ね方、ガラス/ぼかし、境界線の扱い
- **モーション** — イージング、間（ま）、ホバー/入場の微妙な動き
- **レイアウト** — グリッド、ヒーロー構成、情報の階層化

---

## 収集候補 (inbox)

<!-- フォーマット: - [ ] [出典名](URL) — 何が良いか / 抽出したい token・パターン (YYYY-MM-DD) -->

- [x] [DAIICHI DIVE](https://daiichi-dive.ca-event.workers.dev/) — 深海テーマのダークUI。1アクセント・ガラスカード・環境アニメ(光線/泡)・グラデ見出し。→ この台帳と tokens.css の出発点 (2026-06-03)
- [ ] [Awwwards — Sites of the Day](https://www.awwwards.com/websites/sites_of_the_day/) — 良質ダーク/グラス事例の定常ソース。定期的に巡回して配色・ヒーロー構成・モーションの間を観察する巡回元として (2026-06-04)
- [x] [Glassmorphism 2.0 (weblogtrips)](https://weblogtrips.com/technology/glassmorphism-2-0-css-techniques-2026/) — 2026のガラス進化。単純 blur ではなく「光の相互作用」を出す**エッジライト/内側ハイライト**が要点。→ 採用済みへ (2026-06-04)

---

## 採用済み (promoted)

<!-- フォーマット: - [出典名] 取り込んだ内容 → 反映先 (YYYY-MM-DD) -->

- [DAIICHI DIVE] glassmorphism / 1アクセント / 環境アニメ / 極太見出し×字間広ラベルの対比 / prefers-reduced-motion 配慮 → tokens.css 全体・スタイルガイド (2026-06-03)
- [slack-emoji-agent 移行で発覚] グラデ上の文字が AA を割る問題 → `--accent-fg-shadow` (fg輝度に応じた逆方向シャドウ) を tokens.css に追加し `.ds-btn-accent` に適用 (2026-06-04)
- [スタイルガイド拡充] 余白とリズム/モーションが未掲載だった → Spacing・Radius・Motion(3イージング)のショーケースを Style Guide に追加。トークンから動的描画 (2026-06-04)
- [Glassmorphism 2.0 / Apple Liquid Glass] エッジライト → `--glass-highlight` (上端スペキュラ + 内側縁光、light/dark別) を追加し `.ds-glass` と topbar に合成。blur/saturate も微増。今後の Apple 寄せの第一歩 (2026-06-04)
