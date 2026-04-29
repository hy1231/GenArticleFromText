import os
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

def setup_env_and_proxy() -> str:
    load_dotenv()
    # 自动设置环境变量中的代理
    for p in ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"]:
        proxy = os.getenv(p, "").strip()
        if proxy:
            os.environ[p] = proxy

    api_key = os.getenv("GOOGLE_API_KEY", "").strip()
    if not api_key:
        print("❌ 未检测到 GOOGLE_API_KEY，请检查 .env 文件。")
        sys.exit(1)


    AI_MODEL_ID = os.getenv("AI_MODEL_ID")    
    return api_key,AI_MODEL_ID

def read_material() -> str:
    """直接读取本地 rawdata/materials.md"""
    input_path = Path("rawdata/materials.md")
    if not input_path.exists():
        print(f"❌ 找不到素材文件: {input_path.resolve()}")
        print("请手动创建 rawdata 文件夹并放入 materials.md。")
        sys.exit(1)

    content = input_path.read_text(encoding="utf-8").strip()
    if not content:
        print(f"⚠️ 素材文件为空，请先补充内容。")
        sys.exit(1)
    return content

def call_model(api_key: str,ai_model_id: str, material: str) -> str:
    """第一轮：基于素材生成公众号初稿"""
    client = genai.Client(api_key=api_key)

    # 这里直接写死你的写作人设
    system_prompt = """
    你是一位公众号主笔。
    你的任务是：根据用户提供的原始素材，撰写一篇微信公众号文章。
    
    【写作要求】：
    1. 标题：提供3个可选标题放在开头。
    2. 篇幅控制：全文严禁超过2000字，建议控制在1500字左右。
    3. 结构约束：
    - 开篇：吸引人，不超过200字。
    - 正文：分为3-5个核心段落，每个段落重点提炼素材，段落标题通俗易懂。
    - 结尾：总结升华，不超过150字。
    4. 语言风格：精炼干脆，删掉所有废话和过度的修辞。
    5. 使用漂亮的 Markdown 排版，适当使用图表。
    """
    
    user_prompt = f"以下是我的原始素材，请帮我写成文章：\n\n{material}"

    response = client.models.generate_content(
        model=ai_model_id, 
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.7,
        ),
    )
    return (response.text or "").strip()

def remove_ai_flavor(api_key: str, ai_model_id: str,draft: str) -> str:
    """第二轮：专门洗稿，增加“人味儿”"""
    client = genai.Client(api_key=api_key)

    editor_prompt = """
    你是一个拥有10年经验、的资深新媒体主编。
    你的唯一任务是：审阅我提供的初稿，适当消除其中的“AI味”，并输出最终排版好的纯文本。
    
    【洗稿核心军规】：
    1. 不要删除初稿中的任何信息点或细节，保持内容完整。
    2. 不要添加任何新的信息点或细节，保持内容纯净。
    3. 你可以调整句式、用词、段落结构等来去除AI生成的痕迹，但请确保不改变原意。
    4. 不要输出任何评价或分析，直接给我修改后的最终文章文本。
    """
    
    response = client.models.generate_content(
        model=ai_model_id, 
        contents=f"请把以下初稿里的‘AI味’洗掉，让它读起来更有张力：\n\n{draft}",
        config=types.GenerateContentConfig(
            system_instruction=editor_prompt,
            temperature=0.9, # 提高温度让表达更跳跃
        ),
    )
    return (response.text or "").strip()

def save_output(content: str, suffix: str, ts: str) -> Path:
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 文件名：article_时间戳_步骤.md
    output_path = output_dir / f"article_{ts}_{suffix}.md"
    output_path.write_text(content, encoding="utf-8")
    return output_path

def main() -> None:
    print("🚀 微信公众号自动化写作助手启动...")
    
    api_key,ai_model_id = setup_env_and_proxy()
    ts = datetime.now().strftime("%m%d_%H%M%S")

    # 1. 获取素材
    material = read_material()
    print(f"📖 已成功读取素材，长度：{len(material)} 字符")

    try:
        # 2. 生成初稿
        print("🧠 [1/2] 正在构建文章初稿...")
        draft = call_model(api_key,ai_model_id, material)
        save_output(draft, "draft", ts)
        print("✅ 初稿生成并已保存。")

        # 3. 润色去AI味
        print("🧽 [2/2] 主编正在进行‘去AI味’深度加工...")
        final_text = remove_ai_flavor(api_key,ai_model_id, draft)
        final_path = save_output(final_text, "final", ts)

        print("\n" + "="*40)
        print(f"🎉 任务圆满完成！")
        print(f"📍 最终成品请查看: {final_path.resolve()}")
        print("="*40)

    except Exception as e:
        print(f"❌ 运行过程中出现错误: {e}")

if __name__ == "__main__":
    main()