import os
import json
import asyncio
from pathlib import Path
from typing import List
from openai import AsyncOpenAI

# ---------------- CONFIG ----------------

MODEL = "gpt-4.1-mini"      # Adjust if needed
TEMPERATURE = 0
MAX_CONCURRENCY = 5         # Tune based on rate limits
TIMEOUT = 120               # Seconds per request

GITINGEST_DIR = Path("gitingest")
OUTPUT_DIR = Path("evaluation_results")
ERROR_DIR = Path("evaluation_errors")
SYSTEM_PROMPT_FILE = Path("system_prompt.txt")

REVIEW_FILE = Path("good_questions_for_review.csv")

# ---------------------------------------

OUTPUT_DIR.mkdir(exist_ok=True)
ERROR_DIR.mkdir(exist_ok=True)

# Create review CSV header once
if not REVIEW_FILE.exists():
    REVIEW_FILE.write_text("roll_no,file_path\n")

client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])

SYSTEM_PROMPT = SYSTEM_PROMPT_FILE.read_text()


def already_done(roll_no: str) -> bool:
    """Checkpoint: skip students already evaluated"""
    return (OUTPUT_DIR / f"{roll_no}.json").exists()


async def evaluate_student(
    roll_no: str,
    content: str,
    semaphore: asyncio.Semaphore,
):
    async with semaphore:
        try:
            response = await client.chat.completions.create(
                model=MODEL,
                temperature=TEMPERATURE,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": content},
                ],
                response_format={"type": "json_object"},
                timeout=TIMEOUT,
            )

            result = json.loads(response.choices[0].message.content)

            # ---------------- WRITE EVALUATION RESULT (ATOMIC) ----------------

            tmp_file = OUTPUT_DIR / f"{roll_no}.json.tmp"
            final_file = OUTPUT_DIR / f"{roll_no}.json"

            with tmp_file.open("w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            tmp_file.rename(final_file)

            # ---------------- WRITE GOOD QUESTIONS FOR HUMAN REVIEW ----------------

            good_paths = result.get("good_question_paths", [])

            if isinstance(good_paths, list) and good_paths:
                with REVIEW_FILE.open("a", encoding="utf-8") as f:
                    for path in good_paths:
                        f.write(f"{roll_no},{path}\n")

            print(f"[OK] {roll_no}")

        except Exception as e:
            error_file = ERROR_DIR / f"{roll_no}.txt"
            error_file.write_text(str(e), encoding="utf-8")
            print(f"[ERROR] {roll_no}: {e}")


async def main():
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    tasks: List[asyncio.Task] = []

    for file in GITINGEST_DIR.iterdir():
        if not file.name.endswith(".txt"):
            continue

        roll_no = file.stem

        # Resume capability
        if already_done(roll_no):
            continue

        content = file.read_text(encoding="utf-8")

        task = asyncio.create_task(
            evaluate_student(roll_no, content, semaphore)
        )
        tasks.append(task)

    if not tasks:
        print("All students already evaluated.")
        return

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
