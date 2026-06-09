#!/usr/bin/env python3
"""
deck_to_pdf.py — 作成済みスライド(pptx)を全ページ PDF に変換 (LibreOffice headless)。

slides.html の「全ページ」ボタンから使う。soffice は GUI/ダイアログ無しで安定して
全ページ PDF を生成できる(PowerPoint AppleScript は -9074 で不安定だったため不採用)。

使い方:
  python3 tools/deck_to_pdf.py <slides.json の id> [--open]
  python3 tools/deck_to_pdf.py --path "/path/deck.pptx" [--open]
PDF は data/slide-pdfs/<id>.pdf にキャッシュ (元より新しければ再利用)。
"""
import argparse, json, os, sys, subprocess, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLIDES = os.path.join(ROOT, "data", "slides.json")
PDF_DIR = os.path.join(ROOT, "data", "slide-pdfs")
SOFFICE = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
PROFILE = "file:///tmp/lo-ds-profile"  # GUI と競合しない専用プロファイル


def resolve_path(args):
    if args.path:
        return args.path
    if not os.path.exists(SLIDES):
        sys.exit("data/slides.json がありません。先に python3 tools/index_slides.py を実行してください。")
    with open(SLIDES, encoding="utf-8") as f:
        for it in json.load(f).get("slides", []):
            if it.get("id") == args.ref_id:
                return it["path"]
    sys.exit(f"id '{args.ref_id}' が slides.json に見つかりません。")


def convert(src, dst):
    """soffice で pptx → pdf。成功で dst パスを返す。"""
    if not os.path.exists(SOFFICE):
        sys.exit("LibreOffice が見つかりません。brew install --cask libreoffice を実行してください。")
    os.makedirs(PDF_DIR, exist_ok=True)
    r = subprocess.run(
        [SOFFICE, "-env:UserInstallation=" + PROFILE, "--headless",
         "--convert-to", "pdf", "--outdir", PDF_DIR, src],
        capture_output=True, text=True, timeout=600)
    # soffice は <basename>.pdf を outdir に作る → 目的の名前にリネーム
    produced = os.path.join(PDF_DIR, os.path.splitext(os.path.basename(src))[0] + ".pdf")
    if not os.path.exists(produced):
        raise RuntimeError("変換失敗: " + (r.stderr or r.stdout or "")[:300])
    if produced != dst:
        os.replace(produced, dst)
    return dst


def main():
    ap = argparse.ArgumentParser(description="pptx → 全ページ PDF (LibreOffice)")
    ap.add_argument("ref_id", nargs="?", help="slides.json の id")
    ap.add_argument("--path", help="pptx を直接指定")
    ap.add_argument("--open", action="store_true", help="生成後に開く")
    args = ap.parse_args()
    if not args.ref_id and not args.path:
        sys.exit("id か --path を指定してください。")

    src = resolve_path(args)
    if not os.path.exists(src):
        sys.exit(f"ファイルがありません: {src}")
    if not src.lower().endswith(".pptx"):
        sys.exit("pptx のみ対応です。")

    key = args.ref_id or hashlib.sha1(src.encode()).hexdigest()[:16]
    dst = os.path.join(PDF_DIR, key + ".pdf")
    if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
        print(f"[cache] {dst}")
    else:
        print("LibreOffice で PDF 変換中…", file=sys.stderr)
        convert(src, dst)
        print(f"[OK] {dst}")
    if args.open:
        subprocess.run(["open", dst], check=False)


if __name__ == "__main__":
    main()
