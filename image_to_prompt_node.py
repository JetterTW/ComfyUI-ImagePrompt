import json
import requests
import os
import glob

class ImageToMultiPromptNode:
    @classmethod
    def INPUT_TYPES(s):
        # 1. 尋找 prompt 目錄下的所有 .md 檔案
        # 為了簡化，我們直接從執行檔路徑附近尋找
        current_dir = os.path.dirname(os.path.realpath(__file__))
        prompt_dir = os.path.join(current_dir, "prompt")
        
        md_files = []
        if os.path.exists(prompt_dir):
            # 取得所有 .md 檔名，但不含副檔名
            md_files = [os.path.splitext(os.path.basename(f))[0] for f in glob.glob(os.path.join(prompt_dir, "*.md"))]
        
        # 選項列表：檔案名 + 'Custom'
        options = md_files + ["Custom"]
        if not options:
            options = ["default"]

        return {
            "required": {
                "image": ("IMAGE",),
                "api_url": ("STRING", {"default": "http://192.168.1.9:8000/v1"}),
                "model_name": ("STRING", {"default": "GPT-4o"}),
                "api_key": ("STRING", {"default": "apikey"}),
                "system_prompt_selector": (options, ),
                "custom_system_prompt": ("STRING", {"multiline": True, "default": "Describe this image in detail."}),
                "max_tokens": ("INT", {"default": 2048, "min": 1, "max": 8192}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.01}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
        }

    # 返回三個輸出類型
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("en_prompt", "zh_tw_prompt", "zh_cn_prompt")
    FUNCTION = "generate_prompts"
    CATEGORY = "CustomNodes/Vision"

    def load_md_content(self, selector, current_dir):
        """讀取指定 md 檔案的內容"""
        prompt_dir = os.path.join(current_dir, "prompt")
        file_path = os.path.join(prompt_dir, f"{selector}.md")
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        return ""

    def generate_prompts(self, image, api_url, model_name, api_key, system_prompt_selector, custom_system_prompt, max_tokens, temperature, seed):
        # 1. 處理圖片 (將 Tensor 轉為 base64 格式，這是呼叫多模態模型必備的)
        # 注意：這裡假設你的 API 是 OpenAI 相容的 Vision 模型 (如 GPT-4o 或 LLaVA)
        # 為了簡化，這裡假設 API 接收標準 base64 圖片數據
        import torch
        import numpy as np
        from PIL import Image
        import io
        import base64

        # 將 ComfyUI Tensor 轉為 PIL Image
        # image 是 [Batch, Height, Width, Channels]
        img_tensor = image[0] # 取第一張
        img_np = 255. * img_tensor.cpu().numpy()
        img_np = img_np.astype(np.uint8)
        # 轉回 HWC 格式
        img_pil = Image.fromarray(img_np)
        
        # 轉 Base64
        buffered = io.BytesIO()
        img_pil.save(buffered, format="JPEG")
        base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

        # 2. 決定系統提示詞 (System Prompt)
        current_dir = os.path.dirname(os.path.realpath(__file__))
        if system_prompt_selector == "Custom":
            sys_prompt = custom_system_prompt
        else:
            sys_prompt = self.load_md_content(system_prompt_selector, current_dir)

        # 3. 構建 Prompt (要求模型輸出 JSON 格式以方便拆分，或者一次輸出三個段落)
        # 為了穩定性，我們要求模型輸出一個 JSON 字串
        full_prompt = (
            f"Please analyze the image and provide descriptions in three formats: "
            f"1. English, 2. Traditional Chinese (繁體中文), 3. Simplified Chinese (简体中文). "
            f"The output must be a pure JSON object with the following keys: "
            f'"en", "zh_tw", "zh_cn". Do not include markdown code blocks like ```json, just the JSON object.'
        )

        # 4. 呼叫 API
        url = f"{api_url.rstrip('/')}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "system",
                    "content": sys_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": full_prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        }
                    ]
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "chat_template_kwargs": {
                "enable_thinking": False
            },
            "seed": seed # 將 Seed 加入 API 請求以保證可重複性
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            res_json = response.json()
            
            # 取得內容
            content_str = res_json['choices'][0]['message']['content']
            
            # 嘗試解析 JSON (有時模型會多包一層 ```json ... ```)
            if "```json" in content_str:
                content_str = content_str.split("```json")[1].split("```")[0].strip()
            elif "```" in content_str:
                content_str = content_str.split("```")[1].split("```")[0].strip()
            
            data = json.loads(content_str)
            
            en_p = data.get("en", "")
            tw_p = data.get("zh_tw", "")
            cn_p = data.get("zh_cn", "")

            return (en_p, tw_p, cn_p)

        except Exception as e:
            print(f"Error calling API: {e}")
            # 如果失敗，回傳錯誤訊息作為結果，避免流程中斷
            error_msg = f"Error: {str(e)}"
            return (error_msg, error_msg, error_msg)

# 註冊節點
NODE_CLASS_MAPPINGS = {
    "ImageToMultiPrompt": ImageToMultiPromptNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageToMultiPrompt": "Image to Multi-Language Prompt (OpenAI API)"
}
