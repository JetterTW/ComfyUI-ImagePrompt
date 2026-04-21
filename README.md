# ComfyUI-ImagePrompt

[![Author](https://img.shields.io/badge/Author-Jetter-blue.svg)](https://github.com/JetterTW)
[![GitHub Stars](https://img.shields.io/github/stars/JetterTW/ComfyUI-ImagePrompt?style=social)](https://github.com/JetterTW/ComfyUI-ImagePrompt/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**ComfyUI-ImagePrompt** 是一個專為視覺模型設計的強大提示詞生成節點。它透過連接大型語言模型 (LLM)，自動分析輸入的圖像，並將其視覺特徵轉化為高品質的提示詞。

本專案支援同時輸出 **英文 Prompt** (用於繪圖) 與 **繁體/簡體中文 Prompt** (用於理解與驗證)，讓你在創作時能精準掌控 AI 生成的細節。

## ✨ 功能特點

* **🌓 圖像視覺理解**：利用多模態視覺模型 (Vision LLM) 分析圖像內容，將視覺資訊轉化為文字描述。
* **🌐 多語言同步輸出**：一次生成英文 Prompt 用於繪圖，並同時提供繁體與簡體中文對照，兼顧繪圖實用性與視覺理解。
* **⚙️ 高度靈活性**：
    * **自訂模型**：直接在節點上指定 model_name (如 oss-20b, gpt-4o, qwen-vl)。
    * **自訂端點**：支援自訂 api_url，可輕鬆連接本地 (LM Studio, vLLM, Ollama) 或遠端伺服器。
    * **自訂指令**：透過系統提示詞選擇器切換預設模板，或使用 Custom 選項直接輸入自訂的系統提示詞。
* **🔌 全兼容 API 介面**：採用 OpenAI API 標準格式，支援幾乎所有主流的視覺語言模型 (VLM) 後端。
* **🛡️ 穩定輸出**：內建強大的 JSON 解析與 Markdown 清理機制，確保輸出結果能直接被 ComfyUI 節點讀取，不會因為模型多吐了字元而導致錯誤。

## 🚀 安裝方法

1. 進入您的 ComfyUI/custom_nodes 目錄。
2. 使用 Git 下載本專案：
```
git clone https://github.com/JetterTW/ComfyUI-ImagePrompt.git
```
3. 進入ComfyUI-ImagePrompt 目錄並確保已安裝依賴套件：
```
cd ComfyUI-ImagePrompt
pip install -r requirements.txt
```
4. 重啟 ComfyUI。

## 🛠 參數說明

| 參數 | 類型 | 預設值 | 說明 |
| :--- | :--- | :--- | :--- |
| image | IMAGE | - | 輸入您想要分析的圖像。 |
| api_url | STRING | http://192.168.1.9:8000/v1 | LLM API 的端點網址 (自動補上 /chat/completions)。 |
| model_name | STRING | oss-20b | 指定要使用的模型名稱。 |
| api_key | STRING | apikey | API 認證金鑰 (本地模型通常填 apikey 或 not-needed)。 |
| system_prompt_selector | OPTION | default | 從 prompt 目錄下選擇 .md 檔案作為系統提示詞。 |
| custom_system_prompt | STRING | Describe this image... | 當選擇器選擇 Custom 時，在此輸入自訂的系統提示詞。 |
| max_tokens | INT | 2048 | 生成文字的最大長度上限。 |
| temperature | FLOAT | 0.7 | 創意程度 (0.0 - 2.0)。越高越具想像力。 |
| seed | INT | 0 | 隨機種子，確保生成結果的可重複性。 |

## 💡 使用範例

### 場景一：使用本地 vLLM 或 LM Studio (完全隱私)
* api_url: http://127.0.0.1:1234/v1
* model_name: local-vision-model

### 場景二：使用遠端伺服器 (例如 vLLM 連線到 192.168.1.9)
* api_url: http://192.168.1.9:8000/v1
* model_name: Gemma-4-26b

## 📋 推薦工作流 (Workflow)

1. **Input**: 使用 ImageToMultiPrompt 節點輸入一張圖片。
2. **Generation**: 將 en_prompt 輸出端連接至 CLIP Text Encode 作為繪圖提示詞。
3. **Review**: 將 zh_tw_prompt 或 zh_cn_prompt 輸出端連接至 Show Text 節點，以便確認 AI 解析的內容是否符合預期。

## 📂 系統提示詞範例
節點會自動讀取 prompt 目錄下的 .md 檔案，您可以參考該目錄下的範例檔案來定義不同的模型角色與風格。

## ⚠️ 注意事項

* **URL 格式**：請確保 API URL 指向的是 /v1 結尾的路徑 (例如 http://127.0.0.1:1234/v1)。
* **模型選擇**：由於此節點需要分析圖片，請務必使用支援 Vision (多模態) 的模型 (如 GPT-4o, LLaVA, Qwen-VL)。
* **網路環境**：若連接遠端 IP，請確保網路連線暢通且該伺服器的 Port 已開啟。

## 🤝 貢獻與回報

如果您發現任何問題或有改進建議，歡迎提交 Issue 或 Pull Request。

也可以請我[喝杯咖啡](https://p.ecpay.com.tw/778EAAD)。

---
**Author:** [Jetter](https://github.com/JetterTW)  
**License:** MIT
