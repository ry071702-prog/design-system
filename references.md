# デザイン・リファレンス台帳

世の中の優秀なデザインを継続的に取り込み、`tokens.css` / スタイルガイドへ還元するための台帳。
AIツール活用ナレッジ循環 (`/ai-scout` → `/ai-review`) のデザイン版。

> **描画ソースは `data/references.json`** — ライブラリ画面 (`library.html`) はこの JSON を読んで表示する。
> 新規エントリは `library.html` の追加フォームで JSON 雛形を生成 → `data/references.json` に貼る。
> このファイルは「循環フロー/抽出観点/物語メモ」を残す台帳として併用する。

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

- [Creating a Thumbnail Flow Animation with GSAP MotionPath] GSAPモーションパス参考 → --ease-path / --stack-offset-x・y / --stack-scale-active・rest / --z-stack-step・base / --dur-stagger / --transition-overlap を :root に追記（tokens.css モーションセクション末尾） (2026-06-08)

- [自動収集の選別統合] PP Neue Montreal/Convicts/Twoo/Project Simply → フォントウェイトscale(--weight-*) / 特大型(--text-6xl・7xl) / 大型余白(--space-10・11) / --tracking-tighter を :root に追記。重複・競合・既存再定義の提案は不採用 (2026-06-09)

- [自動収集レシピ統合] Twoo/108 Supply/Kosbiotic/Beaucoup/Forging → .ds-hero(-title)/.ds-product-card(+grid)/.ds-article-body/.ds-lead/.ds-pull-quote と --ease-lift/--measure/--card-lift-y を追記。重複は1本化 (2026-06-09)

- [Anatoly Ivanov] Anatoly Ivanov (minimal portfolio) → --tracking-display / --scrim-opacity / --grid-asym-* / --lift-subtle / .ds-nameplate / .ds-asymmetric-grid / .ds-gallery-card を tokens.css に追記 (2026-06-09) (2026-07-12)

- [Blank Inside] Blank Inside (minimal.gallery EC) → .ds-section-spacious / .ds-product-grid-editorial / .ds-btn-ghost / .ds-divider-label を追記（大余白・ゴーストCTA・ラベル区切り） (2026-07-12)

- [Cantor8] Cantor8 (Web3 minimal gallery) → ダークサーフェス/グロー/データラベルタイポ/タイトグリッドトークン + .ds-data-label / .ds-data-grid / .ds-data-cell / .ds-data-row / .ds-badge-glow-* レシピを :root および共通レシピ末尾に追記 — 2026-06-09 (2026-07-12)

- [Designing Beyond the Surface: How DashDigital Turns Complexity into Clarity] DashDigital エディトリアル記事レイアウト → --content-max-width / --section-gap / --section-inner-gap トークン追加 + .ds-article-container / .ds-section-divider / .ds-article-heading / .ds-article-subheading レシピ追記 (tokens.css :root 末尾) (2026-07-12)

- [DreamHouse Productions] DreamHouse Productions → .ds-display-title(text-6xl×weight-black×tracking-tighter)・.ds-section / .ds-section--wide(space-10/space-11ラッパー)・.theme-editorial .ds-kicker--mono を追記 (2026-07-12)

- [Engineering the Web Experience Behind Shopify’s Spring ’26 Edition: Everywhere] Shopify Edition WebGL事例 → z-indexレイヤースタック(--z-canvas/content/overlay等6段階)・スクロール駆動イージング(--ease-scroll-in/out)・ローディングトークン(--progress-track-h等)を:rootに追記 — tokens.css (2026-07-12)

- [Exploring 3D Image Rotations on Scroll] Exploring 3D Image Rotations on Scroll → --perspective-near/mid/far・--rotation-max-x/y・--transform-origin-3d・--ease-scroll-3d トークン追加 + .ds-scroll-3d-stage / .ds-scroll-3d / .ds-scroll-3d.is-resting レシピ追記 (tokens.css :root + モーション・ユーティリティセクション) (2026-07-12)

- [Gusta] Gusta (minimal branding agency) → --space-section / --bg-hover / --grid-gutter トークン追加、.ds-gallery-grid / .ds-hover-minimal / .ds-section / .ds-brand-label レシピ追記 (tokens.css :root + コンポーネント・レシピ節) (2026-07-12)

- [Longbow] Longbow (automotive/dark/editorial) → --contrast-dark-bg/fg, --tracking-wider, --space-9-5, .ds-accent-rule, .ds-dark-section を追記 (tokens.css :root + レシピ拡張) — 2026-06-09 (2026-07-12)

- [Off Mute] Off Mute (podcast/editorial) → --fg-meta / --episode-row-gap / --episode-num-width / --episode-row-min-height / --player-track-height / --player-track-radius / --section-divider-margin + .ds-episode-list / .ds-episode-item / .ds-section-divider / .ds-player-track を tokens.css に追記 (2026-07-12)

- [Podium: Building a Website Where Running Becomes Storytelling] Podium (Scroll Narrative) → --ease-narrative / --ease-scene / --dur-cinematic / --space-narrative / --space-breath / --webgl-blend / --webgl-opacity / --parallax-factor / --dur-line-stagger / --scene-scale-from / --overlay-grad-dark / .ds-narrative-section / .ds-webgl-overlay / .ds-narrative-overlay / .ds-narrative-content / .ds-animate-narrative を :root およびコンポーネントレシピとして追記 (2026-07-12)

