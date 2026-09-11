from neo4j import GraphDatabase, Driver
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class Neo4jManager:
    _driver: Driver | None = None

    @classmethod
    def get_driver(cls) -> Driver | None:
        if cls._driver is None:
            try:
                cls._driver = GraphDatabase.driver(
                    settings.NEO4J_URI,
                    auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
                )
                # Verify connectivity — raises if unreachable
                cls._driver.verify_connectivity()
                logger.info("Neo4j connected successfully.")
            except Exception as e:
                logger.warning(f"Neo4j unavailable (graph features disabled): {e}")
                # Close stale driver if it was created before connectivity check failed
                try:
                    if cls._driver:
                        cls._driver.close()
                except Exception:
                    pass
                cls._driver = None
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
