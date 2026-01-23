import asyncio
import os
from app.gemini_utils import enhance_resume_with_gemini
from dotenv import load_dotenv

load_dotenv()


async def main():
    print("Testing Gemini API fix...")
    dummy_resume = "Software Engineer with 5 years of experience in Python and Flask."
    try:
        result = await enhance_resume_with_gemini(
            dummy_resume, "Senior Python Developer"
        )
        print("\nSuccess! Result received:")
        print(f"Structured Data Keys: {result.get('structured_data', {}).keys()}")
        print(f"Latex length: {len(result.get('latex', ''))}")
    except Exception as e:
        print(f"\nFailed with error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
