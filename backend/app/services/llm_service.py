"""
LLM Service — handles Groq API calls for generation.
Implements: streaming, structured prompts, fallback, token tracking.
"""

from openai import OpenAI
from app.config import get_settings
import json
import time

settings = get_settings()

# ── System Prompt (versioned — v1.0) ──
SYSTEM_PROMPT_V1 = """You are an Enterprise Knowledge Assistant. Your role is to answer questions accurately based ONLY on the provided context documents.

## RULES
1. Answer ONLY using information from the provided context passages.
2. If the context does not contain enough information to answer, respond with:
   {"answer": "I don't have enough information in the uploaded documents to answer this question.", "confidence": 0.0, "sources": []}
3. Always cite your sources using the format [Source: filename, Page X].
4. Be concise but thorough. Do not add information beyond what the context provides.
5. If multiple sources are relevant, cite all of them.

## OUTPUT FORMAT
Respond in this exact JSON format:
{
  "answer": "Your detailed answer here with [Source: filename, Page X] citations inline.",
  "confidence": 0.85,
  "sources": [
    {"filename": "document.pdf", "page": 3, "relevance": "high"}
  ]
}
"""


def build_rag_prompt(query: str, chunks: list[dict]) -> list[dict]:
    """
    Build the message array for the Groq API call.

    Args:
        query: The user's question.
        chunks: Retrieved chunks from Qdrant with text, filename, page.

    Returns:
        List of message dicts for the chat completion API.
    """
    # Format retrieved context with source labels
    context_parts = []
    for i, chunk in enumerate(chunks):
        source_label = f"[Source: {chunk['filename']}, Page {chunk['page']}]"
        context_parts.append(f"--- Passage {i+1} {source_label} ---\n{chunk['text']}")

    context_str = "\n\n".join(context_parts)

    return [
        {"role": "system", "content": SYSTEM_PROMPT_V1},
        {"role": "user", "content": f"## CONTEXT\n{context_str}\n\n## QUESTION\n{query}"},
    ]


def generate_answer(query: str, chunks: list[dict]) -> dict:
    """
    Generate a grounded answer using Groq API.

    Returns:
        Dict with: answer, confidence, sources, input_tokens, output_tokens, latency_ms
    """
    client = OpenAI(
        base_url="https://models.github.ai/inference",
        api_key=settings.github_token
    )
    messages = build_rag_prompt(query, chunks)

    start = time.perf_counter()

    try:
        response = client.chat.completions.create(
            model=settings.llm_model,
            messages=messages,
            temperature=0.1,           # Low temp for factual answers
            max_tokens=1024,
        )

        latency_ms = int((time.perf_counter() - start) * 1000)

        raw_content = response.choices[0].message.content

        # Parse the structured JSON output
        try:
            parsed = json.loads(raw_content)
        except json.JSONDecodeError:
            # Repair loop: if JSON parsing fails, return raw text with low confidence
            parsed = {
                "answer": raw_content,
                "confidence": 0.3,
                "sources": [],
            }

        return {
            "answer": parsed.get("answer", raw_content),
            "confidence": parsed.get("confidence", 0.5),
            "sources": parsed.get("sources", []),
            "model_used": settings.llm_model,
            "input_tokens": response.usage.prompt_tokens,
            "output_tokens": response.usage.completion_tokens,
            "latency_ms": latency_ms,
        }

    except Exception as e:
        latency_ms = int((time.perf_counter() - start) * 1000)
        # ── Fallback response when LLM fails ──
        return {
            "answer": "I'm temporarily unable to process your request. Please try again in a moment.",
            "confidence": 0.0,
            "sources": [],
            "model_used": settings.llm_model,
            "input_tokens": 0,
            "output_tokens": 0,
            "latency_ms": latency_ms,
            "error": str(e),
        }
