# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "pandas",
#     "altair",
# ]
# ///

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    import io
    import json
    import sys

    import altair as alt
    import pandas as pd
    return alt, io, json, pd, sys


@app.cell
def _(io, mo, sys):
    IN_BROWSER = sys.platform == "emscripten"

    def read_text(rel: str) -> str:
        """本地讀檔；在瀏覽器（WASM）內則從同一網址讀取。"""
        loc = mo.notebook_location() / rel
        if IN_BROWSER:
            from pyodide.http import open_url

            return open_url(str(loc)).read()
        with open(loc, encoding="utf-8") as f:
            return f.read()

    def read_csv_text(rel: str):
        return io.StringIO(read_text(rel))
    return IN_BROWSER, read_csv_text, read_text


@app.cell
def _(IN_BROWSER, json, mo, read_text):
    if IN_BROWSER:
        run_files = json.loads(read_text("runs/index.json"))
    else:
        run_files = sorted(p.name for p in (mo.notebook_location() / "runs").glob("*.csv"))
    run_picker = mo.ui.dropdown(
        options=run_files, value=run_files[-1], label="選擇評測記錄（run）"
    )
    return (run_picker,)


@app.cell
def _(mo, run_picker):
    is_demo = "demo" in run_picker.value
    banner = (
        mo.callout(
            mo.md(
                "**注意：這是示範資料，並非真實模型輸出。**"
                "「實際」一欄由人手撰寫，並故意加入錯誤，用來示範判定規則與人手覆核。"
                "接上真模型後，執行 `python run_eval.py` 會產生新的 run 檔案。"
            ),
            kind="warn",
        )
        if is_demo
        else mo.md("")
    )
    mo.vstack(
        [
            mo.md(
                "# 香港用藥安全 AI 評測\n"
                "20 題香港藥物規管常識題，每題附官方來源。"
                "四欄：**輸入**（題目）、**預期**（官方答案）、**實際**（模型答案）、**判定**（PASS／FAIL）。"
            ),
            run_picker,
            banner,
        ]
    )
    return


@app.cell
def _(pd, read_csv_text, run_picker):
    questions = pd.read_csv(read_csv_text("questions.csv"), dtype=str).fillna("")
    run = pd.read_csv(read_csv_text(f"runs/{run_picker.value}"), dtype=str).fillna("")

    def norm(s: str) -> str:
        return "".join(str(s).lower().split())

    def auto_judge(actual: str, keywords: str) -> str:
        """關鍵詞規則：以 ; 分組，每組都要命中；組內以 | 分隔，命中其一即可。"""
        text = norm(actual)
        groups = [g for g in keywords.split(";") if g.strip()]
        ok = all(any(norm(alt) in text for alt in g.split("|")) for g in groups)
        return "PASS" if ok else "FAIL"

    df = questions.merge(run, on="id", how="left").fillna("")
    df["自動判定"] = [auto_judge(a, k) for a, k in zip(df["actual"], df["keywords"])]
    df["判定"] = [o.strip().upper() or a for o, a in zip(df["override"], df["自動判定"])]
    df["人手覆核"] = ["是" if o.strip() else "" for o in df["override"]]
    return (df,)


@app.cell
def _(df, mo):
    n = len(df)
    passed = int((df["判定"] == "PASS").sum())
    overridden = int((df["人手覆核"] == "是").sum())
    mo.hstack(
        [
            mo.stat(value=f"{passed} / {n}", label="總分"),
            mo.stat(value=f"{passed / n:.0%}", label="正確率"),
            mo.stat(value=str(overridden), label="人手覆核改判"),
        ],
        justify="start",
    )
    return


@app.cell
def _(alt, df):
    counts = df["判定"].value_counts().reindex(["PASS", "FAIL"], fill_value=0).reset_index()
    counts.columns = ["判定", "題數"]
    chart = (
        alt.Chart(counts)
        .mark_bar()
        .encode(
            x=alt.X("判定:N", sort=["PASS", "FAIL"]),
            y=alt.Y("題數:Q"),
            color=alt.Color(
                "判定:N",
                scale=alt.Scale(domain=["PASS", "FAIL"], range=["#2e7d32", "#c62828"]),
                legend=None,
            ),
        )
        .properties(width=300, height=220, title="判定分佈")
    )
    chart
    return


@app.cell
def _(df, mo):
    table = df.rename(
        columns={"question": "輸入", "expected": "預期", "actual": "實際", "source": "來源", "note": "備註"}
    )[["id", "輸入", "預期", "實際", "判定", "自動判定", "人手覆核", "來源", "備註"]]
    mo.vstack([mo.md("## 各題判定"), mo.ui.table(table, selection=None, page_size=20)])
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 判定規則
    - `questions.csv` 的 `keywords` 欄：以 `;` 分組，每組都要命中；組內以 `|` 分隔同義詞，命中其一即可（不分大小寫、忽略空格）。
    - run 檔案的 `override` 欄填 `PASS` 或 `FAIL`，即以人手覆核取代自動判定。
    - 關鍵詞匹配只是粗篩，例如第 20 題的示範答案含「不能」二字而被誤判為 PASS，須人手改判。
    """)
    return


if __name__ == "__main__":
    app.run()
