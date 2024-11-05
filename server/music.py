# server/music.py

import sqlite3
from typing import List, Dict, Any
import re
from .llm import LMStudioClient

class MusicQueryProcessor:
    """Processes natural language queries for music database"""
    
    def __init__(self, db_path: str = "music.db"):
        """
        Initialize the Music Query Processor.
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self.llm_client = LMStudioClient()
    
    def generate_sql(self, query: str) -> str:
        """
        Generate SQL query from natural language input.
        
        Args:
            query (str): Natural language query
            
        Returns:
            str: Generated SQL query
        """
        prompt = f"""
        Convert the following natural language query to a SQL query for a music database.
        The database has a table 'music' with columns: album, artist, composer, year, genre.
        Make the search case-insensitive and use proper SQL syntax.
        
        Query: {query}
        
        Response should only contain the SQL query, nothing else.
        """
        
        sql = self.llm_client.generate(prompt)
        return self._validate_and_clean_sql(sql)
    
    def execute_query(self, sql: str) -> List[Dict[str, Any]]:
        """
        Execute SQL query and return results.
        
        Args:
            sql (str): SQL query to execute
            
        Returns:
            List[Dict[str, Any]]: Query results
            
        Raises:
            Exception: If query execution fails
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(sql)
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise Exception(f"Database error: {str(e)}")
    
    def format_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Format query results for LLM processing.
        
        Args:
            results (List[Dict[str, Any]]): Query results
            
        Returns:
            str: Formatted results
        """
        if not results:
            return "No results found matching your query."
            
        formatted_results = json.dumps(results, indent=2)
        prompt = f"""
        Convert these music database results into a natural language response:
        {formatted_results}
        
        Make the response conversational and well-formatted.
        """
        
        return self.llm_client.generate(prompt)
    
    def _validate_and_clean_sql(self, sql: str) -> str:
        """
        Validate and clean generated SQL query.
        
        Args:
            sql (str): SQL query to validate
            
        Returns:
            str: Cleaned SQL query
            
        Raises:
            Exception: If SQL query is invalid
        """
        # Remove any leading/trailing whitespace and comments
        sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE).strip()
        
        # Basic validation
        if not sql.lower().startswith('select'):
            raise Exception("Invalid SQL query: Must start with SELECT")
        
        # Prevent dangerous operations
        dangerous_keywords = ['drop', 'delete', 'update', 'insert', 'alter', 'create']
        if any(keyword in sql.lower() for keyword in dangerous_keywords):
            raise Exception("Invalid SQL query: Contains forbidden operations")
        
        return sql
