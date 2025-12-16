from sqlalchemy import Column, String, Integer, DateTime, BigInteger, ForeignKey, func
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Video(Base):
    __tablename__ = 'videos'
    
    id = Column(String, primary_key=True)  # UUID stored as string
    creator_id = Column(String, nullable=False)
    video_created_at = Column(DateTime(timezone=True), nullable=False)
    
    views_count = Column(BigInteger, default=0)
    likes_count = Column(BigInteger, default=0)
    comments_count = Column(BigInteger, default=0)
    reports_count = Column(BigInteger, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    snapshots = relationship("VideoSnapshot", back_populates="video", cascade="all, delete-orphan")

class VideoSnapshot(Base):
    __tablename__ = 'video_snapshots'
    
    id = Column(String, primary_key=True)
    video_id = Column(String, ForeignKey('videos.id'), nullable=False)
    
    views_count = Column(BigInteger, default=0)
    likes_count = Column(BigInteger, default=0)
    comments_count = Column(BigInteger, default=0)
    reports_count = Column(BigInteger, default=0)
    
    delta_views_count = Column(BigInteger, default=0)
    delta_likes_count = Column(BigInteger, default=0)
    delta_comments_count = Column(BigInteger, default=0)
    delta_reports_count = Column(BigInteger, default=0)
    
    created_at = Column(DateTime(timezone=True), nullable=False) # Snapshot timestamp
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    video = relationship("Video", back_populates="snapshots")
