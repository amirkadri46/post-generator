import streamlit as st
import logging
import io
import json
import re
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass
import openai
import google.generativeai as genai
from docx import Document
from pypdf import PdfReader
from news_scraper import NewsScraperModule

# New imports for video parsing
try:
    import yt_dlp
    from youtube_transcript_api import YouTubeTranscriptApi  # type: ignore[import]
    YT_AVAILABLE = True
except ImportError:
    YT_AVAILABLE = False
    
try:
    import instaloader
    INSTA_AVAILABLE = True
except ImportError:
    INSTA_AVAILABLE = False

# Sensitive content check
SENSITIVE_WORDS = ["hate", "violence", "illegal", "offensive", "harm"]

# POST TEMPLATES
POST_TEMPLATES = {
    "Educational/Informative": "Break down complex topics into digestible insights with clear explanations",
    "Conversational": "Write as if speaking directly to a friend, casual and relatable",
    "Breaking News": "Urgent, immediate impact focus with what-just-happened energy",
    "Thought Leadership": "Authoritative insights with forward-looking industry implications",
    "Controversial/Provocative": "Challenge assumptions with contrarian takes and bold statements",
    "Story-Driven": "Use narrative and personal journey to illustrate points",
    "Funny/Witty": "Light-hearted, humorous take while delivering real value",
    "Motivational": "Inspire action with empowering and energizing language",
    "Technical Deep-Dive": "Detailed analysis for technically savvy audience",
    "Beginner-Friendly": "Simple explanations perfect for newcomers to the topic",
    "Custom": "Use your own custom template style"
}

# HOOK CATEGORIES
HOOK_CATEGORIES = {
    "Learning & Tips": [
        "5 tips I wish I knew earlier about [topic]",
        "The most important thing that I learned about [topic]",
        "5 dumbest mistakes I made in [topic]",
        "My worst mistake in [topic]",
        "Life lessons I learned from [topic]",
        "One tip that is going to change your life",
        "10 facts everyone should know about [topic]",
        "5 facts you didn't know about [topic]"
    ],
    "Why/Reasoning": [
        "Why [X] is better than [Y]",
        "Why you will not succeed at [task]",
        "Why you don't deserve success",
        "Why nobody loves your content",
        "Why original ideas suck",
        "Why people love [topic]",
        "Why learning [skill] takes so long",
        "Why is it hard to succeed in [area]"
    ],
    "Problem/Solution": [
        "What I hate about [topic]",
        "You don't need money to start [activity]",
        "You are wasting your time doing [activity]",
        "Why you are not good at [skill]",
        "Avoid these 5 mistakes in [topic]",
        "Stop doing this one mistake",
        "Debunk a common myth about [topic]",
        "Not many people know this about [topic]"
    ],
    "Contrarian/Provocative": [
        "Success is overrated",
        "Working hard is a mistake",
        "Quit [activity] if you are not creative",
        "Why you will not get better at [skill]",
        "Never break this one rule in [topic]",
        "Quantity vs Quality in [topic]",
        "[Platform] hates [your approach]",
        "5 facts people neglect about [topic]"
    ],
    "How-To/Process": [
        "How to be unique in [area]",
        "5 best tools for [activity]",
        "How I became successful in [area]",
        "How to work smart not hard in [topic]",
        "Step by step guide to [goal]",
        "How most people succeed in [area]",
        "Tools I use for [task]",
        "How to make people pay you for [service]"
    ],
    "Lists/Resources": [
        "My top 5 favorite [category]",
        "Where to start learning [skill]",
        "Top 5 apps to be better at [topic]",
        "Best websites to learn about [topic]",
        "5 books to become better at [skill]",
        "5 dos and don'ts about [topic]",
        "5 rules of success in [area]"
    ],
    "Personal/Journey": [
        "Talk about your motivation and struggles",
        "This is where I work at",
        "Before and after [change]",
        "What to expect when you start [activity]",
        "My journey so far with [topic]",
        "Talk about your struggles in the past",
        "Introduce yourself and your mission"
    ],
    "Getting Started": [
        "Easy way to start doing [activity]",
        "What you will need to start [activity]",
        "Read this if you are unsure about starting [activity]",
        "Follow this guide to succeed in [area]",
        "5 creative ways to make money with [skill]",
        "5 ways to become famous with [activity]"
    ]
}

POST_GENERATION_PROMPT = """Create an X post about {topic} with these specifications:

TEMPLATE STYLE: {template_style}
SELECTED HOOK: {selected_hook}
POST LENGTH: {post_length}

CONTENT SOURCE:
{content_source}

KEY INSIGHTS:
{key_insights}

ADDITIONAL INSTRUCTIONS:
{custom_instructions}

---

CORE RULES:
1. Use intermediate, conversational English - write like you're talking to a friend
2. NO emojis, NO hashtags
3. Create curiosity - make them want to know more
4. Be specific and concrete with examples
5. Every sentence should add value

POST LENGTH GUIDELINES:

SHORT (150-280 chars):
- Hook → One powerful insight → Curiosity gap
- Punchy and direct

MEDIUM (280-400 chars):
- Hook → Insight 1 with context → Insight 2 → What this means
- Build anticipation

LARGE (400-550 chars):
- Hook → Brief context → Insight 1 → Insight 2 → Insight 3 → Future implications
- Create momentum

THREAD (Multiple tweets):
Tweet 1: Hook + Setup (trigger curiosity/shock/value)
Tweets 2-5: Break down What → Why → Use cases → Implications
Final Tweet: Key takeaway + thought-provoking close

Format threads as:
1/6
[First tweet content]
---
2/6
[Second tweet content]
---
etc.

Generate the post now following the {template_style} style and using the hook naturally.
Output ONLY the post content."""

