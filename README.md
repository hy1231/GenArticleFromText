# 微信公众号自动化写作助手

基于 Google AI (Gemini) 的微信公众号文章自动生成工具。

## 功能特点

- 📝 **自动写作**：根据提供的素材自动生成微信公众号文章
- 🎯 **传播力优化**：内置专业写作人设，生成极具传播力的内容
- 🤖 **去 AI 味**：两轮处理，第二轮专门消除 AI 生成痕迹，增加"人味儿"
- 📱 **移动优化**：自动生成适合手机阅读的短段落和精美排版

## 环境准备

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **配置 API Key**
   - 复制 `.env.example` 为 `.env`
   - 填入你的 Google API Key
   ```bash
   cp .env.example .env
   ```
   - 编辑 `.env` 文件，设置 `GOOGLE_API_KEY`

3. **准备素材**
   - 创建 `rawdata` 文件夹
   - 在其中放入 `materials.md` 文件作为写作素材

## 使用方法

直接运行主程序：

```bash
python main.py
```

程序会自动：
1. 读取 `rawdata/materials.md` 中的素材
2. 生成文章初稿并保存为 `output/article_时间戳_draft.md`
3. 进行"去 AI 味"润色，生成最终稿并保存为 `output/article_时间戳_final.md`

## 输出说明

程序会在 `output/` 目录下生成两个文件：
- `article_时间戳_draft.md` - 初稿
- `article_时间戳_final.md` - 最终成品

## 注意事项

- 需要有效的 Google API Key（访问 Gemini API）
- 如果需要使用代理，请在 `.env` 中配置 `HTTP_PROXY` 和 `HTTPS_PROXY`
- 确保 `rawdata/materials.md` 文件存在且不为空
