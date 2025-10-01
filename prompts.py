MEGA_PROMPT = """Create an X post about {topic} following these specifications:

POST TYPE: {post_type}

CONTENT REQUIREMENTS:
- Extract the core newsworthy element from: {article_source}
- Identify 2-3 high-value insights or use cases
- Apply appropriate hook from the extensive list below based on content type
- Create curiosity about what comes next
- Provide information that engages the reader
- Use conversational but authoritative tone

---

## COMPREHENSIVE HOOK LIBRARY:

### Learning & Tips Hooks:
1. "5 tips I wish I knew earlier about [topic]"
2. "The most important thing that I learned about [topic]"
3. "5 dumbest mistakes I made in [niche]"
4. "My worst mistake in [niche]"
5. "Life lessons I learned from [topic]"
6. "5 tips to fast success in [niche]"
7. "5 easy ways to monetize [topic]"
8. "5 tips to save time when doing [activity]"
9. "5 tips to save money in [niche]"
10. "One tip that is going to change your life"
11. "10 facts everyone should know about [topic]"
12. "5 facts you didn't know about [topic]"

### Why/Reasoning Hooks:
13. "Why I started doing [activity]"
14. "Why I started instagram account about [niche]"
15. "Why [tool] is better than [tool] (two tools, topics)"
16. "Why [tool/creator] is the worst"
17. "Why you will not succeed at [niche]"
18. "Why you don't deserve success"
19. "Why nobody loves your content"
20. "Why original ideas suck"
21. "Why you will succeed in [niche]"
22. "Why people love [profession]"
23. "Why doing [activity] is good for your health"
24. "Why it is worth doing [activity]"
25. "Why do you like [topic]? Comment below"
26. "Why learning [skill] takes so long"
27. "Why are some people naturally good at [skill]"
28. "Why is it hard to succeed in [niche]"

### Problem/Solution Hooks:
29. "What I hate about [topic] (your niche)"
30. "My worst experience in [niche]"
31. "What I love about [niche]"
32. "You don't need money to start [activity]"
33. "You are wasting your time doing [activity]"
34. "Why you shouldn't do [activity]"
35. "Why you are not good at [skill]"
36. "Mistakes are good for you"
37. "Don't compare yourself to others"
38. "Avoid these 5 mistakes in [niche]"
39. "Stop doing this one mistake"
40. "5 struggles everyone is facing in [niche]"
41. "Debunk a common myth in your industry"
42. "Common misconceptions about me"
43. "Not many people know this about me"

### Contrarian/Provocative Hooks:
44. "Success is overrated"
45. "Working hard is a mistake"
46. "Quit [activity] if you are not creative"
47. "Don't start [activity] if you are emotional"
48. "Instagram hates [your niche]"
49. "Why you will not get better at [skill]"
50. "Never break this one rule in [niche]"
51. "5 facts people neglect about [topic]"
52. "Quantity vs Quality in [niche]"

### How-To/Process Hooks:
53. "How I make my content"
54. "Tools I use in my job"
55. "How most people succeed in [niche]"
56. "How to be unique in [niche]"
57. "5 reasons [activity] is easy"
58. "5 reasons [activity] is hard"
59. "5 mistakes everyone makes when starting [activity]"
60. "How to make people pay you for [service]"
61. "5 best tools for [activity]"
62. "5 lesser known tools for [activity]"
63. "This is how I (make a tutorial)"
64. "How I improved in [skill] on social media"
65. "How I started [journey]"
66. "How I became successful in [niche]"
67. "How long did it take me to succeed in [niche]?"
68. "How to work smart not hard in [niche]"

### Resource/List Hooks:
69. "My top 5 favorite creators in [niche]"
70. "Where to start learning [skill]"
71. "Where to get tools that I use for [activity]"
72. "Top 5 apps to be better in [niche]"
73. "Best websites to learn about [topic]"
74. "Websites to find a job for [niche]"
75. "5 books to become better at [skill]"
76. "5 dos and don'ts about your niche"
77. "5 rules of success in [niche]"

### Personal/Journey Hooks:
78. "Introduce yourself"
79. "Talk about your motivation and struggles"
80. "This is where I work at"
81. "Introduce your family"
82. "Talk about your journey on social media so far"
83. "Talk about your education"
84. "Talk about your struggles in the past"
85. "Talk about a trend in your industry"
86. "Before and after a certain change"
87. "Post a work testimonial"
88. "What to expect when you start [activity]"
89. "10 Funny facts about [topic]"

### Getting Started Hooks:
90. "Easy way to start doing [activity]"
91. "What you will need to start [activity]"
92. "Read this if you are unsure about starting [activity]"
93. "Step by step guide to start with [activity]"
94. "Follow this guide to succeed in [niche]"
95. "5 creative ways to make money with [skill]"
96. "5 ways to become famous with [activity]"

### Unique/Advanced Hooks:
97. "The best thing about [niche]"
98. "A lifehack from your experience"
99. "Best way to promote [activity] on social media"
100. "5 ways to become famous with [topic]"

---

## SHORT POST (~150-280 characters)

Generate a punchy post that:
- Opens with ONE hook from the library above that triggers curiosity/shock/awe
- States one concrete use case or insight
- Ends with intrigue or thought-provoking implication
- Creates "what's next?" curiosity
- NO emojis, NO hashtags

STRUCTURE:
[Hook statement]. [One powerful insight]. [Curiosity gap].

HOOK EXAMPLES FOR SHORT POSTS:
- "The most important thing that I learned about [model]"
- "Why [feature] is better than [alternative]"
- "One tip that is going to change your life"
- "Stop doing this one mistake"
- "Not many people know this about [feature]"

---

## MEDIUM POST (~280-400 characters)

Generate a post that:
- Opens with a hook from the library that triggers curiosity, shock, or awe
- Provides 2 specific insights or use cases
- Engages reader with information that matters
- Creates anticipation for implications
- Includes subtle perspective shift
- NO emojis, NO hashtags

STRUCTURE:
[Hook]. [Insight 1 with context]. [Insight 2]. [Implication/What this means].

HOOK EXAMPLES FOR MEDIUM POSTS:
- "5 tips I wish I knew earlier about [topic]"
- "Why you will not succeed at [task] (without this)"
- "You don't need money to start [activity]"
- "5 facts you didn't know about [topic]"
- "Working hard is a mistake (here's why)"
- "What I hate about [limitation]"
- "How most people succeed in [niche]"

---

## LONG POST (~400-550 characters)

Generate a post that:
- Opens with a strong contrarian or counterintuitive hook from the library
- Presents 3 concrete insights/use cases with brief context
- Builds anticipation throughout
- Creates "what comes next" curiosity
- Includes forward-looking statement
- Engages with valuable, actionable information
- NO emojis, NO hashtags

STRUCTURE:
[Contrarian hook]. [Brief context]. [Insight 1]. [Insight 2]. [Insight 3]. [What this means for the future/industry].

HOOK EXAMPLES FOR LONG POSTS:
- "Success is overrated. Here's what actually matters with [topic]"
- "5 dumbest mistakes I made in [niche] (so you don't have to)"
- "Why [new feature] changes everything about [industry]"
- "The most important thing nobody's talking about [release]"
- "You are wasting your time doing [old method]"
- "Why original ideas suck (and what works instead)"
- "Instagram hates [approach] (but this works)"
- "5 struggles everyone is facing in [niche]"
- "Debunk a common myth: [myth about technology]"

---

## ARTICLE THREAD (Multi-tweet breakdown)

Generate a thread following this exact structure:

### TWEET 1 (Hook + Setup):
- **Sentence 1**: Use a hook from the library that triggers anger, curiosity, fear, shock, or awe. Direct it at a person scrolling by. Make it a complete sentence.
- **Sentence 2**: Introduction to the thread content. Another attention-grabbing statement that previews what's coming.
- Keep it concise, around 2-3 sentences.

HOOK OPTIONS FOR TWEET 1:
- "Why you will not succeed at [task] without knowing this."
- "The most important thing I learned about [topic] that nobody talks about."
- "Stop doing [common practice]. Here's what actually works."
- "5 tips I wish I knew earlier about [topic]."
- "You don't need [expensive thing] to [achieve result]."
- "Working hard at [task] is a mistake. Here's why."
- "Success is overrated in [niche]. What matters is this."
- "Why [tool/approach] is better than [alternative]."
- "Common misconceptions about [topic] are killing your progress."
- "Mistakes are good for you. But only these 5 types."

### TWEETS 2-6 (Content Body):
Each tweet should:
- Build logically on the previous tweet
- Cover: What is it? → Why it matters → Use cases → Implications
- Use analogies or examples for clarity
- Aim for 2-4 sentences per tweet to allow natural flow
- Create natural curiosity to read next tweet
- Include valuable, engaging information
- Maintain conversational but public-facing tone

CONTENT FLOW OPTIONS:
- **Tweet 2**: What the news/feature actually is (simple explanation)
- **Tweet 3**: Why this matters (context and significance)
- **Tweet 4**: Specific use case #1 (concrete example)
- **Tweet 5**: Specific use case #2 (concrete example)
- **Tweet 6**: What this means going forward (implications)

OR

- **Tweet 2**: The problem everyone faces
- **Tweet 3**: How this solves it
- **Tweet 4**: 3 immediate applications
- **Tweet 5**: What makes this different
- **Tweet 6**: What to do next

### FINAL TWEET (Insight/Takeaway):
- Distill the key learning or forward-looking implication
- End with thought-provoking statement or call to action
- Create curiosity about what comes next in the industry
- Keep it to 2-4 sentences for a strong close

THREAD RULES:
- NO emojis anywhere (use words to convey emotion)
- NO hashtags
- Address reader directly but avoid excessive personal details
- Focus on transferable insights and learnings
- Complete sentences in conversational tone
- Each tweet must stand alone yet flow into the next
- Create "I need to read the next one" feeling
- Provide information that engages and educates
- Generate the full thread completely; do not cut off mid-sentence or mid-thought. Ensure all tweets are fully developed.

HOOK INTEGRATION IN THREADS:
Weave these hooks throughout your thread naturally:
- "Life lessons I learned from [experience]"
- "Tools I use in my job for [task]"
- "How I make my content using [tool/feature]"
- "5 easy ways to monetize [capability]"
- "Why doing [activity] is good for your [benefit]"
- "Best way to [achieve outcome]"
- "Never break this one rule in [niche]"
- "How to be unique in [crowded space]"
- "What to expect when you start [activity]"

---

## HOOK CUSTOMIZATION FOR AI/TECH NEWS:

Adapt these proven hooks specifically for your content:

**For Model Releases:**
- "The most important thing about [model] that nobody's talking about"
- "Why [model] is better than [competing model]"
- "5 tips I wish I knew earlier about [model capabilities]"
- "You don't need [expensive alternative] to [achieve outcome] anymore"
- "Stop doing [old method]. [New model] changes everything."

**For Feature Updates:**
- "5 facts you didn't know about [new feature]"
- "Why [feature] will change how you [task]"
- "What I love about [feature] (and one thing I hate)"
- "Tools I use in my job: [feature] edition"
- "How most people will succeed using [feature]"

**For Industry Analysis:**
- "Success is overrated. [Model/feature] proves it."
- "Why original ideas suck (and why [approach] works)"
- "Working hard is a mistake. [Automation/tool] is the answer."
- "Common misconceptions about [technology]"
- "5 struggles everyone is facing in [industry] (solved)"

**For Technical Deep-Dives:**
- "Debunk a common myth: [myth about AI/tech]"
- "5 dumbest mistakes people make with [technology]"
- "Why you are not good at [skill] (and how [tool] helps)"
- "The best thing about [technical capability]"
- "5 lesser known tools for [advanced use case]"

**For Practical Guides:**
- "Step by step guide to start with [new feature]"
- "5 creative ways to make money with [capability]"
- "How to make people pay you for [AI service]"
- "Easy way to start doing [advanced task]"
- "What you will need to start [using new tool]"

**For Trend Predictions:**
- "Why [technology] is the worst (hot take)"
- "Never break this one rule in [AI development]"
- "Before and after [technology adoption]"
- "What to expect when you start [using new tool]"
- "Talk about a trend in your industry: [emerging pattern]"

---

## TONE & STYLE GUIDELINES:

1. **Intermediate English Tone**: Use intermediate and average English like normal human talk. Avoid overly complex vocabulary, formal language, or advanced phrasing. Keep it conversational and relatable, as if chatting with a friend.

1. **Conversational Authority**: Sound like an expert having a casual conversation, not a press release
2. **Direct Address**: Speak to the reader scrolling by ("You need to see this" not "People should know")
3. **Curiosity Creation**: Every sentence should make them want the next one
4. **Value First**: Lead with insight, not description
5. **No Fluff**: Every word earns its place
6. **Engaging Information**: Don't just inform, make it matter to them
7. **Future-Focused**: Always hint at "what's next" or "what this means"

---

## ENGAGEMENT TRIGGERS TO INCLUDE:

- **Curiosity Gap**: Hint at information without revealing everything
- **Contrarian Take**: Challenge common assumptions
- **Practical Value**: Show immediate applicability
- **FOMO Element**: Suggest advantage of knowing this
- **Pattern Break**: Disrupt expected narratives
- **Tangible Examples**: Make abstract concrete
- **Forward Momentum**: Always point to what comes next

---

## INPUT YOUR CONTENT:

**Article/News Source**: {article_source}

**Key Points to Cover**:
{key_points}

**Target Audience**: {target_audience}

**Desired Tone**: {desired_tone}

**Primary Hook to Use**: {primary_hook}

**What Curiosity to Create**: {curiosity_create}

---

Apply style: {apply_style}

Generate the post now following ALL specifications above. 

Output only the post content. For threads, number each tweet (e.g., 1/7, 2/7) and separate tweets with '---' after the full tweet content. Ensure the entire thread is generated completely without cutoff."""

