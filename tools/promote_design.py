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


def apply_to_tokens(ref, prop):
    css = (prop.get("additive_css") or "").strip()
    if not css:
        return False, "追記候補が無いため tokens.css は変更しません。"
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
        ok, msg = apply_to_tokens(ref, prop)
        print(msg)
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
    print(f"     適用: python3 tools/promote_design.py {ref['id']} --apply")


if __name__ == "__main__":
    main()
