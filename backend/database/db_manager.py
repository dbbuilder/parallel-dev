"""
Database Manager for ParallelDev
Handles SQLite database operations with full CRUD support.
"""

import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager


logger = logging.getLogger(__name__)


def init_database(db_path: str | Path) -> None:
    """
    Initialize database with schema from schema.sql.

    Args:
        db_path: Path to SQLite database file

    Raises:
        FileNotFoundError: If schema.sql not found
        sqlite3.Error: If database initialization fails
    """
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)

    # Read schema file
    schema_path = Path(__file__).parent / "schema.sql"
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    # Create database and execute schema
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.executescript(schema_sql)
        conn.commit()
        conn.close()
        logger.info(f"Database initialized successfully: {db_path}")
    except sqlite3.Error as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


class DatabaseManager:
    """
    Manages database connections and operations.

    This class provides:
    - Connection management with automatic cleanup
    - CRUD operations for all entities
    - Transaction support
    - Query helpers and utilities
    """

    def __init__(self, db_path: str | Path):
        """
        Initialize database manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        # Use check_same_thread=False for Flask's multi-threaded environment
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.conn.cursor()

    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.debug("Database connection closed")

    def commit(self) -> None:
        """Commit current transaction."""
        self.conn.commit()

    def rollback(self) -> None:
        """Rollback current transaction."""
        self.conn.rollback()

    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions.

        Usage:
            with db_manager.transaction():
                db_manager.execute_query("INSERT ...")
                db_manager.execute_query("UPDATE ...")
        """
        try:
            yield
            self.commit()
        except Exception:
            self.rollback()
            raise

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def foreign_keys_enabled(self) -> bool:
        """
        Check if foreign keys are enabled.

        Returns:
            True if foreign keys are enabled
        """
        result = self.cursor.execute("PRAGMA foreign_keys").fetchone()
        return result[0] == 1

    def get_tables(self) -> List[str]:
        """
        Get list of all tables in database.

        Returns:
            List of table names
        """
        self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        return [row[0] for row in self.cursor.fetchall()]

    def get_views(self) -> List[str]:
        """
        Get list of all views in database.

        Returns:
            List of view names
        """
        self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='view' ORDER BY name"
        )
        return [row[0] for row in self.cursor.fetchall()]

    def get_indexes(self) -> List[str]:
        """
        Get list of all indexes in database.

        Returns:
            List of index names
        """
        self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='index' ORDER BY name"
        )
        return [row[0] for row in self.cursor.fetchall() if row[0] is not None]

    def get_columns(self, table_name: str) -> List[str]:
        """
        Get list of columns for a table.

        Args:
            table_name: Name of the table

        Returns:
            List of column names
        """
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        return [row[1] for row in self.cursor.fetchall()]

    def table_exists(self, table_name: str) -> bool:
        """
        Check if table exists.

        Args:
            table_name: Name of the table

        Returns:
            True if table exists
        """
        return table_name in self.get_tables()

    def get_schema_version(self) -> int:
        """
        Get current schema version.

        Returns:
            Schema version number
        """
        result = self.execute_query(
            "SELECT MAX(version) as version FROM schema_version"
        )
        return result[0]['version'] if result and result[0]['version'] else 0

    # =========================================================================
    # Query Execution Methods
    # =========================================================================

    def execute_query(self, query: str, params: Tuple = None) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results as list of dictionaries.

        Args:
            query: SQL query string
            params: Optional query parameters

        Returns:
            List of dictionaries (rows)
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)

            # Convert Row objects to dictionaries
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]

        except sqlite3.Error as e:
            logger.error(f"Query execution failed: {e}\nQuery: {query}")
            raise

    def execute_update(self, query: str, params: Tuple = None) -> int:
        """
        Execute an INSERT, UPDATE, or DELETE query.

        Args:
            query: SQL query string
            params: Optional query parameters

        Returns:
            Number of affected rows
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)

            self.conn.commit()
            return self.cursor.rowcount

        except sqlite3.Error as e:
            logger.error(f"Update execution failed: {e}\nQuery: {query}")
            self.conn.rollback()
            raise

    def execute_many(self, query: str, data: List[Tuple]) -> int:
        """
        Execute query with multiple parameter sets (batch operation).

        Args:
            query: SQL query string with placeholders
            data: List of parameter tuples

        Returns:
            Number of affected rows
        """
        try:
            self.cursor.executemany(query, data)
            self.conn.commit()
            return self.cursor.rowcount

        except sqlite3.Error as e:
            logger.error(f"Batch execution failed: {e}")
            self.conn.rollback()
            raise

    def insert_and_get_id(self, query: str, params: Tuple = None) -> int:
        """
        Execute INSERT query and return the new row ID.

        Args:
            query: SQL INSERT query string
            params: Optional query parameters

        Returns:
            ID of newly inserted row
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)

            self.conn.commit()
            return self.cursor.lastrowid

        except sqlite3.Error as e:
            logger.error(f"Insert failed: {e}\nQuery: {query}")
            self.conn.rollback()
            raise

    # =========================================================================
    # Configuration Methods
    # =========================================================================

    def get_all_configuration(self) -> List[Dict[str, Any]]:
        """
        Get all configuration key-value pairs.

        Returns:
            List of configuration dictionaries
        """
        return self.execute_query("SELECT * FROM configuration ORDER BY key")

    def get_configuration(self, key: str) -> Optional[str]:
        """
        Get configuration value by key.

        Args:
            key: Configuration key

        Returns:
            Configuration value or None if not found
        """
        result = self.execute_query(
            "SELECT value FROM configuration WHERE key = ?",
            (key,)
        )
        return result[0]['value'] if result else None

    def set_configuration(self, key: str, value: str, description: str = None) -> None:
        """
        Set configuration value.

        Args:
            key: Configuration key
            value: Configuration value
            description: Optional description
        """
        if description:
            self.execute_update(
                "INSERT OR REPLACE INTO configuration (key, value, description) "
                "VALUES (?, ?, ?)",
                (key, value, description)
            )
        else:
            self.execute_update(
                "INSERT OR REPLACE INTO configuration (key, value) VALUES (?, ?)",
                (key, value)
            )

    # =========================================================================
    # Project CRUD Operations
    # =========================================================================

    def create_project(self, name: str, path: str, **kwargs) -> int:
        """
        Create a new project. Returns project ID.

        Args:
            name: Project name
            path: Project path (must be unique)
            **kwargs: Optional fields (description, parent_id, status,
                     requirements_content, todo_content, readme_content)

        Returns:
            ID of newly created project

        Raises:
            sqlite3.IntegrityError: If path is not unique or parent_id is invalid
        """
        # Build dynamic INSERT query
        fields = ['name', 'path']
        values = [name, path]

        # Add optional fields
        optional_fields = [
            'description', 'parent_id', 'status',
            'requirements_content', 'todo_content', 'readme_content'
        ]

        for field in optional_fields:
            if field in kwargs:
                fields.append(field)
                values.append(kwargs[field])

        placeholders = ', '.join(['?' for _ in fields])
        fields_str = ', '.join(fields)

        query = f"INSERT INTO projects ({fields_str}) VALUES ({placeholders})"

        return self.insert_and_get_id(query, tuple(values))

    def get_project(self, project_id: int) -> Optional[Dict[str, Any]]:
        """
        Get project by ID.

        Args:
            project_id: Project ID

        Returns:
            Project dictionary or None if not found
        """
        result = self.execute_query(
            "SELECT * FROM projects WHERE id = ?",
            (project_id,)
        )
        return result[0] if result else None

    def get_project_by_path(self, path: str) -> Optional[Dict[str, Any]]:
        """
        Get project by path.

        Args:
            path: Project path

        Returns:
            Project dictionary or None if not found
        """
        result = self.execute_query(
            "SELECT * FROM projects WHERE path = ?",
            (path,)
        )
        return result[0] if result else None

    def update_project(self, project_id: int, **kwargs) -> bool:
        """
        Update project. Returns True if successful.

        Args:
            project_id: Project ID
            **kwargs: Fields to update (name, description, status, etc.)

        Returns:
            True if project was updated, False if not found
        """
        if not kwargs:
            return False

        # Build dynamic UPDATE query
        set_clauses = []
        values = []

        allowed_fields = [
            'name', 'path', 'description', 'parent_id', 'status',
            'requirements_content', 'todo_content', 'readme_content',
            'last_scanned'
        ]

        for field in allowed_fields:
            if field in kwargs:
                set_clauses.append(f"{field} = ?")
                values.append(kwargs[field])

        if not set_clauses:
            return False

        values.append(project_id)
        set_clause_str = ', '.join(set_clauses)

        query = f"UPDATE projects SET {set_clause_str} WHERE id = ?"

        rows_affected = self.execute_update(query, tuple(values))
        return rows_affected > 0

    def delete_project(self, project_id: int) -> bool:
        """
        Delete project. Returns True if successful.

        Args:
            project_id: Project ID

        Returns:
            True if project was deleted, False if not found
        """
        rows_affected = self.execute_update(
            "DELETE FROM projects WHERE id = ?",
            (project_id,)
        )
        return rows_affected > 0

    def list_projects(self, **filters) -> List[Dict[str, Any]]:
        """
        List all projects with optional filters.

        Args:
            **filters: Optional filters (status, parent_id)

        Returns:
            List of project dictionaries
        """
        query = "SELECT * FROM projects"
        conditions = []
        values = []

        # Add filter conditions
        if 'status' in filters:
            conditions.append("status = ?")
            values.append(filters['status'])

        if 'parent_id' in filters:
            conditions.append("parent_id = ?")
            values.append(filters['parent_id'])

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY created_at DESC"

        return self.execute_query(query, tuple(values) if values else None)

    # =========================================================================
    # Task CRUD Operations
    # =========================================================================

    def create_task(self, project_id: int, description: str, **kwargs) -> int:
        """
        Create a new task. Returns task ID.

        Args:
            project_id: Project ID
            description: Task description
            **kwargs: Optional fields (section, stage, priority, status,
                     order_number, line_number, parent_task_id, estimated_effort)

        Returns:
            ID of newly created task

        Raises:
            sqlite3.IntegrityError: If project_id or parent_task_id is invalid
        """
        # Build dynamic INSERT query
        fields = ['project_id', 'description']
        values = [project_id, description]

        # Add optional fields
        optional_fields = [
            'section', 'stage', 'priority', 'status',
            'order_number', 'line_number', 'parent_task_id', 'estimated_effort'
        ]

        for field in optional_fields:
            if field in kwargs:
                fields.append(field)
                values.append(kwargs[field])

        placeholders = ', '.join(['?' for _ in fields])
        fields_str = ', '.join(fields)

        query = f"INSERT INTO tasks ({fields_str}) VALUES ({placeholders})"

        return self.insert_and_get_id(query, tuple(values))

    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """
        Get task by ID.

        Args:
            task_id: Task ID

        Returns:
            Task dictionary or None if not found
        """
        result = self.execute_query(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,)
        )
        return result[0] if result else None

    def update_task(self, task_id: int, **kwargs) -> bool:
        """
        Update task. Returns True if successful.

        Args:
            task_id: Task ID
            **kwargs: Fields to update (description, status, priority, etc.)

        Returns:
            True if task was updated, False if not found
        """
        if not kwargs:
            return False

        # Build dynamic UPDATE query
        set_clauses = []
        values = []

        allowed_fields = [
            'description', 'section', 'stage', 'priority', 'status',
            'order_number', 'line_number', 'parent_task_id', 'estimated_effort'
        ]

        for field in allowed_fields:
            if field in kwargs:
                set_clauses.append(f"{field} = ?")
                values.append(kwargs[field])

        if not set_clauses:
            return False

        values.append(task_id)
        set_clause_str = ', '.join(set_clauses)

        query = f"UPDATE tasks SET {set_clause_str} WHERE id = ?"

        rows_affected = self.execute_update(query, tuple(values))
        return rows_affected > 0

    def delete_task(self, task_id: int) -> bool:
        """
        Delete task. Returns True if successful.

        Args:
            task_id: Task ID

        Returns:
            True if task was deleted, False if not found
        """
        rows_affected = self.execute_update(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,)
        )
        return rows_affected > 0

    def list_tasks(self, project_id: int = None, **filters) -> List[Dict[str, Any]]:
        """
        List tasks with optional filters.

        Args:
            project_id: Optional project ID filter
            **filters: Optional filters (status, priority, parent_task_id)

        Returns:
            List of task dictionaries
        """
        query = "SELECT * FROM tasks"
        conditions = []
        values = []

        # Add project_id filter
        if project_id is not None:
            conditions.append("project_id = ?")
            values.append(project_id)

        # Add other filter conditions
        if 'status' in filters:
            conditions.append("status = ?")
            values.append(filters['status'])

        if 'priority' in filters:
            conditions.append("priority = ?")
            values.append(filters['priority'])

        if 'parent_task_id' in filters:
            conditions.append("parent_task_id = ?")
            values.append(filters['parent_task_id'])

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY order_number, created_at ASC"

        return self.execute_query(query, tuple(values) if values else None)

    # =========================================================================
    # Requirement CRUD Operations
    # =========================================================================

    def create_requirement(self, project_id: int, description: str, **kwargs) -> int:
        """
        Create a new requirement. Returns requirement ID.

        Args:
            project_id: Project ID
            description: Requirement description
            **kwargs: Optional fields (category, priority, status,
                     requirement_number, line_number)

        Returns:
            ID of newly created requirement

        Raises:
            sqlite3.IntegrityError: If project_id is invalid
        """
        # Build dynamic INSERT query
        fields = ['project_id', 'description']
        values = [project_id, description]

        # Add optional fields
        optional_fields = [
            'category', 'priority', 'status',
            'requirement_number', 'line_number'
        ]

        for field in optional_fields:
            if field in kwargs:
                fields.append(field)
                values.append(kwargs[field])

        placeholders = ', '.join(['?' for _ in fields])
        fields_str = ', '.join(fields)

        query = f"INSERT INTO requirements ({fields_str}) VALUES ({placeholders})"

        return self.insert_and_get_id(query, tuple(values))

    def get_requirement(self, requirement_id: int) -> Optional[Dict[str, Any]]:
        """
        Get requirement by ID.

        Args:
            requirement_id: Requirement ID

        Returns:
            Requirement dictionary or None if not found
        """
        result = self.execute_query(
            "SELECT * FROM requirements WHERE id = ?",
            (requirement_id,)
        )
        return result[0] if result else None

    def update_requirement(self, requirement_id: int, **kwargs) -> bool:
        """
        Update requirement. Returns True if successful.

        Args:
            requirement_id: Requirement ID
            **kwargs: Fields to update (description, status, priority, etc.)

        Returns:
            True if requirement was updated, False if not found
        """
        if not kwargs:
            return False

        # Build dynamic UPDATE query
        set_clauses = []
        values = []

        allowed_fields = [
            'description', 'category', 'priority', 'status',
            'requirement_number', 'line_number'
        ]

        for field in allowed_fields:
            if field in kwargs:
                set_clauses.append(f"{field} = ?")
                values.append(kwargs[field])

        if not set_clauses:
            return False

        values.append(requirement_id)
        set_clause_str = ', '.join(set_clauses)

        query = f"UPDATE requirements SET {set_clause_str} WHERE id = ?"

        rows_affected = self.execute_update(query, tuple(values))
        return rows_affected > 0

    def delete_requirement(self, requirement_id: int) -> bool:
        """
        Delete requirement. Returns True if successful.

        Args:
            requirement_id: Requirement ID

        Returns:
            True if requirement was deleted, False if not found
        """
        rows_affected = self.execute_update(
            "DELETE FROM requirements WHERE id = ?",
            (requirement_id,)
        )
        return rows_affected > 0

    def list_requirements(self, project_id: int = None, **filters) -> List[Dict[str, Any]]:
        """
        List requirements with optional filters.

        Args:
            project_id: Optional project ID filter
            **filters: Optional filters (status, priority, category)

        Returns:
            List of requirement dictionaries
        """
        query = "SELECT * FROM requirements"
        conditions = []
        values = []

        # Add project_id filter
        if project_id is not None:
            conditions.append("project_id = ?")
            values.append(project_id)

        # Add other filter conditions
        if 'status' in filters:
            conditions.append("status = ?")
            values.append(filters['status'])

        if 'priority' in filters:
            conditions.append("priority = ?")
            values.append(filters['priority'])

        if 'category' in filters:
            conditions.append("category = ?")
            values.append(filters['category'])

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY requirement_number, created_at ASC"

        return self.execute_query(query, tuple(values) if values else None)


# =============================================================================
# Helper Functions
# =============================================================================

def get_database_manager(db_path: str | Path = None) -> DatabaseManager:
    """
    Get database manager instance (factory function).

    Args:
        db_path: Optional database path (defaults to config value)

    Returns:
        DatabaseManager instance
    """
    if db_path is None:
        # Import here to avoid circular dependency
        from backend.config import get_config
        config = get_config()
        db_path = config.get('database.path', './data/projects.db')

    return DatabaseManager(db_path)
