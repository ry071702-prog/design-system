#!/usr/bin/env python3
"""
scout_designs.py — 世の中のデザインを自動で取り込む収集エンジン (ローカル専用)。

フロー: デザイン系 RSS を取得 → 新着を抽出 → Dify(デザイン収集スカウト)で
観点・抽出トークン・タグを付与 → microlink でスクリーンショットURL取得 →
data/references.json の inbox に追記 (URL で重複排除)。

人手の「選別(promote)」は従来どおり library.html / references.md で行う。
これは「収集(inbox)」の自動化部分。

使い方:
  python3 tools/scout_designs.py                # 既定ソースを収集
  python3 tools/scout_designs.py --limit 4 --dry-run
設定: config.local.json の difyBaseUrl / difyScoutAppKey、任意で scoutSources。
"""
import argparse, json, os, re, sys, hashlib, datetime, urllib.request, urllib.parse
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(ROOT, "config.local.json")
REFS = os.path.join(ROOT, "data", "references.json")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

DEFAULT_SOURCES = [
    {"name": "minimal.gallery", "feed": "https://minimal.gallery/feed/"},
    {"name": "Codrops", "feed": "https://tympanus.net/codrops/feed/"},
]


def load_config():
    if not os.path.exists(CONFIG):
        sys.exit("config.local.json がありません。")
    with open(CONFIG, encoding="utf-8") as f:
        return json.load(f)


def http_get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def fetch_feed(feed):
    """RSS を取得して [{title, link, date, categories}] を返す。"""
    raw = http_get(feed)
    root = ET.fromstring(raw)
    items = []
    for it in root.iter("item"):
        def t(tag):
            e = it.find(tag)
            return (e.text or "").strip() if e is not None and e.text else ""
        cats = [c.text.strip() for c in it.findall("category") if c.text]
        date = ""
        pub = t("pubDate")
        if pub:
            try:
                date = datetime.datetime.strptime(pub[:25], "%a, %d %b %Y %H:%M:%S").date().isoformat()
            except Exception:
                date = ""
        items.append({"title": t("title"), "link": t("link"),
                      "date": date or datetime.date.today().isoformat(), "categories": cats})
    return items


