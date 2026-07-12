#!/usr/bin/env python3
"""
promote_design.py — デザインの「還元」自動化 (ローカル専用)。

収集したデザインの良いパターンを、現行 tokens.css に整合する「追記専用の
トークン提案」へ Dify(デザイン還元キュレーター, Claude Sonnet)が変換し、
人がレビューできる提案を data/promotions/<id>.md に書き出す。承認できたら
--apply で tokens.css に追記し、references.md/json に記録する。

tokens.css は聖域なので、--apply は「既存値を壊さない追記」だけを行う。
既存値の変更提案(value_changes)は適用せず、人が手動判断する。

使い方:
  python3 tools/promote_design.py <ref-id>            # 1件の還元案を生成 (提案のみ)
  python3 tools/promote_design.py <ref-id> --apply    # 提案を tokens.css へ追記
  python3 tools/promote_design.py --weekly            # 直近7日のinboxをまとめて提案
  python3 tools/promote_design.py --list              # ref 一覧と状態
"""
import argparse, json, os, re, sys, datetime, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(ROOT, "config.local.json")
REFS = os.path.join(ROOT, "data", "references.json")
TOKENS = os.path.join(ROOT, "tokens.css")
REFS_MD = os.path.join(ROOT, "references.md")
PROM_DIR = os.path.join(ROOT, "data", "promotions")


def load_config():
    with open(CONFIG, encoding="utf-8") as f:
        return json.load(f)


def load_refs():
    with open(REFS, encoding="utf-8") as f:
        return json.load(f)


