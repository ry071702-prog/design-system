#!/usr/bin/env python3
"""
export_pptx.py — HTML スライド (.slide 要素) を html2pptx.app の REST API で
編集可能な .pptx に変換する (ローカル専用ツール)。

build_pptx.py が「CA 公式テンプレ複製」ルートなのに対し、こちらは
tokens.css ベースの HTML デザインをそのまま PPTX 化する第2ルート。

HTML 規約 (html2pptx.app の HTML Contract):
  - 1 スライド = .slide クラスを持つ要素 1 つ。幅・高さを px で明示する
    (例: <section class="slide" style="width:1600px;height:900px">)
  - script / iframe / form / a タグは除去される
  - 画像は絶対 URL か base64 データ URI のみ

使い方:
  python3 tools/export_pptx.py --html out/deck.html --open
  python3 tools/export_pptx.py --html out/deck.html --css tokens.css \
      --name 提案資料.pptx

設定: config.local.json の html2pptxApiKey を使う (https://html2pptx.app で
無料登録して取得)。無料枠: 100 件/日・3 リクエスト/分・50 スライド/ジョブ・
ペイロード 1MB。
"""
import argparse, json, os, sys, time, subprocess, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(ROOT, "config.local.json")
BASE_URL = "https://html2pptx.app"
PAYLOAD_LIMIT = 1_000_000  # 無料枠 1MB
POLL_INTERVAL = 2          # 秒 (ドキュメント推奨)
POLL_TIMEOUT = 300         # 秒


def load_api_key():
    if not os.path.exists(CONFIG):
        sys.exit("config.local.json がありません。config.example.json をコピーして設定してください。")
    with open(CONFIG, encoding="utf-8") as f:
        key = json.load(f).get("html2pptxApiKey", "")
    if not key or key.startswith("sk_live_xxxx"):
        sys.exit("config.local.json に html2pptxApiKey がありません。\n"
                 "https://html2pptx.app で無料登録して API キーを取得・設定してください。")
    return key


def api(key, method, path, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        BASE_URL + path, data=data, method=method,
        headers={"Authorization": "Bearer " + key,
                 "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:500]
        sys.exit(f"API エラー {e.code} ({method} {path}): {detail}")


def create_job(key, html, css, file_name):
    body = {"fileName": file_name, "html": html, "css": css,
            "responseFormat": "url"}
    size = len(json.dumps(body).encode("utf-8"))
    if size > PAYLOAD_LIMIT:
        sys.exit(f"ペイロードが {size/1e6:.2f}MB で無料枠の上限 1MB を超えています。"
                 "画像を URL 参照にするか、スライドを分割してください。")
    job = api(key, "POST", "/api/export/jobs", body)
    job_id = job.get("jobId")
    if not job_id:
        sys.exit("jobId が返りませんでした: " + json.dumps(job, ensure_ascii=False))
    return job_id


def wait_job(key, job_id):
    deadline = time.time() + POLL_TIMEOUT
    while time.time() < deadline:
        job = api(key, "GET", f"/api/export/jobs/{job_id}")
        status = job.get("status")
        if status == "completed":
            return job
        if status == "failed":
            sys.exit("変換失敗: " + json.dumps(job, ensure_ascii=False))
        print(f"  status={status} ...", file=sys.stderr)
        time.sleep(POLL_INTERVAL)
    sys.exit(f"{POLL_TIMEOUT} 秒以内に完了しませんでした (jobId={job_id})")


def download(url, dest):
    with urllib.request.urlopen(url, timeout=120) as r, open(dest, "wb") as f:
        f.write(r.read())


def main():
    ap = argparse.ArgumentParser(description="HTML スライドを html2pptx.app で .pptx 化")
    ap.add_argument("--html", required=True, help=".slide 要素を含む HTML ファイル")
    ap.add_argument("--css", action="append", default=[],
                    help="追加 CSS ファイル (複数指定可。tokens.css など)")
    ap.add_argument("--name", default=None, help="出力ファイル名 (省略時は HTML 名 + .pptx)")
    ap.add_argument("--open", action="store_true", help="完了後に開く")
    args = ap.parse_args()

    with open(args.html, encoding="utf-8") as f:
        html = f.read()
    css = "\n".join(open(p, encoding="utf-8").read() for p in args.css)

    file_name = args.name or os.path.splitext(os.path.basename(args.html))[0] + ".pptx"
    if not file_name.endswith(".pptx"):
        file_name += ".pptx"

    key = load_api_key()
    print(f"ジョブ作成: {file_name}", file=sys.stderr)
    job_id = create_job(key, html, css, file_name)
    job = wait_job(key, job_id)

    out_dir = os.path.join(ROOT, "out")
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, file_name)
    download(job["downloadUrl"], dest)
    print(f"完了 ({job.get('slideCount', '?')} 枚) → {dest}")
    if args.open:
        subprocess.run(["open", dest])


if __name__ == "__main__":
    main()
