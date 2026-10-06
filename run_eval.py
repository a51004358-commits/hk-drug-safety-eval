"""用真模型重跑評測，輸出 runs/<日期>_<模型>.csv。

用法：
    export LLM_API_KEY=...            # 不要把密鑰寫入檔案或 commit
    export LLM_BASE_URL=https://api.openai.com/v1   # 任何 OpenAI 相容端點
    export LLM_MODEL=gpt-4o-mini
    python run_eval.py

只需改 model_answer() 就可接上其他模型；其餘流程不變。
"""
import csv
import datetime as dt
import json
import os
import re
import urllib.request

SYSTEM = "你是香港藥物規管專家。請用繁體中文，以一至兩句簡潔回答。"


def model_answer(question: str) -> str:
    """輸入一條題目，回傳模型的文字答案。換模型只需改這個函數。"""
    key = os.environ["LLM_API_KEY"]
    base = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("LLM_MODEL", "gpt-4o-mini")
    body = json.dumps({
        "model": model,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": question},
        ],
    }).encode()
    req = urllib.request.Request(
        f"{base}/chat/completions",
        data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["choices"][0]["message"]["content"].strip()


def main() -> None:
    model = os.environ.get("LLM_MODEL", "model")
    out = f"runs/{dt.date.today().isoformat()}_{re.sub(r'[^A-Za-z0-9._-]', '-', model)}.csv"
    with open("questions.csv", encoding="utf-8") as f:
        questions = list(csv.DictReader(f))
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "actual", "override", "note"])
        for q in questions:
            ans = model_answer(q["question"])
            w.writerow([q["id"], ans, "", f"模型：{model}"])
            print(q["id"], ans)
    print("已寫入", out)


if __name__ == "__main__":
    main()
