# 🚀 Advanced X & LinkedIn Post Generator

A powerful Streamlit-based application that transforms articles, videos, and notes into engaging X (Twitter) posts and LinkedIn content using AI. Supports multiple AI providers (OpenAI, Gemini, OpenRouter), news scraping from top tech sources, and integrated video parsing from YouTube and Instagram for seamless content generation.

## ✨ Features

- **AI-Powered Generation**: Create X posts in various styles (Educational, Conversational, Breaking News, Thought Leadership, etc.) and lengths (Short ~150-280 chars, Medium ~280-400 chars, Large ~400-550 chars, Article Threads).
- **LinkedIn Posts**: Generate professional, structured LinkedIn content with attention-grabbing hooks, key insights, actionable takeaways, and relevant hashtags.
- **News Discovery**: Automatically scrape and rank trending articles from Hacker News, Reddit (r/artificial, r/technology, etc.), TechCrunch, and VentureBeat based on keywords and timeframe.
- **Video Integration**: 
  - **YouTube Video Parser**: Extract video titles, descriptions, full transcripts (if available), and metadata. Generate posts directly from video content.
  - **Instagram Reel Parser**: Pull captions, engagement stats (likes, comments), and metadata from public Reels to inspire post content.
- **File Uploads**: Support for TXT, DOCX, and PDF files (up to 10 pages for PDFs, 10k chars limit).
- **Customizable Hooks**: Extensive categorized hook library (Learning & Tips, Why/Reasoning, Problem/Solution, Contrarian/Provocative, How-To/Process, Lists/Resources, Personal/Journey, Getting Started) with custom hook saving.
- **Virality Scoring**: AI-evaluated post potential with engagement tips, character counts, and quality checks.
- **Multiple AI Providers**: Seamless integration with OpenAI (GPT-4o, GPT-4o-mini), Google Gemini (1.5-flash, 1.5-pro), and OpenRouter (free models like DeepSeek, Llama; premium like Claude, Grok).
- **Content Analysis**: Pre-generation AI analysis for topic extraction, tone detection (Neutral/Positive/Negative), trending potential, accuracy, and key insights.

## 🛠️ Installation

1. Clone the repository:
   ```
   git clone <your-repo-url>
   cd x-post-generator
   ```

2. Install core dependencies:
   ```
   pip install -r requirements.txt
   ```

3. For full video support:
   - YouTube parsing is included (yt-dlp, youtube-transcript-api).
   - Instagram Reels: Ensure `instaloader` is installed (included in requirements).

## 🔧 Setup

1. **API Keys** (Required for generation):
   - **OpenAI**: Obtain from [OpenAI Platform](https://platform.openai.com/api-keys).
   - **Gemini**: Get from [Google AI Studio](https://aistudio.google.com/app/apikey).
   - **OpenRouter**: Register at [OpenRouter.ai](https://openrouter.ai) for free tier access.

2. Launch the app:
   ```
   streamlit run app.py
   ```
   Access at `http://localhost:8501`.

3. **Sidebar Configuration**:
   - Select API provider and model.
   - Enter API key (stored in session).
   - Choose post template, hook category/specific hook, length, and custom instructions.
   - Enable virality scoring and set variation count (1-3).

## 📖 Usage

### 1. Manual Content Input
- **Text/Files**: Paste content or upload TXT/DOCX/PDF files. Previews available for DOCX/PDF.
- **YouTube Videos**: Enter URL (e.g., `https://www.youtube.com/watch?v=...`). Parses title, description, transcript, and duration. Handles errors gracefully (e.g., no transcript available).
- **Instagram Reels**: Enter public Reel URL (e.g., `https://www.instagram.com/reel/...`). Extracts caption, likes, comments. Note: Private accounts not supported.
- Once loaded, click **Analyze Content** for AI insights (topic, tone, insights).
- Generate X posts or LinkedIn content with one click. Supports multiple variations.

### 2. News Discovery
- Enter keywords (e.g., "AI ethics, machine learning") – optional for all articles.
- Select sources (Hacker News, Reddit, TechCrunch, VentureBeat) and timeframe (24h to 14 days).
- Set max articles (5-50).
- Click **Find Trending News** to fetch, score, and display articles with previews.
- Generate posts directly from any article (auto-extracts content).

### 3. Generated Posts
- **X Posts Tab**: View/edit posts with metadata (template, hook, length). Includes virality score (1-10), engagement tips, and download as TXT.
- **LinkedIn Posts Tab**: Professional formats with hooks, numbered insights, takeaways, and 3-5 hashtags. Editable and downloadable.
- All posts adhere to rules: No emojis/hashtags in X posts; conversational tone; curiosity-driven.

### Example Workflow
1. Paste a YouTube URL or article text.
2. Select "Educational/Informative" template, "Learning & Tips" hook category.
3. Choose "Medium" length.
4. Click **Generate X Post** → Get 1-3 variations.
5. Review virality score and tips, then download/post.

## 📁 Project Structure

- `app.py`: Core Streamlit app with VideoParser class for YouTube/Instagram integration, post generation logic, and UI tabs.
- `news_scraper.py` : Scraping module for news sources with content extraction.
- `prompts.py` : Advanced prompt templates for X and LinkedIn generation (MEGA_PROMPT, SPECIFIC_PROMPTS, LINKEDIN_MEGA_PROMPT).
- `requirements.txt`: Lists all dependencies including video tools.
- `README.md`: This file.

## ⚠️ Limitations & Notes

- **Sensitive Content Filter**: Blocks posts with words like "hate", "violence", "illegal".
- **Video Parsing**:
  - YouTube: Transcripts unavailable for some videos; uses yt-dlp for metadata.
  - Instagram: Public accounts only; no private content access.
- **API Dependencies**: Generation requires valid API keys; free tiers have limits.
- **News Scraping**: Includes delays to respect sites; may miss paywalled content.
- **Content Limits**: Text truncated at 10k chars; PDFs to 10 pages.
- **No Production Deployment**: Designed for local development; add secrets management for APIs in production.
- **Platform Rules**: X posts avoid emojis/hashtags for authenticity; LinkedIn uses minimal emojis.

## 🤝 Contributing

1. Fork the repo.
2. Create a branch: `git checkout -b feature/video-enhancements`.
3. Commit changes: `git commit -m 'Enhance Instagram parsing'`.
4. Push: `git push origin feature/video-enhancements`.
5. Open a PR with details.

Issues, features, or bug reports welcome!

## 📄 License

MIT License – feel free to use, modify, and distribute.

## 🙏 Acknowledgments

- **Frameworks**: Streamlit for UI, OpenAI/Google/OpenRouter for AI.
- **Libraries**: yt-dlp & youtube-transcript-api (YouTube), instaloader (Instagram), BeautifulSoup/requests (scraping), python-docx/pypdf (files).
- **Inspiration**: Best practices from X/LinkedIn growth experts.
- **Sources**: Hacker News API, Reddit JSON, TechCrunch/VentureBeat RSS.

---

⭐ Star if helpful! Report issues or suggest features.