KEYWORD_EXTRACTION_PROMPT = """
You are an expert ATS (Applicant Tracking System) analyzer.

Given the following job description, extract the most important keywords and skills that an ATS would scan for.
Focus on: technical skills, tools, frameworks, programming languages, domain knowledge, and key responsibilities.

Job Description:
{jd_text}

Return ONLY a comma-separated list of keywords. No explanations, no bullet points, just keywords.
Example: Python, Machine Learning, SQL, TensorFlow, Data Pipeline, NLP, Docker
"""

GAP_ANALYSIS_PROMPT = """
You are an expert resume consultant and ATS specialist.

Resume Text:
{resume_text}

Job Description Keywords:
{jd_keywords}

Analyze the resume against the job description keywords and provide:
1. MATCHED keywords (present in resume)
2. MISSING keywords (in JD but not in resume)
3. A match score out of 100
4. 3 specific, actionable suggestions to improve the resume

Format your response EXACTLY like this:
MATCHED: keyword1, keyword2, keyword3
MISSING: keyword4, keyword5, keyword6
SCORE: 75
SUGGESTIONS:
1. Add experience with [specific missing skill] by highlighting [relevant project/experience]
2. Include [missing keyword] in your skills section as you have [related experience]
3. Reframe [existing experience] to emphasize [missing requirement]
"""

SUMMARY_REWRITE_PROMPT = """
You are an expert resume writer specializing in ATS optimization.

Current Resume Summary:
{current_summary}

Job Description:
{jd_text}

Missing Keywords to incorporate:
{missing_keywords}

Rewrite the professional summary to:
1. Incorporate the missing keywords naturally
2. Highlight the most relevant experience for this role
3. Keep it to 3-4 sentences maximum
4. Sound professional and human, not keyword-stuffed

Return ONLY the rewritten summary, nothing else.
"""
