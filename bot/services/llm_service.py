import os
import re
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        self.model = os.getenv("LLM_MODEL", "deepseek/deepseek-chat:free")
        self.database_url = os.getenv("DATABASE_URL")
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is not set")
            
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )
        
        self.engine = create_async_engine(self.database_url, echo=False)

    def _get_system_prompt(self):
        return """You are an expert PostgreSQL Data Analyst. 
Your task is to convert natural language questions into a SINGLE SQL query to retrieve a specific metric.
The database schema is as follows:

Table `videos`:
- id (UUID string): Unique video identifier.
- creator_id (string): Creator identifier.
- video_created_at (timestamp): When the video was published.
- views_count (int): Final view count.
- likes_count (int): Final like count.
- comments_count (int): Final comment count.
- reports_count (int): Final report count.
- created_at (timestamp), updated_at (timestamp).

Table `video_snapshots` (Hourly stats for each video):
- id (UUID string): Unique snapshot identifier.
- video_id (UUID string): FK to videos.id.
- created_at (timestamp): The time of this snapshot (hourly).
- views_count, likes_count, comments_count, reports_count: Values at that specific time.
- delta_views_count, delta_likes_count, ...: The INCREASE since the last snapshot.

IMPORTANT RULES:
1. Return ONLY the raw SQL query. Do not wrap it in markdown (```sql ... ```). Do not add explanations.
2. The query must return exactly ONE row with ONE column (a single number).
3. If the user asks for "how many videos", count rows in `videos`.
4. If the user asks for "sum of view growth on date X", use `SUM(delta_views_count)` from `video_snapshots` where `created_at` is within that day.
5. Pay attention to dates. "November 28th" means `created_at >= '2025-11-28 00:00:00' AND created_at < '2025-11-29 00:00:00'`.
6. Use valid PostgreSQL syntax.
"""

    async def generate_sql(self, user_query: str) -> str:
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": user_query}
        ]
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.1,
            max_tokens=200
        )
        
        content = response.choices[0].message.content.strip()
        
        # Cleanup: Remove markdown code blocks if present
        content = re.sub(r'^```sql\s*', '', content)
        content = re.sub(r'^```\s*', '', content)
        content = re.sub(r'\s*```$', '', content)
        
        return content.strip()

    async def execute_sql(self, sql_query: str):
        async with self.engine.connect() as conn:
            try:
                result = await conn.execute(text(sql_query))
                val = result.scalar()
                return val
            except Exception as e:
                return f"Error executing SQL: {e}"
