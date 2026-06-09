#!/usr/bin/env python3
"""
build_marp.py — スライド構成を Marp 形式(Markdown + テーマCSS)に変換する。
デザインシステムのテーマ(studio/editorial/focus)を反映した HTML/PDF スライドを
すぐ作れる。CAテンプレ pptx とは別の「軽量・共有用」出力。

レンダリングは外部パッケージ(marp-cli)を使うため、このスクリプトは Markdown と
テーマCSS を out/ に生成し、実行コマンドを表示するだけ(実行はユーザー)。

使い方:
  python3 tools/build_marp.py --from out/structure.md --theme editorial
  python3 tools/build_marp.py --topic "新規事業の提案" --theme studio --count 8
"""
import argparse, importlib.util, os, re, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out")
CONFIG = os.path.join(ROOT, "config.local.json")

# テーマごとの見た目 (tokens.css の各 theme と対応)
THEMES = {
    "studio":    {"accent": "#8b5cf6", "grad": "linear-gradient(135deg,#7c3aed,#db2777,#06b6d4)",
                  "bg": "#ffffff", "fg": "#0f172a", "muted": "#475569",
                  "display": "'Inter','Noto Sans JP',sans-serif"},
    "editorial": {"accent": "#1e3a5f", "grad": "linear-gradient(135deg,#1e3a5f,#2c5282)",
                  "bg": "#faf7f2", "fg": "#11100f", "muted": "#524d45",
                  "display": "'Noto Serif JP',serif"},
    "focus":     {"accent": "#4f46e5", "grad": "linear-gradient(135deg,#6366f1,#4f46e5)",
                  "bg": "#f6f8fb", "fg": "#0f172a", "muted": "#475569",
                  "display": "'Inter','Noto Sans JP',sans-serif"},
}


def load_parse_deck():
    spec = importlib.util.spec_from_file_location("bp", os.path.join(ROOT, "tools", "build_pptx.py"))
    bp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bp)
    return bp


def theme_css(name):
    t = THEMES.get(name, THEMES["focus"])
    return f"""/* @theme ds */
@import 'default';
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&family=Noto+Sans+JP:wght@400;500;700;900&family=Noto+Serif+JP:wght@600;700;900&display=swap');

section {{
  background: {t['bg']};
  color: {t['fg']};
  font-family: 'Inter','Noto Sans JP',sans-serif;
  font-size: 26px;
  line-height: 1.7;
  padding: 80px 90px;
}}
h1 {{ font-family: {t['display']}; font-weight: 900; letter-spacing: -0.02em;
  font-size: 60px; line-height: 1.1; color: {t['fg']}; }}
h2 {{ font-family: {t['display']}; font-weight: 900; letter-spacing: -0.02em;
  font-size: 40px; color: {t['fg']}; border-bottom: 3px solid {t['accent']};
  padding-bottom: 12px; }}
h3 {{ font-size: 28px; color: {t['accent']}; }}
strong {{ color: {t['accent']}; }}
ul {{ margin-top: 24px; }}
li {{ margin: 10px 0; color: {t['muted']}; }}
em {{ color: {t['muted']}; font-size: 20px; font-style: normal; }}
a {{ color: {t['accent']}; }}
section.title {{ display: flex; flex-direction: column; justify-content: center; }}
section.title h1 {{ font-size: 76px;
  background: {t['grad']}; -webkit-background-clip: text; background-clip: text;
  -webkit-text-fill-color: transparent; }}
section.title p {{ color: {t['muted']}; font-size: 28px; margin-top: 16px; }}
section::after {{ color: {t['muted']}; font-size: 16px; }} /* ページ番号 */
"""


def deck_to_marp(title, slides, subtitle, theme, bp):
    out = ["---", "marp: true", "theme: ds", "paginate: true", "---", ""]
    # 表紙 (タイトルスライドが表紙を兼ねるので、構成側の表紙ロールは除外)
    out += ["<!-- _class: title -->", f"# {title}", "", f"{subtitle}" if subtitle else "", ""]
    for sl in slides:
        if bp.is_cover(sl):
            continue
        out.append("---")
        out.append("")
        out.append(f"## {sl['role']}")
        out.append("")
        if sl.get("layout"):
            out.append(f"**レイアウト**: {sl['layout']}")
            out.append("")
        for el in sl.get("elements", []):
            out.append(f"- {el}")
        if sl.get("hint"):
            out.append("")
            out.append(f"*記入ヒント: {sl['hint']}*")
        out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="スライド構成 → Marp (Markdown+テーマCSS)")
    ap.add_argument("--from", dest="from_file", help="構成 Markdown")
    ap.add_argument("--topic", help="提案テーマ (Dify を呼ぶ)")
    ap.add_argument("--theme", default="focus", choices=list(THEMES))
    ap.add_argument("--tone", default="")
    ap.add_argument("--audience", default="")
    ap.add_argument("--goal", default="")
    ap.add_argument("--count", default="")
    ap.add_argument("--outline", default="")
    args = ap.parse_args()

    bp = load_parse_deck()
    if args.from_file:
        md = open(args.from_file, encoding="utf-8").read()
    elif args.topic:
        import json
        cfg = json.load(open(CONFIG, encoding="utf-8"))
        print("Dify で構成を生成中…", file=sys.stderr)
        md = bp.call_dify(cfg, {"mode": "deck", "theme": args.theme, "tone": args.tone,
                                "topic": args.topic, "audience": args.audience, "goal": args.goal,
                                "constraints": "", "idea": "", "count": args.count, "outline": args.outline})
    else:
        sys.exit("--from か --topic を指定してください。")

    title, slides = bp.parse_deck(md)
    if not slides:
        sys.exit("構成を解析できませんでした。")
    os.makedirs(OUT, exist_ok=True)
    slug = re.sub(r"[^\w\-]+", "-", title.lower())[:36] or "deck"
    md_path = os.path.join(OUT, slug + ".md")
    css_path = os.path.join(OUT, "ds.css")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(deck_to_marp(title, slides, args.topic or "", args.theme, bp))
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(theme_css(args.theme))

    print(f"[OK] Marp 生成: {os.path.relpath(md_path, ROOT)} / {os.path.relpath(css_path, ROOT)} ({len(slides)+1} スライド)")
    print("レンダリング (どちらか):")
    print(f"  PDF : npx --yes @marp-team/marp-cli {md_path} --theme {css_path} --allow-local-files -o {OUT}/{slug}.pdf")
    print(f"  HTML: npx --yes @marp-team/marp-cli {md_path} --theme {css_path} -o {OUT}/{slug}.html")


if __name__ == "__main__":
    main()
