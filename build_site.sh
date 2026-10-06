#!/usr/bin/env bash
# 匯出 WASM 網頁版到 docs/，並複製題庫與 runs，讓瀏覽器內的筆記本讀取。
set -euo pipefail
cd "$(dirname "$0")"
rm -rf docs
marimo export html-wasm eval.py -o docs --mode run
cp questions.csv docs/
mkdir -p docs/runs
cp runs/*.csv docs/runs/
python3 -c "import glob,json,os;json.dump(sorted(os.path.basename(p) for p in glob.glob('runs/*.csv')),open('docs/runs/index.json','w'))"
touch docs/.nojekyll
echo "OK: docs/"
