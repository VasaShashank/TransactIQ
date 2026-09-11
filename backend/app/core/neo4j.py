from neo4j import GraphDatabase, Driver
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class Neo4jManager:
    _driver: Driver | None = None
    _unavailable: bool = False

    @classmethod
    def get_driver(cls) -> Driver | None:
        if cls._unavailable:
            return None
        if cls._driver is None:
            try:
                cls._driver = GraphDatabase.driver(
                    settings.NEO4J_URI,
                    auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
                )
                # Verify connectivity
                cls._driver.verify_connectivity()
            except Exception as e:
                logger.warning(f"Neo4j is not available, graph features will be disabled: {e}")
                cls._driver = None
                cls._unavailable = True
                return None
        return cls._driver

    @classmethod
    def close(cls):
        if cls._driver is not None:
            cls._driver.close()
            cls._driver = None

def get_neo4j_session():
    driver = Neo4jManager.get_driver()
    if driver is None:
        yield None
        return
    with driver.session() as session:
        yield session