LINKEDIN_POST_PROMPT = """Create a LinkedIn post about {topic}:

TEMPLATE STYLE: {template_style}
CONTENT SOURCE: {content_source}
KEY INSIGHTS: {key_insights}

STRUCTURE:
1. HOOK (1-2 lines): Grab attention with professional intrigue
2. CONTEXT (2-4 lines): Set up why this matters
3. MAIN CONTENT (8-12 lines): Break down insights with clear formatting
4. TAKEAWAY (2-3 lines): Key learning + discussion prompt
5. HASHTAGS: 3-5 relevant tags

TONE: Professional but conversational, use "I" and "you" naturally

LENGTH: 1300-2000 characters

FORMATTING:
- Use line breaks generously
- Can use 1-2 emojis for emphasis
- Numbered lists or bullets for clarity

Generate the LinkedIn post now.
Output ONLY the post content with proper formatting."""


class VideoParser:
    """Handle YouTube and Instagram video parsing"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_youtube_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def parse_youtube_video(self, url: str) -> Dict:
        """Parse YouTube video and extract transcript/metadata"""
        if not YT_AVAILABLE:
            return {"error": "YouTube parsing libraries not installed. Run: pip install yt-dlp youtube-transcript-api"}
        
        video_id = self.extract_youtube_id(url)
        if not video_id:
            return {"error": "Invalid YouTube URL"}
        
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
            title = info.get('title', 'Unknown')
            description = info.get('description', '')
            duration = info.get('duration', 0)
            
            transcript_text = ""
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                transcript_text = " ".join([item['text'] for item in transcript_list])
            except Exception as e:
                self.logger.warning(f"Could not fetch transcript: {e}")
                transcript_text = "Transcript not available"
            
            full_content = f"""
VIDEO TITLE: {title}

VIDEO DESCRIPTION:
{description[:1000]}

VIDEO TRANSCRIPT:
{transcript_text[:5000]}

