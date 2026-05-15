from sqlalchemy import Column, Integer, String, DateTime, Text, func, DDL, event, Index
from sqlalchemy.dialects.postgresql import TSVECTOR
from .database import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    source = Column(String)
    url = Column(String)
    url_hash = Column(String, unique=True, index=True, nullable=False)
    published_at = Column(DateTime(timezone=True), server_default=func.now())
    category = Column(String)
    search_vector = Column(TSVECTOR)

    __table_args__ = (
        Index('idx_article_search_vector', search_vector, postgresql_using='gin'),
    )

update_search_vector_ddl = DDL(
    """
    CREATE OR REPLACE FUNCTION update_article_search_vector() RETURNS trigger AS $$
    BEGIN
        NEW.search_vector := 
            setweight(to_tsvector('english', coalesce(NEW.title, '')), 'A') || 
            setweight(to_tsvector('english', coalesce(NEW.body, '')), 'B');
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS article_search_vector_trigger ON articles;
    CREATE TRIGGER article_search_vector_trigger
    BEFORE INSERT OR UPDATE ON articles
    FOR EACH ROW EXECUTE PROCEDURE update_article_search_vector();
    """
)

event.listen(Article.__table__, 'after_create', update_search_vector_ddl)