SPECIFIC_PROMPTS = {
    "Breaking News": """Create a SHORT X post about the topic using intermediate and average English like normal human talk. Avoid complex words or formal style.

Use one of these hooks:
- "The most important thing about [topic] that nobody's talking about"
- "Why [news] changes everything"
- "Stop what you're doing. [News] just happened."

Focus on the one insight that changes everything. Create urgency and "what's next" curiosity. NO emojis. NO hashtags.""",
    "Feature Releases": """Create a MEDIUM X post about the new feature using intermediate and average English like normal human talk. Avoid complex words or formal style.

Use one of these hooks:
- "5 facts you didn't know about [feature]"
- "Why [feature] is better than [alternative]"
- "You don't need [expensive tool] anymore"

List 2 concrete use cases. End with implication for the industry. Create curiosity about applications. NO emojis. NO hashtags.""",
    "Deep Analysis": """Create an ARTICLE THREAD about the topic using intermediate and average English like normal human talk. Avoid complex words or formal style.

Tweet 1 hook options:
- "The most important thing I learned about [topic] that nobody talks about"
- "5 dumbest mistakes people make with [topic]"
- "Why you will not succeed at [task] without this"

Break down: what it is → why it matters → 3 use cases → what's next. 

Make each tweet flow naturally. Create "I need to read the next one" feeling. Maximum 3 sentences per tweet. NO emojis. NO hashtags.""",
    "Comparison Posts": """Create a LONG X post comparing two aspects of the topic using intermediate and average English like normal human talk. Avoid complex words or formal style.

Use hook: "Why [A] is better than [B]" or "Why [B] is the worst"

Structure: Hook → Context → 3 key differences → What this means for users.

Engage with valuable insights. Create curiosity about implications. NO emojis. NO hashtags."""
}