- [Sculpting a Digital Athlete: Capturing Stefanos Tsitsipas Beyond the Court] Sculpting a Digital Athlete (Tsitsipas/Blender×WebGL) → ライティングトークン(--light-key/fill/rim)・シェーダー風シャドウ(--shadow-contact/ambient)・WebGL z-index体系(--z-canvas〜overlay)・3Dモーション値(--ease-orbit/emerge, --dur-scene/reveal)・テクスチャ品質スケール・.ds-webgl-hero/.ds-depth-layer/.ds-rim-light/.ds-scene-reveal を :root およびコンポーネントレシピに追記 (2026-07-12)

- [Shaping Stories into Experience: The Work of Kevin Lam] Kevin Lam ポートフォリオ記事 → .ds-byline / .ds-section-divider / .ds-spotlight の 3 レシピを追記（theme-editorial 向け記事レイアウト拡張） (2026-07-12)

- [Testing What Users Actually See with Vitest and Chromatic] Vitest/Chromatic UI観察 → diff強調色ペア(--diff-add-*/--diff-del-*)・コードブロックトークン(--code-bg/fg/border/line-height)・比較レイアウト間隔(--compare-gap)・.ds-code-block/.ds-diff/.ds-compare/.ds-badge-neutralレシピを:rootおよびコンポーネント定義に追記 (2026-07-12)

- [The Print Loft] The Print Loft → --product-aspect-print / --product-grid-gap / --product-col-min / .ds-product-grid-print / .ds-product-card--print 変種を追記 (tokens.css :root + レシピ拡張) (2026-07-12)

- [Website Inspiration: 101 GenAI] Website Inspiration: 101 GenAI → --shadow-glow-strong / --section-gap / --section-content-max / .ds-section-ps / .ds-glow-card を追記（ロングスクロール余白リズム・AIグロー演出の補完） (2026-07-12)

- [Website Inspiration: AlterG Resources] AlterG Resources → グリッドガター(--grid-col-gap/--grid-row-gap)・流動セクション余白(--section-padding-y)・パララックスオフセット4段階(--parallax-offset-sm〜xl)・環境オーバーレイ不透明度3段階(--overlay-subtle/mid/strong) を :root に追記 (2026-07-12)

- [Website Inspiration: Billow] Billow(クラウドSaaS): ソフトグラデーション変数(--cloud-grad-light/dark/--cloud-grad)・セクションリズムエイリアス(--section-gap)・角丸拡張(--radius-2xl)・レシピ(.ds-cloud-section/.ds-soft-card) → :root および コンポーネント・レシピ節に追記 (2026-07-12)

- [Website Inspiration: Kevin] Website Inspiration: Kevin → ドットグリッド背景トークン(--dot-size/gap/color/opacity) + .ds-dot-grid レシピ + --section-gap-sm/md/lg + .ds-section ユーティリティ + .ds-reveal アニメーション を :root / [data-theme="dark"] / レシピ層に追記 (2026-07-12)

- [Website Inspiration: Lovably] Website Inspiration: Lovably → セクション縦余白トークン(--section-gap / --content-width系)・.ds-section / .ds-content / .ds-divider-minimal レシピを :root およびコンポーネント・レシピ末尾に追記 (2026-07-12)

- [Website Inspiration: Monolog] Website Inspiration: Monolog → テクスチャオーバーレイ不透明度トークン(--texture-opacity-*)・長尺スクロール余白(--space-12, --divider-spacing)・セクション区切りレシピ(.ds-section-divider / .ds-scroll-section / .ds-texture-overlay)を :root および theme-editorial に追記 (2026-07-12)

- [Website Inspiration: Neuropelvic Surgery] Website Inspiration: Neuropelvic Surgery → section-spacing-scale (--section-gap-sm/md/lg/xl, .ds-section レシピ), leading-prose (1.85), weight-heading-primary/secondary/tertiary を :root および共通レシピに追記 — 2026-06-09 (2026-07-12)

- [Website Inspiration: Rectangles.fm] Rectangles.fm → テクスチャオーバーレイ変数(--texture-opacity / --texture-url)・ポッドキャストカバー比率(--aspect-podcast-cover 他)・スクロールセクション余白(--space-section / --divider-weight / --divider-color)・.ds-texture-overlay / .ds-scroll-section / .ds-scroll-divider / .ds-podcast-grid / .ds-podcast-cover を tokens.css に追記 (2026-07-12)

- [Website Inspiration: Right-Click Logo] Right-Click Logo → コンテキストメニュートークン (--menu-min-w / --dur-menu / --logo-hover-scale 等) + .ds-context-menu / .ds-logo-interactive レシピを追記 (2026-07-12)

- [Website Inspiration: Secret Garden Stresa] Secret Garden Stresa → --space-12 / --earth-* パレット / .ds-section-divider / .ds-lang-switcher を tokens.css に追記 (2026-06-09) (2026-07-12)
