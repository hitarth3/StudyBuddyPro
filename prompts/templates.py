"""
StudyBuddy Pro — LLM Prompt Templates

All prompt templates used across the application. Each template uses
Python string formatting with named placeholders.
"""

# ---------------------------------------------------------------------------
# RAG Chat
# ---------------------------------------------------------------------------

RAG_SYSTEM_PROMPT = """You are StudyBuddy Pro, an expert AI study assistant. Your role is to help students understand their study material deeply and prepare for exams.

RULES:
1. Answer ONLY using the provided context from the student's uploaded documents.
2. For EVERY claim or fact, include a citation in the format [Source N] where N corresponds to the source number.
3. If the context does not contain enough information to answer confidently, say: "Based on your uploaded notes, I don't have sufficient information to answer this question accurately. Consider uploading more material on this topic."
4. Structure your answers with clear headings, bullet points, and examples where appropriate.
5. Be thorough but concise. Prioritize clarity over length.
6. If the student asks a follow-up question, use the conversation history for context.

EXPLAIN MODE: {explain_mode}
DIFFICULTY: {difficulty}
"""

RAG_USER_PROMPT = """Context from uploaded documents:
{context}

Sources:
{sources}

Conversation history:
{chat_history}

Student's question: {question}

Provide a comprehensive answer with [Source N] citations for every key claim. End with a confidence assessment (0-100%) of how well the context covers this question."""

QUERY_REWRITE_PROMPT = """Given the conversation history and the latest question, rewrite the question to be self-contained and optimized for semantic search retrieval.

Conversation history:
{chat_history}

Latest question: {question}

Rewritten question (return ONLY the rewritten question, nothing else):"""

# ---------------------------------------------------------------------------
# Explain Modes
# ---------------------------------------------------------------------------

EXPLAIN_MODES = {
    "default": "Explain clearly at a general level appropriate for any student.",
    "eli10": "Explain as if the student is 10 years old. Use simple words, fun analogies, and relatable examples. Avoid jargon entirely.",
    "high_school": "Explain at a high school level. Use clear language, provide real-world examples, and define technical terms when first used.",
    "college": "Explain at a college/university level. Use appropriate academic terminology, provide rigorous definitions, and include relevant theoretical context.",
    "exam_revision": "Explain in exam-revision mode. Be extremely concise. Focus on key definitions, formulas, and facts. Use bullet points. Highlight common exam pitfalls.",
}

DIFFICULTY_MODES = {
    "easy": "Keep explanations simple and foundational. Focus on core concepts only.",
    "medium": "Provide balanced explanations with moderate depth and some advanced details.",
    "hard": "Provide in-depth, advanced explanations. Include edge cases, nuances, and complex relationships between concepts.",
    "adaptive": "Adapt the difficulty based on the complexity of the question asked.",
}

# ---------------------------------------------------------------------------
# Quiz Generation
# ---------------------------------------------------------------------------

QUIZ_GENERATION_PROMPT = """You are an expert quiz generator for educational content. Generate a quiz based on the provided study material.

Study material context:
{context}

Topic focus: {topic}
Difficulty: {difficulty}
Number of MCQs: {num_mcq}
Number of Short Answer questions: {num_short}

Generate a quiz in the following EXACT JSON format (no additional text before or after):
{{
    "questions": [
        {{
            "id": 1,
            "type": "mcq",
            "question": "What is...?",
            "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
            "correct_answer": "B",
            "explanation": "The correct answer is B because...",
            "difficulty": "medium",
            "topic": "Topic Name"
        }},
        {{
            "id": 6,
            "type": "short_answer",
            "question": "Explain the concept of...",
            "correct_answer": "A comprehensive expected answer...",
            "explanation": "Key points that should be covered...",
            "difficulty": "medium",
            "topic": "Topic Name"
        }}
    ]
}}

RULES:
- MCQ questions should have exactly 4 options labeled A, B, C, D
- Questions must be based ONLY on the provided context
- Include a mix of recall, comprehension, and application questions
- Each question must have a clear, unambiguous correct answer
- Explanations should reference the source material
- Return ONLY valid JSON, no markdown fences or extra text"""

# ---------------------------------------------------------------------------
# Quiz Evaluation
# ---------------------------------------------------------------------------

QUIZ_EVALUATION_PROMPT = """You are an expert exam evaluator. Evaluate the student's answers against the correct answers.

Questions and answers:
{qa_pairs}

For each answer, evaluate and return JSON in this EXACT format:
{{
    "results": [
        {{
            "question_id": 1,
            "status": "correct",
            "marks": 1.0,
            "max_marks": 1.0,
            "explanation": "Correct! The answer matches..."
        }},
        {{
            "question_id": 2,
            "status": "incorrect",
            "marks": 0.0,
            "max_marks": 1.0,
            "explanation": "Incorrect. The correct answer is... because..."
        }},
        {{
            "question_id": 3,
            "status": "partial",
            "marks": 0.5,
            "max_marks": 1.0,
            "explanation": "Partially correct. You mentioned X but missed Y..."
        }}
    ],
    "total_marks": 7.5,
    "max_marks": 10,
    "percentage": 75.0,
    "summary": "Overall performance summary..."
}}

RULES:
- For MCQs: award 1.0 for correct, 0.0 for incorrect (no partial)
- For short answers: award 0.0 to 1.0 based on completeness and accuracy
- status must be one of: "correct", "incorrect", "partial"
- Be fair but rigorous in evaluation
- Return ONLY valid JSON"""