def call_dify_scout(cfg, title, source, categories):
    body = json.dumps({"inputs": {"title": title, "source": source, "categories": ", ".join(categories)},
                       "response_mode": "blocking", "user": "scout"}).encode("utf-8")
    req = urllib.request.Request(
        cfg["difyBaseUrl"].rstrip("/") + "/workflows/run", data=body,
        headers={"Authorization": "Bearer " + cfg["difyScoutAppKey"], "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.loads(r.read().decode("utf-8"))
    txt = (data.get("data") or {}).get("outputs", {}).get("result", "")
    txt = re.sub(r"^```(?:json)?|```$", "", txt.strip(), flags=re.M).strip()
    try:
        return json.loads(txt)
    except Exception:
        return {"whatsGood": "", "extract": "", "tags": []}


def screenshot(url, attempts=2):
    """microlink でスクリーンショットURLを取得 (失敗時は空)。一時失敗に備え数回リトライ。"""
    api = "https://api.microlink.io/?" + urllib.parse.urlencode(
        {"url": url, "screenshot": "true", "meta": "false"})
    for i in range(attempts):
        try:
            data = json.loads(http_get(api, timeout=45))
            shot = ((data.get("data") or {}).get("screenshot") or {}).get("url", "") or ""
            if shot:
                return shot
        except Exception:
            pass
        import time
        time.sleep(2)
    return ""


def slugify(s):
    s = re.sub(r"[^\w\s-]", "", (s or "").lower()).strip()
    return re.sub(r"\s+", "-", s)[:36] or "ref"


VAULT_INBOX = os.path.expanduser("~/Documents/obsidian/mybrain/Inbox")


def run_digest():
    """週次レビュー用: 直近7日に自動収集した未選別(inbox)を Obsidian Inbox に要約する。"""
    with open(REFS, encoding="utf-8") as f:
        refs = json.load(f)
    today = datetime.date.today()
    week_ago = (today - datetime.timedelta(days=7)).isoformat()
    recent = [r for r in refs.get("references", [])
              if r.get("auto") and r.get("status") == "inbox" and r.get("added", "") >= week_ago]
    os.makedirs(VAULT_INBOX, exist_ok=True)
    path = os.path.join(VAULT_INBOX, today.isoformat() + ".md")
    now = datetime.datetime.now().strftime("%H:%M")
    lines = []
    if not os.path.exists(path):
        lines.append(f"# {today.isoformat()} Inbox\n")
    lines.append(f"- **{now}** [#design/scout] 今週の自動収集デザイン {len(recent)}件が未選別。library.html で promote/破棄を (Claude)")
    for r in recent[:12]:
        lines.append(f"    - [{r['title']}]({r['url']}) — {r.get('source','')} / {', '.join(r.get('tags', [])[:3])}")
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"[OK] 週次ダイジェスト: {len(recent)}件 → {path}")


def main():
    ap = argparse.ArgumentParser(description="デザイン自動収集 → references.json の inbox に追記")
    ap.add_argument("--limit", type=int, default=6, help="1回の最大追加件数 (既定6)")
    ap.add_argument("--dry-run", action="store_true", help="書き込まずに結果だけ表示")
    ap.add_argument("--no-shot", action="store_true", help="スクショ取得をスキップ")
    ap.add_argument("--digest", action="store_true", help="週次レビュー: 直近7日の収集を Obsidian Inbox に要約")
    args = ap.parse_args()

    if args.digest:
        run_digest()
        return

    cfg = load_config()
    if not cfg.get("difyScoutAppKey"):
        sys.exit("config.local.json に difyScoutAppKey がありません。")
    sources = cfg.get("scoutSources") or DEFAULT_SOURCES

    with open(REFS, encoding="utf-8") as f:
        refs = json.load(f)
    existing = {r.get("url") for r in refs.get("references", [])}

    # 全ソースの新着を集めて新しい順に
    candidates = []
    for src in sources:
        try:
            for it in fetch_feed(src["feed"]):
                if it["link"] and it["link"] not in existing:
                    candidates.append({**it, "source": src["name"]})
        except Exception as e:
            print(f"[warn] {src['name']} 取得失敗: {e}", file=sys.stderr)
    candidates.sort(key=lambda x: x["date"], reverse=True)

    seen, picked = set(), []
    for c in candidates:
        if c["link"] in seen:
            continue
        seen.add(c["link"])
        picked.append(c)
        if len(picked) >= args.limit:
            break

    print(f"新着候補 {len(candidates)} 件 → 追加 {len(picked)} 件", file=sys.stderr)
    added = []
    for c in picked:
        meta = call_dify_scout(cfg, c["title"], c["source"], c["categories"])
        shot = "" if args.no_shot else screenshot(c["link"])
        tags = meta.get("tags") or []
        tags = list(dict.fromkeys([t.strip().lower() for t in tags if t.strip()] +
                                  [x.lower() for x in c["categories"][:2] if x and x.lower() != "uncategorized"]))
        entry = {
            "id": slugify(c["title"]) + "-" + hashlib.sha1(c["link"].encode()).hexdigest()[:6],
            "title": c["title"],
            "url": c["link"],
            "shot": shot,
            "whatsGood": meta.get("whatsGood", ""),
            "extract": meta.get("extract", ""),
            "tags": tags[:6],
            "status": "inbox",
            "date": c["date"],
            "added": datetime.date.today().isoformat(),
            "source": c["source"],
            "auto": True,
        }
        added.append(entry)
        print(f"  + [{c['source']}] {c['title']}  (shot={'有' if shot else '無'}, tags={tags[:4]})", file=sys.stderr)

    if args.dry_run:
        print(json.dumps(added, ensure_ascii=False, indent=2))
        return
    refs["references"] = added + refs.get("references", [])
    with open(REFS, "w", encoding="utf-8") as f:
        json.dump(refs, f, ensure_ascii=False, indent=2)
    print(f"[OK] {len(added)} 件を inbox に追加 → {REFS}")


if __name__ == "__main__":
    main()
