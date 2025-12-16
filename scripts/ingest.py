import asyncio
import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Add parent directory to path so we can import from bot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.database.models import Base, Video, VideoSnapshot

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("Error: DATABASE_URL not set in .env")
    sys.exit(1)

# Fix for asyncpg if needed (e.g. windows)
if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def ingest_data():
    print(f"Connecting to database...")
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    # Drop and recreate tables (for this test task, to ensure clean state)
    async with engine.begin() as conn:
        print("Creating tables...")
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    print("Reading videos.json...")
    try:
        with open("videos.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: videos.json not found in current directory.")
        return

    videos_data = data.get("videos", [])
    print(f"Found {len(videos_data)} videos. Starting import...")

    async with async_session() as session:
        batch_size = 50  # Commit every 50 videos and their snapshots
        
        for i, vid_data in enumerate(videos_data):
            # Parse Video
            video = Video(
                id=vid_data['id'],
                creator_id=vid_data['creator_id'],
                video_created_at=datetime.fromisoformat(vid_data['video_created_at']),
                views_count=vid_data['views_count'],
                likes_count=vid_data['likes_count'],
                comments_count=vid_data['comments_count'],
                reports_count=vid_data['reports_count'],
                created_at=datetime.fromisoformat(vid_data['created_at']),
                updated_at=datetime.fromisoformat(vid_data['updated_at']) if vid_data.get('updated_at') else None
            )
            session.add(video)

            # Parse Snapshots
            snapshots = vid_data.get('snapshots', [])
            for snap_data in snapshots:
                snapshot = VideoSnapshot(
                    id=snap_data['id'],
                    video_id=snap_data['video_id'],
                    views_count=snap_data['views_count'],
                    likes_count=snap_data['likes_count'],
                    comments_count=snap_data['comments_count'],
                    reports_count=snap_data['reports_count'],
                    delta_views_count=snap_data['delta_views_count'],
                    delta_likes_count=snap_data['delta_likes_count'],
                    delta_comments_count=snap_data['delta_comments_count'],
                    delta_reports_count=snap_data['delta_reports_count'],
                    created_at=datetime.fromisoformat(snap_data['created_at']),
                    updated_at=datetime.fromisoformat(snap_data['updated_at']) if snap_data.get('updated_at') else None
                )
                session.add(snapshot)

            if (i + 1) % batch_size == 0:
                print(f"Processed {i + 1} videos...")
                await session.commit()
        
        await session.commit()
        print(f"Successfully imported {len(videos_data)} videos and their snapshots.")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(ingest_data())