def save_refs(d):
    with open(REFS, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


def call_dify_promote(cfg, ref, tokens_css):
    body = json.dumps({"inputs": {
        "title": ref.get("title", ""), "whatsGood": ref.get("whatsGood", ""),
        "extract": ref.get("extract", ""), "tags": ", ".join(ref.get("tags", [])),
        "tokens": tokens_css},
        "response_mode": "blocking", "user": "promote"}).encode("utf-8")
    req = urllib.request.Request(
        cfg["difyBaseUrl"].rstrip("/") + "/workflows/run", data=body,
        headers={"Authorization": "Bearer " + cfg["difyPromoteAppKey"], "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        data = json.loads(r.read().decode("utf-8"))
    txt = (data.get("data") or {}).get("outputs", {}).get("result", "")
    txt = re.sub(r"^```(?:json)?|```$", "", txt.strip(), flags=re.M).strip()
    return json.loads(txt)


# --- 重複チェック --------------------------------------------------------
# 還元を重ねると同名のレシピ / トークンが別ブロックで再定義され、CSS の「後勝ち」で
# 意図しない合成が起きる (2026-07-12 に .ds-section x5 / .ds-section-divider x5 を
# 名寄せした)。適用前にそれを検出して、リネームか統合を人に判断させる。

def strip_css_comments(css):
    out, i = [], 0
    while i < len(css):
        j = css.find("/*", i)
        if j < 0:
            out.append(css[i:])
            break
        out.append(css[i:j])
        k = css.find("*/", j + 2)
        i = len(css) if k < 0 else k + 2
    return "".join(out)


def parse_rules(css):
    """CSS を [(@ルール文脈, セレクタ, {宣言プロパティ名})] に分解する

    @media 内の同名セレクタは「レスポンシブ上書き」で正当なので、文脈をキーに含めて
    トップレベルの再定義とは区別する。@keyframes の中身は宣言ではないので捨てる。
    """
    css = strip_css_comments(css)
    rules, stack, depth, start = [], [], 0, 0
    for i, ch in enumerate(css):
        if ch == "{":
            stack.append((css[start:i].strip(), i + 1))
            depth += 1
            start = i + 1
        elif ch == "}":
            if stack:
                head, body_start = stack.pop()
                context = " ".join(h for h, _ in stack if h.startswith("@"))
                if not head.startswith("@") and "keyframes" not in context:
                    props = set(re.findall(r"([\w-]+)\s*:", css[body_start:i]))
                    for sel in (s.strip() for s in head.split(",")):
                        if sel:
                            rules.append((context, sel, props))
            depth -= 1
            start = i + 1
        elif ch == ";" and depth == 0:
            start = i + 1
    return rules


def find_duplicates(new_css, tokens_css):
    """追記予定の CSS が tokens.css の既存定義とぶつかる箇所を返す"""
    existing = {}
    for ctx, sel, props in parse_rules(tokens_css):
        existing.setdefault((ctx, sel), set()).update(props)
    dup_sel, dup_prop = [], []
    for ctx, sel, props in parse_rules(new_css):
        if (ctx, sel) not in existing:
            continue
        clash = sorted(props & existing[(ctx, sel)])
        # :root / テーマ / ダークは「同じプロパティを再定義したときだけ」重複とみなす
        if sel.startswith((":root", "[data-theme", ".dark", ".theme-", "html", "body", "*")):
            if clash:
                dup_prop.append((sel, clash))
        else:
            dup_sel.append((sel, clash))
    return dup_sel, dup_prop


def duplicate_report(new_css, tokens_css):
    dup_sel, dup_prop = find_duplicates(new_css, tokens_css)
    if not dup_sel and not dup_prop:
        return ""
    lines = []
    for sel, clash in dup_sel:
        hint = "宣言が重なる: " + ", ".join(clash) if clash else "宣言は重ならないが同名"
        lines.append(f"  - レシピ `{sel}` は tokens.css に既にある ({hint})")
    for sel, clash in dup_prop:
        lines.append(f"  - `{sel}` の {', '.join(clash)} は既に定義済み (後勝ちで上書きされる)")
    return "\n".join(lines)


def proposal_md(ref, prop):
    return f"""# 還元案: {ref.get('title','')}

- 元デザイン: {ref.get('url','')}
- 出典: {ref.get('source','-')} / タグ: {', '.join(ref.get('tags', []))}
- リスク: **{prop.get('risk','?')}**

## 概要
{prop.get('summary','')}

## 反映先
{prop.get('target','')}

## 根拠
{prop.get('rationale','')}

## 追記する CSS (追記専用・既存値は壊さない)
```css
{prop.get('additive_css','') or '(追記候補なし)'}
```

## 重複チェック (既存の tokens.css との衝突)
{duplicate_report(prop.get('additive_css','') or '', open(TOKENS, encoding='utf-8').read()) or '(重複なし)'}

## 既存値の変更提案 (適用は手動判断)
{prop.get('value_changes','') or '(なし)'}

## 採用ログ (references.md 採用済みに残す)
{prop.get('log_line','')}

---
適用: `python3 tools/promote_design.py {ref.get('id','')} --apply`
(tokens.css へ上の「追記する CSS」を追記し、references に記録します。git で差分確認・取り消し可)
"""


def write_proposal(ref, prop):
    os.makedirs(PROM_DIR, exist_ok=True)
    path = os.path.join(PROM_DIR, ref["id"] + ".md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(proposal_md(ref, prop))
    # 構造データも保存 → --apply はこれをそのまま適用する (レビュー内容=適用内容)
    with open(os.path.join(PROM_DIR, ref["id"] + ".json"), "w", encoding="utf-8") as jf:
        json.dump(prop, jf, ensure_ascii=False, indent=2)
    return path


def apply_to_tokens(ref, prop, allow_dup=False):
    css = (prop.get("additive_css") or "").strip()
    if not css:
        return False, "追記候補が無いため tokens.css は変更しません。"
    report = duplicate_report(css, open(TOKENS, encoding="utf-8").read())
    if report and not allow_dup:
        return False, ("既存定義と重複しているため適用を中止しました。\n" + report +
                       "\n\n対応:\n"
                       "  1. 同じ役割なら追記せず既存レシピを使う (提案 json の additive_css から削る)\n"
                       "  2. 挙動が違うなら別名にリネームする (例: .ds-section-hero)\n"
                       "  3. 意図的に上書きするなら --allow-dup を付けて再実行する")
    if report:
        print("[警告] 重複を検出しましたが --allow-dup 指定のため続行します:\n" + report,
              file=sys.stderr)
    today = datetime.date.today().isoformat()
    block = (f"\n\n/* =============================================================================\n"
             f"   還元 (promoted): {ref.get('title','')} — {today}\n"
             f"   {prop.get('summary','').strip()}\n"
             f"   出典: {ref.get('url','')}\n"
             f"   ========================================================================== */\n"
             f"{css}\n")
    with open(TOKENS, "a", encoding="utf-8") as f:
        f.write(block)
    # references.md 採用済みに1行
    log = prop.get("log_line", "").strip()
    if log:
        with open(REFS_MD, "a", encoding="utf-8") as f:
            f.write(f"\n- [{ref.get('title','')}] {log} ({today})\n")
    return True, f"tokens.css に追記しました ({len(css)} 文字)。"


def find_ref(d, ref_id):
    for r in d.get("references", []):
        if r.get("id") == ref_id:
            return r
    return None


def main():
    ap = argparse.ArgumentParser(description="デザイン還元: tokens.css への追記提案を生成/適用")
    ap.add_argument("ref_id", nargs="?", help="対象 reference の id")
    ap.add_argument("--apply", action="store_true", help="生成済み提案を tokens.css に追記")
    ap.add_argument("--allow-dup", action="store_true",
                    help="既存レシピ/トークンと重複していても適用する (既定は中止)")
    ap.add_argument("--weekly", action="store_true", help="直近7日のinboxをまとめて提案 (適用しない)")
    ap.add_argument("--list", action="store_true", help="reference 一覧と状態")
    args = ap.parse_args()

    cfg = load_config()
    if not cfg.get("difyPromoteAppKey"):
        sys.exit("config.local.json に difyPromoteAppKey がありません。")
    d = load_refs()

    if args.list:
        for r in d.get("references", []):
            mark = "✓還元" if r.get("reflected") else ("提案済" if r.get("proposed") else r.get("status", ""))
            print(f"{r.get('id'):42s} [{mark:6s}] {r.get('title','')[:40]}")
        return

    if args.weekly:
        tokens_css = open(TOKENS, encoding="utf-8").read()
        week_ago = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
        targets = [r for r in d.get("references", [])
                   if r.get("status") == "inbox" and not r.get("reflected")
                   and not r.get("proposed") and r.get("added", "") >= week_ago]
        print(f"週次還元: 提案対象 {len(targets)} 件", file=sys.stderr)
        for r in targets:
            try:
                prop = call_dify_promote(cfg, r, tokens_css)
                path = write_proposal(r, prop)
                r["proposed"] = True
                print(f"  + {r['title'][:40]} → {os.path.relpath(path, ROOT)} (risk={prop.get('risk')})")
            except Exception as e:
                print(f"  ! {r['title'][:40]} 失敗: {e}", file=sys.stderr)
        save_refs(d)
        print(f"[OK] 提案を {PROM_DIR} に出力。レビュー後 --apply で適用。")
        return

    if not args.ref_id:
        sys.exit("ref-id を指定するか --weekly / --list を使ってください。 (一覧: --list)")
    ref = find_ref(d, args.ref_id)
    if not ref:
        sys.exit(f"id '{args.ref_id}' が references.json に見つかりません。--list で確認。")

    if args.apply:
        jpath = os.path.join(PROM_DIR, ref["id"] + ".json")
        if os.path.exists(jpath):
            # レビュー済みの提案をそのまま適用 (WYSIWYG)
            with open(jpath, encoding="utf-8") as jf:
                prop = json.load(jf)
        else:
            # 提案が無ければ生成してから適用
            prop = call_dify_promote(cfg, ref, open(TOKENS, encoding="utf-8").read())
            write_proposal(ref, prop)
        ok, msg = apply_to_tokens(ref, prop, allow_dup=args.allow_dup)
        print(msg)
        if not ok and "重複" in msg:
            sys.exit(1)
        if ok:
            ref["status"] = "promoted"
            ref["reflected"] = True
            ref["reflected_date"] = datetime.date.today().isoformat()
            save_refs(d)
            print(f"[OK] {ref['title']} を還元済みに更新。git diff tokens.css で確認できます。")
        return

    # 提案のみ
    prop = call_dify_promote(cfg, ref, open(TOKENS, encoding="utf-8").read())
    path = write_proposal(ref, prop)
    ref["proposed"] = True
    save_refs(d)
    print(f"[OK] 還元案を生成: {os.path.relpath(path, ROOT)}  (risk={prop.get('risk')})")
    print(f"     概要: {prop.get('summary','')[:80]}")
    report = duplicate_report(prop.get("additive_css") or "", open(TOKENS, encoding="utf-8").read())
    if report:
        print("[警告] 既存定義と重複しています (このままでは --apply は中止されます):\n" + report,
              file=sys.stderr)
    print(f"     適用: python3 tools/promote_design.py {ref['id']} --apply")


if __name__ == "__main__":
    main()