# ---------------------------------------------------------------------------
# Weak Topic Detection
# ---------------------------------------------------------------------------

WEAK_TOPIC_PROMPT = """Analyze the following quiz history and identify the student's weak and strong topics.

Quiz history:
{quiz_history}

Return a JSON analysis in this EXACT format:
{{
    "weak_topics": [
        {{
            "topic": "Topic Name",
            "accuracy": 30.0,
            "times_tested": 5,
            "common_mistakes": ["Mistake 1", "Mistake 2"],
            "recommendation": "Focus on..."
        }}
    ],
    "strong_topics": [
        {{
            "topic": "Topic Name",
            "accuracy": 90.0,
            "times_tested": 3
        }}
    ],
    "overall_recommendation": "Overall study advice..."
}}

Rank weak topics from weakest to strongest. Return ONLY valid JSON."""

# ---------------------------------------------------------------------------
# Flashcard Generation
# ---------------------------------------------------------------------------

FLASHCARD_GENERATION_PROMPT = """Generate educational flashcards from the provided study material.

Study material context:
{context}

Topic: {topic}
Number of flashcards: {count}

Return flashcards in this EXACT JSON format:
{{
    "flashcards": [
        {{
            "id": 1,
            "front": "Question or term",
            "back": "Answer or definition",
            "topic": "Topic Name",
            "difficulty": "medium"
        }}
    ]
}}

RULES:
- Front should be a clear question, term, or concept
- Back should be a concise but complete answer or definition
- Include a variety of question types: definitions, concepts, applications
- Base all content on the provided context only
- Return ONLY valid JSON"""

# ---------------------------------------------------------------------------
# Summary Generation
# ---------------------------------------------------------------------------

SUMMARY_SHORT_PROMPT = """Summarize the following study material in a concise paragraph (150-200 words). Focus on the key themes and main takeaways.

Material:
{context}

Provide a clear, well-structured short summary:"""

SUMMARY_DETAILED_PROMPT = """Provide a comprehensive, detailed summary of the following study material. Include all major topics, subtopics, key concepts, and their relationships.

Material:
{context}

Structure the summary with:
- Main themes and overarching concepts
- Key definitions and terminology
- Important relationships and connections
- Notable examples or applications
- Critical formulas or rules (if applicable)

Detailed summary:"""

SUMMARY_BULLETS_PROMPT = """Convert the following study material into well-organized bullet point notes. Use hierarchical bullet points with main topics and sub-points.

Material:
{context}

Format as:
• Main Topic 1
  - Key point
  - Key point
    - Sub-detail
• Main Topic 2
  - Key point

Bullet point notes:"""

SUMMARY_ONE_PAGE_PROMPT = """Create a comprehensive one-page study sheet from the following material. This should serve as a quick reference for exam revision.

Material:
{context}

Include:
- Key definitions in bold
- Important formulas/rules in a separate section
- Critical facts and figures
- Common exam topics highlighted
- Memory aids or mnemonics where helpful

One-page study sheet:"""

SUMMARY_MIND_MAP_PROMPT = """Create a text-based mind map of the following study material using Markdown formatting. Use indentation and symbols to show hierarchy and connections.

Material:
{context}

Format as a hierarchical mind map:
# Central Topic
## Branch 1
### Sub-branch 1.1
- Detail
- Detail
### Sub-branch 1.2
- Detail
## Branch 2
### Sub-branch 2.1
- Detail

Mind map:"""

# ---------------------------------------------------------------------------
# Revision Notes
# ---------------------------------------------------------------------------

REVISION_NOTES_PROMPT = """Generate comprehensive revision notes from the following study material. These notes should be optimized for exam preparation.

Material:
{context}

Topic focus: {topic}

Structure the revision notes as follows:

## 📚 Key Definitions
List and explain all important terms and definitions.

## 📐 Important Formulas & Rules
List all formulas, rules, theorems, or principles with brief explanations.

## 💡 Core Concepts Explained
Explain the main concepts clearly and concisely.

## 📝 Worked Examples
Provide step-by-step examples where applicable.

## ⚠️ Common Mistakes to Avoid
List typical errors students make on this topic.

## 🎯 Exam Tips
Provide specific tips for answering exam questions on this topic.

Revision notes:"""

# ---------------------------------------------------------------------------
# Study Planner
# ---------------------------------------------------------------------------

STUDY_PLAN_PROMPT = """Create a detailed study plan based on the following information.

Topics to cover:
{topics}

Exam date: {exam_date}
Days until exam: {days_remaining}
Study hours per day: {hours_per_day}

Create a structured study plan with:

## 📅 Daily Study Schedule
A day-by-day plan allocating topics to specific dates. Include:
- Topic to study
- Estimated time needed
- Learning objectives for each session

## 📖 Revision Timetable
A structured revision schedule for reviewing previously covered material.

## 📝 Mock Test Schedule
When to take practice tests and which topics to cover.

## 🔄 Final Revision Week
A detailed plan for the last 7 days before the exam, including:
- Quick review sessions
- Practice questions
- Rest and mental preparation

## 💡 Study Tips
General tips for effective studying.

Study plan:"""
