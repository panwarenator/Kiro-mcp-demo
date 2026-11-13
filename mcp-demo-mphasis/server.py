import sqlite3
import json
import os
from mcp.server.fastmcp import FastMCP

DB_PATH = os.path.join(os.path.dirname(__file__), "talent.db")

mcp = FastMCP("TalentPool-DB-Server")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

@mcp.tool()
def get_database_schema() -> str:
    """Returns the SQL schema structure of all tables in talent.db."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, sql FROM sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite_%';
    """)
    tables = cursor.fetchall()
    conn.close()
    schema_info = []
    for table in tables:
        schema_info.append(f"Table: {table['name']}\nSQL: {table['sql']}\n")
    return "\n".join(schema_info)

@mcp.tool()
def query_talent_database(sql_query: str) -> str:
    """
    Executes a read-only SELECT query against the local talent.db database.
    Use this to inspect employees, skills, allocations, and departments.
    """
    trimmed = sql_query.strip().lower()
    if not trimmed.startswith("select") and not trimmed.startswith("with"):
        return "Error: Only read-only SELECT or CTE queries are permitted."

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        result = [dict(row) for row in rows]
        conn.close()
        return json.dumps(result, indent=2)
    except Exception as e:
        conn.close()
        return f"Database Query Error: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