LINKEDIN_MEGA_PROMPT = """Create a LinkedIn post about {topic} following these specifications:

POST TYPE: LinkedIn Professional Post

CONTENT REQUIREMENTS:
- Extract core insights from: {article_source}
- Professional yet conversational tone
- Story-driven structure with clear takeaways
- Include 3-5 relevant hashtags at the end
- Length: {length} characters

---

## LINKEDIN POST STRUCTURE:

### HOOK (1-2 lines)
Start with one of these proven LinkedIn hooks:
- "Here's what nobody tells you about [topic]"
- "After [X] years in [industry], here's what I learned"
- "The biggest mistake I see people make with [topic]"
- "This changed how I think about [topic]"
- "Most people don't realize this about [topic]"
- "[Number] lessons from [experience/news]"
- "Why [common belief] is actually wrong"
- "The one thing that surprised me about [topic]"

### CONTEXT (2-4 lines)
Provide background or setup:
- What prompted this post (news, experience, observation)
- Why this matters now
- Brief context for readers unfamiliar with topic

### MAIN CONTENT (8-12 lines)
Break down insights using one of these formats:

**Format 1 - Numbered List:**
Here's what this means:

1. [First insight]
   Brief explanation of why it matters

2. [Second insight]
   Practical implication or example

3. [Third insight]
   Forward-looking statement or prediction

**Format 2 - Story + Insights:**
Tell a brief story, then extract lessons:
- Lesson 1: [insight]
- Lesson 2: [insight]
- Lesson 3: [insight]

**Format 3 - Problem → Solution:**
The challenge: [describe problem]
What's changing: [explain solution/news]
Why it matters: [implications]

### TAKEAWAY (2-3 lines)
End with:
- Key learning or action item
- Question to spark discussion
- Forward-looking statement about industry impact

### HASHTAGS (3-5 tags)
Include relevant professional hashtags:
#ArtificialIntelligence #TechIndustry #Innovation #StartupLife #AITools

---

## TONE GUIDELINES:

1. **Professional but Human**: Use "I" and "you" naturally
2. **Conversational Authority**: Expert sharing insights, not lecturing
3. **Value-First**: Every paragraph should provide insight
4. **Accessible Language**: Explain complex topics simply
5. **Engagement-Focused**: Invite discussion and thoughts
6. **Strategic Emojis**: Use 1-2 emojis max for emphasis (🚀 💡 ⚡)

---

## LINKEDIN-SPECIFIC RULES:

- Length: {length} characters (LinkedIn sweet spot: 1300-2000)
- Line breaks: Use white space generously for readability
- No excessive hashtags (3-5 max at the end)
- Include a discussion prompt or question
- Professional emoji use (not like X/Twitter)
- Write for business professionals and decision-makers
- Focus on actionable insights and implications

---

## INPUT CONTENT:

**Topic**: {topic}

**Article/News Source**: {article_source}

**Key Points**:
{key_points}

**Target Audience**: {target_audience}

**Desired Tone**: {desired_tone}

---

Generate the LinkedIn post now following ALL specifications above.

Output ONLY the post content with proper line breaks and formatting. Do not include explanations or meta-commentary."""