Duration: {duration // 60} minutes {duration % 60} seconds
            """.strip()
            
            return {
                "success": True,
                "title": title,
                "description": description,
                "transcript": transcript_text,
                "duration": duration,
                "content": full_content,
                "url": url
            }
            
        except Exception as e:
            self.logger.error(f"YouTube parsing error: {e}")
            return {"error": f"Failed to parse YouTube video: {str(e)}"}
    
    def extract_instagram_shortcode(self, url: str) -> Optional[str]:
        """Extract Instagram shortcode from URL"""
        patterns = [
            r'instagram\.com\/reel\/([A-Za-z0-9_-]+)',
            r'instagram\.com\/p\/([A-Za-z0-9_-]+)',
            r'instagram\.com\/tv\/([A-Za-z0-9_-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def parse_instagram_reel(self, url: str) -> Dict:
        """Parse Instagram Reel and extract metadata"""
        if not INSTA_AVAILABLE:
            return {"error": "Instagram parsing library not installed. Run: pip install instaloader"}
        
        shortcode = self.extract_instagram_shortcode(url)
        if not shortcode:
            return {"error": "Invalid Instagram URL. Use format: https://instagram.com/reel/SHORTCODE"}
        
        try:
            L = instaloader.Instaloader()
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            
            caption = post.caption or ""
            likes = post.likes
            comments = post.comments
            is_video = post.is_video
            
            if not is_video:
                return {"error": "This Instagram post is not a video/reel"}
            
            full_content = f"""
INSTAGRAM REEL

CAPTION:
{caption}

ENGAGEMENT:
Likes: {likes}
Comments: {comments}

URL: {url}
            """.strip()
            
            return {
                "success": True,
                "caption": caption,
                "likes": likes,
                "comments": comments,
                "content": full_content,
                "url": url
            }
            
        except Exception as e:
            self.logger.error(f"Instagram parsing error: {e}")
            return {"error": f"Failed to parse Instagram reel: {str(e)}. Note: Private accounts cannot be accessed."}


class XPostGeneratorApp:
    """Main application class for the Advanced X Post Generator"""

    SUPPORTED_TEXT_TYPES = {".txt", ".docx", ".pdf"}
    MAX_TEXT_LENGTH = 10000
    MAX_PDF_PAGES = 10
    
    LENGTH_OPTIONS = {
        "Short (~150-280 chars)": 280,
        "Medium (~280-400 chars)": 400,
        "Large (~400-550 chars)": 550,
        "Article Thread (Multiple tweets)": 0
    }
    
    API_OPTIONS = ["OpenAI", "Gemini", "OpenRouter"]
    OPENAI_MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
    GEMINI_MODELS = ["gemini-1.5-flash", "gemini-1.5-pro"]
    OPENROUTER_MODELS = [
        "deepseek/deepseek-chat-v3-0324:free",
        "deepseek/deepseek-r1:free",
        "deepseek/deepseek-chat-v3.1:free",
        "meta-llama/llama-3.1-8b-instruct:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "mistralai/mistral-7b-instruct:free",
        "google/gemini-2.0-flash-exp:free",
        "qwen/qwen-2.5-7b-instruct:free",
        "x-ai/grok-4-fast:free",
        "openai/gpt-4o-mini",
        "openai/gpt-4o",
        "anthropic/claude-sonnet-4.5",
        "deepseek/deepseek-chat",
        "x-ai/grok-4-fast"
    ]

    def __init__(self):
        """Initialize the application"""
        self._setup_logging()
        self._setup_page_config()
        self._initialize_session_state()
        self.news_scraper = NewsScraperModule()
        self.video_parser = VideoParser()

    def _setup_logging(self):
        logging.basicConfig(level=logging.ERROR)
        self.logger = logging.getLogger(__name__)
        if "error_logs" not in st.session_state:
            st.session_state.error_logs = []

    def _setup_page_config(self):
        st.set_page_config(
            page_title="Advanced X Post Generator",
            page_icon="🚀",
            layout="wide"
        )

    def _initialize_session_state(self):
        """Initialize all session state variables"""
        defaults = {
            "api_key": "",
            "api_provider": "OpenAI",
            "model": "gpt-4o-mini",
            "post_template": "Educational/Informative",
            "custom_template_text": "",
            "hook_category": "Auto-Select Best Hook",
            "specific_hook": "Auto-Select Best Hook",
            "custom_hook_text": "",
            "saved_custom_hooks": [],
            "length": "Medium (~280-400 chars)",
            "custom_instructions": "",
            "virality_enabled": True,
            "generated_posts": [],
            "enhanced_posts": [],
            "content_analysis": None,
            "num_variations": 1,
            "trending_articles": [],
            "selected_articles": [],
            "linkedin_posts": [],
            "manual_input_content": "",
            "video_content": None,
            "video_analysis": None
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    def handle_file_uploads(self, files) -> str:
        """Process uploaded text files and return combined content"""
        if not files:
            return ""
            
        texts = []
        for file in files:
            ext = Path(file.name).suffix.lower()
            try:
                if ext == ".txt":
                    text = file.getvalue().decode("utf-8", errors="ignore")
                    texts.append(f"{file.name}:\n{text}")
                    with st.expander(f"Preview: {file.name}"):
                        st.text(text[:2000])

                elif ext == ".docx":
                    doc = Document(io.BytesIO(file.getvalue()))
                    text = "\n".join(p.text for p in doc.paragraphs)
                    texts.append(f"{file.name}:\n{text}")
                    with st.expander(f"Preview: {file.name}"):
                        st.text(text[:2000])

                elif ext == ".pdf":
                    reader = PdfReader(io.BytesIO(file.getvalue()))
                    pages_text = [page.extract_text() or "" for page in reader.pages[:self.MAX_PDF_PAGES]]
                    text = "\n".join(pages_text)
                    texts.append(f"{file.name}:\n{text}")
                    st.caption(f"PDF: {file.name} ({min(len(reader.pages), self.MAX_PDF_PAGES)} pages)")

            except Exception as e:
                self.logger.error(f"Error handling file {file.name}: {e}")
                st.warning(f"Could not process {file.name}")

        text_blob = "\n\n".join(texts)
        
        if len(text_blob) > self.MAX_TEXT_LENGTH:
            text_blob = text_blob[:self.MAX_TEXT_LENGTH] + "\n[Content truncated]"
            st.warning("Content truncated to processing limits.")
            
        return text_blob

    def setup_api(self, api_key: str, provider: str, model: str):
        """Setup API client based on provider and model"""
        if not api_key:
            st.error(f"{provider} API key required.")
            return None

        try:
            if provider == "OpenAI":
                client = openai.OpenAI(api_key=api_key)
                return {"type": "openai", "model": model, "client": client}
                
            elif provider == "Gemini":
                genai.configure(api_key=api_key)
                return genai.GenerativeModel(model)
                
            elif provider == "OpenRouter":
                client = openai.OpenAI(
                    api_key=api_key,
                    base_url="https://openrouter.ai/api/v1"
                )
                return {"type": "openrouter", "model": model, "client": client}
                
        except Exception as e:
            st.error(f"API setup failed: {str(e)}")
            self.logger.error(f"API setup error: {e}")
            
        return None

    def analyze_content(self, content: str, api_config) -> Dict:
        """Analyze input content using API"""
        if not content or not content.strip():
            return {"error": "No content provided."}

        if any(word in content.lower() for word in SENSITIVE_WORDS):
            return {"error": "Content contains sensitive topics. Please revise."}

        if len(content) < 100:
            return {
                "topic": "Brief content",
                "insights": ["Consider adding more detail for better analysis"],
                "tone": "Neutral",
                "trending": "Low",
                "accuracy": "Medium"
            }

        analysis_prompt = f"""
Analyze this content and respond with valid JSON only:

{{
    "topic": "Main topic or theme",
    "insights": ["Key insight 1", "Key insight 2", "Key insight 3"],
    "tone": "Neutral/Positive/Negative/Emotional",
    "trending": "High/Medium/Low",
    "accuracy": "High/Medium/Low"
}}

Content: {content[:2000]}
"""
        
        try:
            if isinstance(api_config, dict) and api_config.get("type") in ["openai", "openrouter"]:
                client = api_config.get("client")
                response = client.chat.completions.create(
                    model=api_config.get("model", "gpt-4o-mini"),
                    messages=[
                        {"role": "system", "content": "You are a JSON generator. Return only valid JSON."},
                        {"role": "user", "content": analysis_prompt}
                    ],
                    temperature=0.1,
                    max_tokens=500,
                    response_format={"type": "json_object"}
                )
                analysis_text = response.choices[0].message.content
            else:
                response = api_config.generate_content(analysis_prompt)
                analysis_text = response.text

            analysis_text = analysis_text.strip().replace("```json", "").replace("```", "")
            analysis = json.loads(analysis_text)
            
            if not isinstance(analysis.get("insights"), list):
                analysis["insights"] = [str(analysis.get("insights", ""))] if analysis.get("insights") else []
                
            return analysis
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parse error: {e}")
            return {
                "topic": "General Topic",
                "insights": ["Unable to extract detailed insights"],
                "tone": "Neutral",
                "trending": "Medium",
                "accuracy": "Medium"
            }
        except Exception as e:
            self.logger.error(f"Analysis error: {e}")
            return {"error": f"Analysis failed: {str(e)}"}

    def generate_post(self, content: str, api_config, analysis: Dict, variation_num: int = 1) -> Dict:
        """Generate X post using template system"""
        if analysis is None or not isinstance(analysis, dict):
            return {"error": "Valid analysis is required"}
            
        if "error" in analysis:
            return {"error": f"Cannot generate: {analysis['error']}"}

        if any(word in content.lower() for word in SENSITIVE_WORDS):
            return {"error": "Content contains sensitive topics."}

        if len(content) < 50:
            return {"warning": "Content too short for meaningful post."}

        # Get configuration
        template_style = st.session_state.get("post_template", "Educational/Informative")
        if template_style == "Custom":
            template_style = st.session_state.get("custom_template_text", "Professional and engaging")
        
        hook_category = st.session_state.get("hook_category", "Auto-Select Best Hook")
        specific_hook = st.session_state.get("specific_hook", "Auto-Select Best Hook")
        length = st.session_state.get("length", "Medium (~280-400 chars)")
        custom_instructions = st.session_state.get("custom_instructions", "")
        
        # Handle custom hook
        if specific_hook == "Use Custom Hook":
            selected_hook = st.session_state.get("custom_hook_text", "Start with an engaging hook")
        elif specific_hook not in ["Auto-Select Best Hook", "Let AI Choose"]:
            selected_hook = specific_hook
        elif hook_category != "Auto-Select Best Hook":
            hooks = HOOK_CATEGORIES[hook_category]
            selected_hook = f"Choose the best hook from {hook_category} category"
        else:
            hook_instructions = [
                "Auto-select the BEST hook from Learning & Tips or Why/Reasoning categories",
                "Auto-select the BEST hook from Problem/Solution or How-To categories", 
                "Auto-select the BEST hook from Contrarian/Provocative or Personal/Journey categories"
            ]
            selected_hook = hook_instructions[min(variation_num - 1, len(hook_instructions) - 1)]
        
        if variation_num > 1:
            selected_hook += f" (VARIATION {variation_num} - must be DIFFERENT)"
        
        # Determine post length
        length_map = {
            "Short (~150-280 chars)": "SHORT (150-280 chars)",
            "Medium (~280-400 chars)": "MEDIUM (280-400 chars)",
            "Large (~400-550 chars)": "LARGE (400-550 chars)",
            "Article Thread (Multiple tweets)": "THREAD (Multiple tweets)"
        }
        post_length = length_map.get(length, "MEDIUM (280-400 chars)")
        is_thread = length == "Article Thread (Multiple tweets)"
        max_chars = self.LENGTH_OPTIONS[length]
        
        key_insights = "\n".join([f"• {insight}" for insight in analysis.get('insights', [])]) or "Key points from content"
        
        prompt = POST_GENERATION_PROMPT.format(
            topic=analysis.get('topic', 'the provided content'),
            template_style=template_style,
            selected_hook=selected_hook,
            post_length=post_length,
            content_source=content[:3000],
            key_insights=key_insights,
            custom_instructions=custom_instructions or "None"
        )
        
        try:
            temperature = 0.8 + (variation_num - 1) * 0.05
            
            if isinstance(api_config, dict) and api_config.get("type") in ["openai", "openrouter"]:
                client = api_config.get("client")
                response = client.chat.completions.create(
                    model=api_config.get("model", "gpt-4o-mini"),
                    messages=[{"role": "user", "content": prompt}],
                    temperature=min(temperature, 1.0),
                    max_tokens=2000 if is_thread else 600
                )
                post_content = response.choices[0].message.content.strip()
            else:
                response = api_config.generate_content(prompt)
                post_content = response.text.strip()

            first_line = post_content.split('\n')[0][:100]
            hook_used = first_line if len(first_line) > 10 else "Custom hook"
            char_count = len(post_content)

            tips = [
                "Post during peak hours (8-10am, 5-7pm)",
                "Ask questions to encourage replies",
                "Use clear, action-oriented language"
            ]
            if analysis.get("trending") == "High":
                tips.append("Leverage trending topics for visibility")

            return {
                "template": template_style,
                "hook_category": hook_category,
                "length_type": length,
                "max_chars": max_chars if not is_thread else None,
                "char_count": f"~{char_count} chars" + (f"/{max_chars}" if not is_thread else ""),
                "content": post_content,
                "engagement_tips": tips,
                "quality_check": "Ready to post",
                "hook_used": hook_used,
                "variation": variation_num
            }
            
        except Exception as e:
            self.logger.error(f"Generation error: {e}")
            return {"error": f"Generation failed: {str(e)}"}

    def generate_linkedin_post(self, content: str, analysis: Dict) -> Dict:
        """Generate LinkedIn post"""
        if analysis is None or not isinstance(analysis, dict):
            return {"error": "Valid analysis is required"}
            
        if "error" in analysis:
            return {"error": f"Cannot generate: {analysis['error']}"}
        
        if any(word in content.lower() for word in SENSITIVE_WORDS):
            return {"error": "Content contains sensitive topics."}
        
        template_style = st.session_state.get("post_template", "Educational/Informative")
        if template_style == "Custom":
            template_style = st.session_state.get("custom_template_text", "Professional and engaging")
        
        key_insights = "\n".join([f"• {insight}" for insight in analysis.get('insights', [])]) or "Key points from content"
        
        prompt = LINKEDIN_POST_PROMPT.format(
            topic=analysis.get('topic', 'the provided content'),
            template_style=template_style,
            content_source=content[:3000],
            key_insights=key_insights
        )
        
        try:
            if isinstance(st.session_state.api_client, dict) and st.session_state.api_client.get("type") in ["openai", "openrouter"]:
                client = st.session_state.api_client.get("client")
                response = client.chat.completions.create(
                    model=st.session_state.api_client.get("model", "gpt-4o-mini"),
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=1500
                )
                post_content = response.choices[0].message.content.strip()
            else:
                response = st.session_state.api_client.generate_content(prompt)
                post_content = response.text.strip()
            
            char_count = len(post_content)
            
            return {
                "content": post_content,
                "char_count": f"~{char_count} characters",
                "platform": "LinkedIn",
                "template": template_style,
                "quality_check": "Ready to post"
            }
            
        except Exception as e:
            self.logger.error(f"LinkedIn generation error: {e}")
            return {"error": f"Generation failed: {str(e)}"}

    def _evaluate_virality(self, post_text: str, post_type: str = "") -> Dict:
        """Evaluate post's virality potential"""
        score = 5
        explanation_parts = []
        suggestions = []

        char_len = len(post_text)
        
        if char_len < 150:
            score += 1
            explanation_parts.append("Concise length favors engagement")
        elif 150 <= char_len <= 280:
            score += 2
            explanation_parts.append("Optimal length for X platform")
        else:
            suggestions.append("Consider shortening for better readability")

        start = post_text.lower()[:50]
        hooks = ["the one", "how to", "why", "what if", "?", "this changed", "unlock"]
        if any(h in start for h in hooks):
            score += 2
            explanation_parts.append("Strong opening hook captures attention")
        else:
            suggestions.append("Add a question or curiosity gap at the start")

        tech_keywords = ["ai", "tech", "innovation", "future", "model", "feature"]
        if sum(1 for kw in tech_keywords if kw in post_text.lower()) >= 2:
            score += 2
            explanation_parts.append("Strong tech/AI relevance engages target audience")
        else:
            suggestions.append("Include trending tech keywords")

        if any(fmt in post_type.lower() for fmt in ["thread", "educational"]):
            score += 1
            explanation_parts.append("Format supports shareability")

        score = min(10, max(1, score))
        
        return {
            "score": score,
            "explanation": "; ".join(explanation_parts) or "Moderate viral potential",
            "suggestions": suggestions or ["Post looks ready to share!"]
        }

    def render_sidebar(self):
        """Render the sidebar with configuration"""
        with st.sidebar:
            st.header("⚙️ Configuration")
            
            # API Configuration
            api_provider = st.selectbox(
                "API Provider", 
                self.API_OPTIONS, 
                index=self.API_OPTIONS.index(st.session_state.api_provider)
            )
            
            if api_provider != st.session_state.api_provider:
                st.session_state.api_provider = api_provider
                st.session_state.api_key = ""
                st.session_state.model = self._get_default_model(api_provider)

            models = {
                "OpenAI": self.OPENAI_MODELS,
                "Gemini": self.GEMINI_MODELS,
                "OpenRouter": self.OPENROUTER_MODELS
            }[api_provider]
            
            if api_provider == "OpenRouter":
                st.markdown("**Model Selection**")
                model_type = st.radio(
                    "Model Type",
                    ["Free Models", "Premium Models"],
                    horizontal=True
                )
                
                if model_type == "Free Models":
                    available_models = [m for m in models if ":free" in m]
                else:
                    available_models = [m for m in models if ":free" not in m]
            else:
                available_models = models
            
            model_idx = available_models.index(st.session_state.model) if st.session_state.model in available_models else 0
            model = st.selectbox("Model", available_models, index=model_idx)
            st.session_state.model = model

            api_key = st.text_input(
                "API Key",
                value=st.session_state.api_key,
                type="password"
            )
            st.session_state.api_key = api_key

            if api_key:
                api_client = self.setup_api(api_key, api_provider, model)
                if api_client:
                    st.success(f"✅ {api_provider} ready!")
                    st.session_state.api_client = api_client

            st.divider()
            
            # POST CONFIGURATION
            st.subheader("📝 Post Configuration")
            
            # Template Selection
            st.session_state.post_template = st.selectbox(
                "Writing Style/Template",
                list(POST_TEMPLATES.keys()),
                index=list(POST_TEMPLATES.keys()).index(st.session_state.get("post_template", "Educational/Informative"))
            )
            
            # Custom template input
            if st.session_state.post_template == "Custom":
                st.session_state.custom_template_text = st.text_input(
                    "Enter your custom template style:",
                    value=st.session_state.get("custom_template_text", ""),
                    placeholder="e.g., Bold and controversial with data-driven insights"
                )
            else:
                with st.expander("ℹ️ Template Description", expanded=False):
                    st.caption(POST_TEMPLATES[st.session_state.post_template])
            
            # Hook Category Selection
            st.session_state.hook_category = st.selectbox(
                "Hook Category",
                ["Auto-Select Best Hook"] + list(HOOK_CATEGORIES.keys()),
                index=0
            )
            
            # Specific Hook Selection
            if st.session_state.hook_category != "Auto-Select Best Hook":
                hooks = HOOK_CATEGORIES[st.session_state.hook_category]
                hook_options = ["Let AI Choose", "Use Custom Hook"] + hooks
                st.session_state.specific_hook = st.selectbox(
                    "Specific Hook",
                    hook_options,
                    index=0
                )
                
                # Custom hook input
                if st.session_state.specific_hook == "Use Custom Hook":
                    st.session_state.custom_hook_text = st.text_area(
                        "Enter your custom hook:",
                        value=st.session_state.get("custom_hook_text", ""),
                        height=60,
                        placeholder="e.g., Here's what nobody tells you about..."
                    )
                    
                    # Save custom hook option
                    if st.session_state.custom_hook_text and st.button("💾 Save Hook"):
                        if st.session_state.custom_hook_text not in st.session_state.saved_custom_hooks:
                            st.session_state.saved_custom_hooks.append(st.session_state.custom_hook_text)
                            st.success("Hook saved!")
                    
                    # Show saved hooks
                    if st.session_state.saved_custom_hooks:
                        with st.expander("📚 Saved Custom Hooks", expanded=False):
                            for idx, saved_hook in enumerate(st.session_state.saved_custom_hooks):
                                col1, col2 = st.columns([4, 1])
                                with col1:
                                    st.caption(f"{idx+1}. {saved_hook}")
                                with col2:
                                    if st.button("Use", key=f"use_hook_{idx}"):
                                        st.session_state.custom_hook_text = saved_hook
                                        st.rerun()
            else:
                st.session_state.specific_hook = "Auto-Select Best Hook"
            
            # Show selected hook info
            if st.session_state.specific_hook not in ["Auto-Select Best Hook", "Let AI Choose", "Use Custom Hook"]:
                st.info(f"🎯 Using: {st.session_state.specific_hook}")
            
            # Length Selection
            st.session_state.length = st.selectbox(
                "Post Length",
                list(self.LENGTH_OPTIONS.keys()),
                index=list(self.LENGTH_OPTIONS.keys()).index(
                    st.session_state.get("length", "Medium (~280-400 chars)")
                )
            )
            
            # Custom Instructions
            with st.expander("✏️ Custom Instructions (Optional)", expanded=False):
                st.session_state.custom_instructions = st.text_area(
                    "Additional preferences:",
                    value=st.session_state.get("custom_instructions", ""),
                    height=80,
                    placeholder="e.g., Focus on beginners, Include statistics, etc."
                )
            
            st.divider()
            
            # Additional Options
            st.subheader("⚡ Additional Options")
            
            st.session_state.num_variations = st.slider(
                "Variations to Generate", 
                1, 3, 
                st.session_state.get("num_variations", 1)
            )
            
            st.session_state.virality_enabled = st.checkbox(
                "Show Virality Score", 
                value=st.session_state.get("virality_enabled", True)
            )

            st.divider()
            
            if st.button("🔄 Reset All Settings", type="secondary"):
                keys_to_keep = ['api_key', 'api_provider', 'model']
                for key in list(st.session_state.keys()):
                    if key not in keys_to_keep:
                        del st.session_state[key]
                st.rerun()

    def _get_default_model(self, provider: str) -> str:
        return {
            "OpenAI": "gpt-4o-mini",
            "Gemini": "gemini-1.5-flash",
            "OpenRouter": "deepseek/deepseek-chat-v3-0324:free"
        }.get(provider, "gpt-4o-mini")

    def render_main_content(self):
        """Render the main application content"""
        st.title("🚀 Advanced X & LinkedIn Post Generator")
        st.markdown("Transform content into engaging posts with AI-powered generation")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("X Posts Generated", len(st.session_state.generated_posts))
        with col2:
            st.metric("LinkedIn Posts", len(st.session_state.linkedin_posts))
        with col3:
            st.metric("Articles Found", len(st.session_state.get("trending_articles", [])))
        with col4:
            api_status = "Connected" if hasattr(st.session_state, 'api_client') else "Not Connected"
            st.metric("API Status", api_status)

        st.divider()

        tabs = st.tabs(["📝 Manual Input", "🔍 News Discovery", "🐦 X Posts", "💼 LinkedIn Posts"])
        
        with tabs[0]:
            self._render_manual_input()
        
        with tabs[1]:
            self._render_news_discovery()
        
        with tabs[2]:
            self._render_x_posts()
        
        with tabs[3]:
            self._render_linkedin_posts()

    def _render_manual_input(self):
        """Manual content input interface with video support"""
        st.subheader("📝 Manual Content Input")
        
        input_type = st.radio(
            "Select Input Type:",
            ["Text/Files", "YouTube Video", "Instagram Reel"],
            horizontal=True
        )
        
        st.divider()
        
        if input_type == "Text/Files":
            col1, col2 = st.columns([3, 1])

            with col1:
                user_content = st.text_area(
                    "Paste your article, blog, or notes",
                    height=300,
                    placeholder="Enter content to transform into posts...",
                    key="manual_content"
                )

            with col2:
                st.markdown("**📎 Upload Files**")
                uploaded_files = st.file_uploader(
                    "Upload (TXT, DOCX, PDF)",
                    type=list(self.SUPPORTED_TEXT_TYPES),
                    accept_multiple_files=True,
                    key="manual_files"
                )
                file_content = self.handle_file_uploads(uploaded_files)

            full_content = (user_content + "\n\n" + file_content).strip()
            
            if full_content:
                st.session_state.manual_input_content = full_content
                st.session_state.video_content = None
                st.success(f"✅ Content loaded ({len(full_content)} characters)")
        
        elif input_type == "YouTube Video":
            if not YT_AVAILABLE:
                st.error("❌ YouTube parsing not available. Install required packages:")
                st.code("pip install yt-dlp youtube-transcript-api")
                return
            
            st.markdown("### 🎥 YouTube Video Parser")
            
            youtube_url = st.text_input(
                "YouTube URL",
                placeholder="https://www.youtube.com/watch?v=...",
                key="youtube_url"
            )
            
            if st.button("🔍 Parse Video", type="primary"):
                if youtube_url:
                    with st.spinner("Parsing YouTube video..."):
                        result = self.video_parser.parse_youtube_video(youtube_url)
                        
                        if "error" in result:
                            st.error(f"❌ {result['error']}")
                        else:
                            st.success(f"✅ Successfully parsed: {result['title']}")
                            st.session_state.video_content = result
                            st.session_state.manual_input_content = result['content']
                            
                            with st.expander("📹 Video Information", expanded=True):
                                st.markdown(f"**Title:** {result['title']}")
                                st.markdown(f"**Duration:** {result['duration'] // 60}:{result['duration'] % 60:02d}")
                                
                                if result.get('description'):
                                    st.markdown("**Description:**")
                                    st.text(result['description'][:500])
                                
                                if result.get('transcript') and result['transcript'] != "Transcript not available":
                                    st.markdown("**Transcript Preview:**")
                                    st.text(result['transcript'][:1000] + "...")
        
        elif input_type == "Instagram Reel":
            if not INSTA_AVAILABLE:
                st.error("❌ Instagram parsing not available. Install required package:")
                st.code("pip install instaloader")
                return
            
            st.markdown("### 📸 Instagram Reel Parser")
            st.warning("⚠️ Note: Private accounts may not be accessible")
            
            insta_url = st.text_input(
                "Instagram Reel URL",
                placeholder="https://www.instagram.com/reel/...",
                key="insta_url"
            )
            
            if st.button("🔍 Parse Reel", type="primary"):
                if insta_url:
                    with st.spinner("Parsing Instagram Reel..."):
                        result = self.video_parser.parse_instagram_reel(insta_url)
                        
                        if "error" in result:
                            st.error(f"❌ {result['error']}")
                        else:
                            st.success("✅ Successfully parsed Instagram Reel")
                            st.session_state.video_content = result
                            st.session_state.manual_input_content = result['content']
                            
                            with st.expander("📱 Reel Information", expanded=True):
                                st.markdown("**Caption:**")
                                st.text(result['caption'][:500] if result['caption'] else "No caption")
                                st.markdown(f"**Engagement:**")
                                st.markdown(f"- Likes: {result['likes']}")
                                st.markdown(f"- Comments: {result['comments']}")
        
        # Action buttons if content exists
        if st.session_state.get("manual_input_content"):
            st.divider()
            
            st.markdown("#### 📋 Current Configuration")
            col_cfg1, col_cfg2, col_cfg3 = st.columns(3)
            with col_cfg1:
                template_display = st.session_state.get("post_template", "Educational")
                if template_display == "Custom":
                    template_display = "Custom: " + st.session_state.get("custom_template_text", "")[:20]
                st.metric("Template", template_display)
            with col_cfg2:
                hook_display = st.session_state.get("specific_hook", "Auto")
                if hook_display == "Use Custom Hook":
                    hook_display = "Custom: " + st.session_state.get("custom_hook_text", "")[:20]
                elif hook_display in ["Auto-Select Best Hook", "Let AI Choose"]:
                    hook_display = st.session_state.get("hook_category", "Auto")
                st.metric("Hook", hook_display[:25] + "..." if len(hook_display) > 25 else hook_display)
            with col_cfg3:
                st.metric("Length", st.session_state.get("length", "Medium").split("(")[0].strip())
            
            st.divider()
            
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            
            with col_btn1:
                if st.button("📊 Analyze Content", type="secondary", use_container_width=True):
                    if not hasattr(st.session_state, 'api_client'):
                        st.error("⚠️ Configure API in sidebar first")
                    else:
                        with st.spinner("Analyzing content..."):
                            analysis = self.analyze_content(
                                st.session_state.manual_input_content, 
                                st.session_state.api_client
                            )
                            st.session_state.video_analysis = analysis
                            
                            if "error" not in analysis:
                                st.success("✅ Analysis complete!")
                                with st.expander("📊 Analysis Results", expanded=True):
                                    col_a1, col_a2 = st.columns(2)
                                    with col_a1:
                                        st.metric("Topic", analysis.get("topic", "N/A"))
                                        st.metric("Tone", analysis.get("tone", "N/A"))
                                    with col_a2:
                                        st.metric("Trending", analysis.get("trending", "N/A"))
                                        st.metric("Accuracy", analysis.get("accuracy", "N/A"))
                                    
                                    st.markdown("**Key Insights:**")
                                    for insight in analysis.get("insights", []):
                                        st.markdown(f"- {insight}")
                            else:
                                st.error(f"❌ {analysis['error']}")
            
            with col_btn2:
                if st.button("🐦 Generate X Post", type="primary", use_container_width=True):
                    if not hasattr(st.session_state, 'api_client'):
                        st.error("⚠️ Configure API in sidebar first")
                    else:
                        with st.spinner("Analyzing and generating..."):
                            analysis = self.analyze_content(
                                st.session_state.manual_input_content, 
                                st.session_state.api_client
                            )
                            st.session_state.content_analysis = analysis
                            
                            if "error" not in analysis:
                                num_vars = st.session_state.get("num_variations", 1)
                                for i in range(num_vars):
                                    post = self.generate_post(
                                        st.session_state.manual_input_content, 
                                        st.session_state.api_client, 
                                        analysis, 
                                        i + 1
                                    )
                                    if "error" not in post:
                                        if st.session_state.get("video_content"):
                                            post["source_video"] = st.session_state.video_content.get("title") or "Video content"
                                        st.session_state.generated_posts.append(post)
                                
                                if st.session_state.generated_posts:
                                    st.success(f"✅ Generated {num_vars} post(s)! Check 'X Posts' tab")
                                    st.rerun()
                            else:
                                st.error(f"❌ {analysis['error']}")
            
            with col_btn3:
                if st.button("💼 Generate LinkedIn Post", type="primary", use_container_width=True):
                    if not hasattr(st.session_state, 'api_client'):
                        st.error("⚠️ Configure API in sidebar first")
                    else:
                        with st.spinner("Generating LinkedIn post..."):
                            analysis = self.analyze_content(
                                st.session_state.manual_input_content, 
                                st.session_state.api_client
                            )
                            
                            if "error" not in analysis:
                                post = self.generate_linkedin_post(st.session_state.manual_input_content, analysis)
                                if "error" not in post:
                                    if st.session_state.get("video_content"):
                                        post["source_video"] = st.session_state.video_content.get("title") or "Video content"
                                    st.session_state.linkedin_posts.append(post)
                                    st.success("✅ LinkedIn post generated! Check 'LinkedIn Posts' tab")
                                    st.rerun()
                                else:
                                    st.error(f"❌ {post['error']}")
                            else:
                                st.error(f"❌ {analysis['error']}")

    def _render_news_discovery(self):
        """News discovery and scraping interface"""
        st.subheader("🔍 Automated News Discovery")
        
        col1, col2 = st.columns(2)
        
        with col1:
            keywords = st.text_input(
                "Keywords (comma-separated) - Optional",
                placeholder="AI, GPT, machine learning",
                key="news_keywords"
            )
            
            sources = st.multiselect(
                "News Sources",
                ["Hacker News", "Reddit", "TechCrunch", "VentureBeat"],
                default=["Hacker News", "TechCrunch"],
                key="news_sources"
            )
        
        with col2:
            timeframe_map = {
                "Last 24 hours": 1,
                "Last 3 days": 3,
                "Last 7 days": 7,
                "Last 14 days": 14
            }
            timeframe_label = st.selectbox(
                "Time Range",
                list(timeframe_map.keys()),
                index=1
            )
            timeframe_days = timeframe_map[timeframe_label]
            
            max_articles = st.slider("Max Articles", 5, 50, 20)
        
        if st.button("🔍 Find Trending News", type="primary"):
            if not sources:
                st.error("Please select at least one news source")
            else:
                with st.spinner("Searching..."):
                    try:
                        articles = self.news_scraper.fetch_all_news(
                            keywords=keywords.strip() if keywords else "",
                            timeframe_days=timeframe_days,
                            sources=sources
                        )
                        
                        st.session_state.trending_articles = articles[:max_articles]
                        
                        if articles:
                            st.success(f"✅ Found {len(st.session_state.trending_articles)} articles!")
                        else:
                            st.warning("⚠️ No articles found")
                            
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        if st.session_state.get("trending_articles"):
            st.markdown("---")
            st.markdown("### 📰 Trending Articles")
            
            for idx, article in enumerate(st.session_state.trending_articles[:20]):
                with st.expander(
                    f"⭐ {article.get('score', 0)} | {article['title'][:80]}",
                    expanded=idx < 3
                ):
                    col_info, col_actions = st.columns([3, 1])
                    
                    with col_info:
                        st.markdown(f"**{article['title']}**")
                        st.caption(f"📰 {article['source']} | 📅 {article['date']}")
                        st.markdown(f"[🔗 Read Article]({article['url']})")
                    
                    with col_actions:
                        if st.button("🐦 X Post", key=f"x_{idx}", use_container_width=True):
                            self._generate_from_article(article, "X")
                        
                        if st.button("💼 LinkedIn", key=f"li_{idx}", use_container_width=True):
                            self._generate_from_article(article, "LinkedIn")

    def _generate_from_article(self, article: Dict, platform: str):
        """Generate post from selected article"""
        if not hasattr(st.session_state, 'api_client'):
            st.error("⚠️ Configure API in sidebar first")
            return
        
        with st.spinner(f"Generating {platform} post..."):
            try:
                content = self.news_scraper.extract_article_content(article['url'])
                
                if not content:
                    content = f"Title: {article['title']}\nSource: {article['source']}"
                
                analysis = self.analyze_content(content, st.session_state.api_client)
                
                if "error" in analysis:
                    st.error(f"Analysis failed: {analysis['error']}")
                    return
                
                if platform == "X":
                    post = self.generate_post(content, st.session_state.api_client, analysis, 1)
                    if "error" not in post:
                        post["source_article"] = article['title']
                        st.session_state.generated_posts.append(post)
                        st.success("✅ X post generated!")
                        st.rerun()
                else:
                    post = self.generate_linkedin_post(content, analysis)
                    if "error" not in post:
                        post["source_article"] = article['title']
                        st.session_state.linkedin_posts.append(post)
                        st.success("✅ LinkedIn post generated!")
                        st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")

    def _render_x_posts(self):
        """X post display"""
        st.subheader("🐦 X Post Generator")
        
        if not st.session_state.generated_posts:
            st.info("💡 Generate posts in 'Manual Input' or 'News Discovery' tabs")
            return
        
        if st.session_state.get("content_analysis"):
            st.markdown("#### 📊 Content Analysis")
            analysis = st.session_state.content_analysis
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Topic", analysis.get("topic", "N/A"))
                st.metric("Tone", analysis.get("tone", "N/A"))
            with col_b:
                st.metric("Insights", len(analysis.get("insights", [])))
                st.metric("Trending", analysis.get("trending", "N/A"))
        
        self._display_generated_posts()

    def _render_linkedin_posts(self):
        """LinkedIn post display"""
        st.subheader("💼 LinkedIn Post Generator")
        
        if not st.session_state.linkedin_posts:
            st.info("💡 Generate posts in 'Manual Input' or 'News Discovery' tabs")
            return
        
        st.markdown("### 📝 Generated LinkedIn Posts")
        
        for idx, post in enumerate(st.session_state.linkedin_posts):
            expander_title = f"LinkedIn Post #{idx+1}"
            if post.get('source_article'):
                expander_title += f" - {post['source_article'][:50]}..."
            elif post.get('source_video'):
                expander_title += f" - {post['source_video'][:50]}..."
            
            with st.expander(expander_title, expanded=idx==0):
                st.caption(f"**Template:** {post.get('template', 'N/A')}")
                
                if post.get("source_article"):
                    st.caption(f"📰 Source: {post['source_article'][:60]}...")
                elif post.get("source_video"):
                    st.caption(f"🎥 Source: {post['source_video'][:60]}...")
                
                st.markdown("---")
                st.markdown("**Post Content:**")
                st.text_area(
                    "Edit if needed:",
                    value=post["content"],
                    key=f"edit_li_{idx}",
                    height=400
                )
                st.caption(f"📏 {post['char_count']}")
                
                st.download_button(
                    "📥 Download",
                    post["content"],
                    f"linkedin_post_{idx+1}.txt",
                    key=f"dl_li_{idx}"
                )

    def _display_generated_posts(self):
        """Display X posts"""
        st.markdown("### 📝 Generated X Posts")
        
        for idx, post in enumerate(st.session_state.generated_posts):
            expander_title = f"Variation {post.get('variation', idx+1)} - {post.get('template', 'N/A')}"
            
            with st.expander(expander_title, expanded=idx==0):
                col_meta1, col_meta2, col_meta3 = st.columns(3)
                with col_meta1:
                    st.caption(f"**Template:** {post.get('template', 'N/A')}")
                with col_meta2:
                    hook_cat = post.get('hook_category', 'Auto')
                    st.caption(f"**Hook:** {hook_cat}")
                with col_meta3:
                    st.caption(f"**Length:** {post.get('length_type', 'N/A').split('(')[0].strip()}")
                
                if post.get("source_article"):
                    st.caption(f"📰 Source: {post['source_article'][:60]}...")
                elif post.get("source_video"):
                    st.caption(f"🎥 Source: {post['source_video'][:60]}...")
                
                if post.get("hook_used"):
                    st.info(f"🎯 Opening: {post['hook_used']}")
                
                st.markdown("---")
                st.text_area(
                    "Post Content:",
                    value=post["content"],
                    key=f"edit_x_{idx}",
                    height=250
                )
                
                st.caption(f"📏 {post.get('char_count', 'N/A')}")
                
                col_eng1, col_eng2 = st.columns([2, 1])
                
                with col_eng1:
                    st.markdown("**💡 Engagement Tips:**")
                    for tip in post.get("engagement_tips", []):
                        st.markdown(f"- {tip}")
                
                with col_eng2:
                    if st.session_state.get("virality_enabled"):
                        virality = self._evaluate_virality(post["content"], post.get("template", ""))
                        st.metric("Virality", f"{virality['score']}/10")
                
                st.download_button(
                    "📥 Download",
                    post["content"],
                    f"x_post_{idx+1}.txt",
                    key=f"dl_x_{idx}"
                )

    def render_footer(self):
        """Render footer"""
        st.markdown("---")
        st.caption("Advanced X & LinkedIn Post Generator")

    def run(self):
        """Main entry point"""
        self.render_sidebar()
        self.render_main_content()
        self.render_footer()


if __name__ == "__main__":
    app = XPostGeneratorApp()
    app.run()