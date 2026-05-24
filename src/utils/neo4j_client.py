import os
from neo4j import GraphDatabase
from typing import List, Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Neo4jManager:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "neo4j_password")
        self.driver = None
        self._connect()

    def _connect(self):
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            self.driver.verify_connectivity()
            logger.info(f"Connected to Neo4j at {self.uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    def close(self):
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")

    def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            raise

    def initialize_schema(self):
        constraints = [
            "CREATE CONSTRAINT company_name_unique IF NOT EXISTS FOR (c:Company) REQUIRE c.name IS UNIQUE",
            "CREATE CONSTRAINT metric_id_unique IF NOT EXISTS FOR (m:Metric) REQUIRE m.id IS UNIQUE",
            "CREATE CONSTRAINT segment_name_unique IF NOT EXISTS FOR (s:Segment) REQUIRE s.name IS UNIQUE"
        ]
        
        for constraint in constraints:
            try:
                self.execute_query(constraint)
                logger.info(f"Applied constraint: {constraint}")
            except Exception as e:
                logger.warning(f"Constraint may already exist: {e}")

    def create_company_node(self, name: str, ticker: str) -> Dict[str, Any]:
        query = """
        MERGE (c:Company {name: $name})
        SET c.ticker = $ticker
        RETURN c
        """
        result = self.execute_query(query, {"name": name, "ticker": ticker})
        return result[0] if result else None

    def create_metric_node(
        self,
        metric_id: str,
        name: str,
        value: float,
        unit: str
    ) -> Dict[str, Any]:
        query = """
        MERGE (m:Metric {id: $metric_id})
        SET m.name = $name, m.value = $value, m.unit = $unit
        RETURN m
        """
        result = self.execute_query(query, {
            "metric_id": metric_id,
            "name": name,
            "value": value,
            "unit": unit
        })
        return result[0] if result else None

    def create_temporal_relationship(
        self,
        company_name: str,
        metric_id: str,
        quarter: str,
        year: int,
        valid_from: str,
        valid_to: str
    ):
        query = """
        MATCH (c:Company {name: $company_name})
        MATCH (m:Metric {id: $metric_id})
        MERGE (c)-[r:REPORTED]->(m)
        SET r.quarter = $quarter,
            r.year = $year,
            r.valid_from = $valid_from,
            r.valid_to = $valid_to
        RETURN r
        """
        result = self.execute_query(query, {
            "company_name": company_name,
            "metric_id": metric_id,
            "quarter": quarter,
            "year": year,
            "valid_from": valid_from,
            "valid_to": valid_to
        })
        return result[0] if result else None

    def query_company_metrics(
        self,
        company_name: str,
        quarter: Optional[str] = None,
        year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        if quarter and year:
            query = """
            MATCH (c:Company {name: $company_name})-[r:REPORTED]->(m:Metric)
            WHERE r.quarter = $quarter AND r.year = $year
            RETURN c.name as company, m.name as metric, m.value as value, 
                   m.unit as unit, r.quarter as quarter, r.year as year
            """
            params = {"company_name": company_name, "quarter": quarter, "year": year}
        else:
            query = """
            MATCH (c:Company {name: $company_name})-[r:REPORTED]->(m:Metric)
            RETURN c.name as company, m.name as metric, m.value as value, 
                   m.unit as unit, r.quarter as quarter, r.year as year
            ORDER BY r.year DESC, r.quarter DESC
            """
            params = {"company_name": company_name}
        
        return self.execute_query(query, params)
