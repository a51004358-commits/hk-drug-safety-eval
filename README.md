# 香港用藥安全 AI 評測（hk-drug-safety-eval）

一份可以重跑的 AI 評測範本：以 20 條香港藥物規管常識題測試 AI 模型，逐題記錄並計分。每題附衞生署藥物辦公室、電子版香港法例等官方來源，任何人都可以覆核。

- 網頁版（瀏覽器內直接運行）：https://a51004358-commits.github.io/hk-drug-safety-eval/
- 筆記本：`eval.py`（[marimo](https://marimo.io) 格式，即普通 Python 檔）

> **注意：** 現時的 `runs/2026-10-06_demo.csv` 是**示範資料**，由人手撰寫並故意加入錯誤，用來示範判定規則與人手覆核，**並非真實模型輸出**。

## 四欄定義

| 欄 | 意思 | 來自 |
| --- | --- | --- |
| 輸入 | 題目 | `questions.csv` 的 `question` |
| 預期 | 官方來源支持的答案 | `questions.csv` 的 `expected`（來源見 `source`） |
| 實際 | 模型的回答 | `runs/*.csv` 的 `actual` |
| 判定 | PASS／FAIL | 關鍵詞規則自動判定；`override` 欄可人手改判 |

判定規則：`keywords` 欄以 `;` 分組，每組都要命中；組內以 `|` 分隔同義詞，命中其一即可。關鍵詞匹配只是粗篩，可疑結果應人手覆核，並在 run 檔案的 `override` 欄填 `PASS` 或 `FAIL`。

## 怎樣加題

在 `questions.csv` 加一行：`id,question,expected,source,keywords`。
`source` 必須是可公開查閱的官方網址；`keywords` 寫判定所需的關鍵詞。

## 怎樣換模型重跑

```bash
pip install marimo pandas altair
export LLM_API_KEY=你的密鑰          # 只放環境變數，切勿寫入檔案或 commit
export LLM_BASE_URL=https://api.openai.com/v1   # 任何 OpenAI 相容端點
export LLM_MODEL=gpt-4o-mini
python run_eval.py                  # 產生 runs/<日期>_<模型>.csv
marimo edit eval.py                 # 在下拉選單選新的 run 查看結果
```

換其他模型供應商，只需改 `run_eval.py` 內的 `model_answer()` 函數。

更新網頁版：執行 `./build_site.sh`，把 `docs/` 內容推上 `gh-pages` 分支。`ci/pages.yml` 是自動部署用的 GitHub Actions 檔；以具 `workflow` 權限的帳戶把它移到 `.github/workflows/` 後，每次 push 都會自動更新網頁版。

## 免責聲明

本題庫只作評測用途，並非法律或醫療意見；法例以電子版香港法例最新版本為準。
