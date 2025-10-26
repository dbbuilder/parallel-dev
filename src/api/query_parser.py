"""
Query Parameter Parsing Utilities
Handles parsing and validation of API query parameters for filtering, sorting, and pagination.
"""

from typing import Dict, Any, List, Optional
from flask import request


class QueryParseError(Exception):
    """Exception raised for query parameter parsing errors."""
    pass


class QueryParser:
    """Parse and validate query parameters from Flask requests."""

    # Valid sort fields for each resource type
    VALID_SORT_FIELDS = {
        'projects': ['name', 'path', 'created_at', 'updated_at'],
        'tasks': ['description', 'status', 'priority', 'created_at', 'updated_at'],
        'requirements': ['description', 'priority', 'status', 'created_at']
    }

    # Valid filter fields for each resource type
    VALID_FILTERS = {
        'projects': ['name', 'path'],
        'tasks': ['status', 'priority', 'category', 'stage'],
        'requirements': ['priority', 'status']
    }

    # Valid values for enum fields
    VALID_VALUES = {
        'status': ['todo', 'in_progress', 'done', 'blocked'],
        'priority': ['low', 'medium', 'high'],
        'requirement_status': ['planned', 'in_progress', 'completed'],
        'requirement_priority': ['critical', 'high', 'medium', 'low', 'unknown']
    }

    @staticmethod
    def parse_pagination() -> Dict[str, int]:
        """
        Parse pagination parameters from request.

        Returns:
            Dict with 'page' and 'per_page' keys

        Raises:
            QueryParseError: If pagination parameters are invalid
        """
        page = request.args.get('page', type=int)
        per_page = request.args.get('per_page', type=int)

        # Validate page number
        if page is not None:
            if page < 1:
                raise QueryParseError('Page number must be >= 1')

        # Validate per_page
        if per_page is not None:
            if per_page < 1:
                raise QueryParseError('per_page must be >= 1')
            if per_page > 100:
                raise QueryParseError('per_page cannot exceed 100')

        return {
            'page': page,
            'per_page': per_page
        }

    @staticmethod
    def parse_sorting(resource_type: str) -> Dict[str, str]:
        """
        Parse sorting parameters from request.

        Args:
            resource_type: Type of resource being sorted ('projects', 'tasks', 'requirements')

        Returns:
            Dict with 'sort' and 'order' keys

        Raises:
            QueryParseError: If sort parameters are invalid
        """
        sort_field = request.args.get('sort')
        sort_order = request.args.get('order', 'asc')

        # Validate sort field
        if sort_field:
            valid_fields = QueryParser.VALID_SORT_FIELDS.get(resource_type, [])
            if sort_field not in valid_fields:
                raise QueryParseError(
                    f'Invalid sort field: {sort_field}. '
                    f'Valid fields: {", ".join(valid_fields)}'
                )

        # Validate sort order
        if sort_order not in ['asc', 'desc']:
            raise QueryParseError('Sort order must be "asc" or "desc"')

        return {
            'sort': sort_field,
            'order': sort_order
        }

    @staticmethod
    def parse_filters(resource_type: str) -> Dict[str, Any]:
        """
        Parse filter parameters from request.

        Args:
            resource_type: Type of resource being filtered

        Returns:
            Dict of filter field -> value

        Raises:
            QueryParseError: If filter parameters are invalid
        """
        filters = {}
        valid_filters = QueryParser.VALID_FILTERS.get(resource_type, [])

        for field in valid_filters:
            value = request.args.get(field)
            if value:
                # Validate enum values
                if field == 'status':
                    if value not in QueryParser.VALID_VALUES['status']:
                        raise QueryParseError(
                            f'Invalid status: {value}. '
                            f'Valid values: {", ".join(QueryParser.VALID_VALUES["status"])}'
                        )
                elif field == 'priority':
                    # Check if it's a task priority or requirement priority
                    if resource_type == 'tasks':
                        if value not in QueryParser.VALID_VALUES['priority']:
                            raise QueryParseError(
                                f'Invalid priority: {value}. '
                                f'Valid values: {", ".join(QueryParser.VALID_VALUES["priority"])}'
                            )
                    elif resource_type == 'requirements':
                        if value not in QueryParser.VALID_VALUES['requirement_priority']:
                            raise QueryParseError(
                                f'Invalid priority: {value}. '
                                f'Valid values: {", ".join(QueryParser.VALID_VALUES["requirement_priority"])}'
                            )

                filters[field] = value

        return filters

    @staticmethod
    def parse_search() -> Dict[str, str]:
        """
        Parse search parameters from request.

        Returns:
            Dict with 'query' and 'type' keys

        Raises:
            QueryParseError: If search parameters are invalid
        """
        query = request.args.get('q', '').strip()
        search_type = request.args.get('type', 'all')

        if not query:
            raise QueryParseError('Search query (q) is required')

        valid_types = ['all', 'projects', 'tasks', 'requirements']
        if search_type not in valid_types:
            raise QueryParseError(
                f'Invalid search type: {search_type}. '
                f'Valid types: {", ".join(valid_types)}'
            )

        return {
            'query': query,
            'type': search_type
        }

    @staticmethod
    def apply_filters(data: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """
        Apply filters to a list of data dictionaries.

        Args:
            data: List of dictionaries to filter
            filters: Dict of field -> value filters

        Returns:
            Filtered list
        """
        if not filters:
            return data

        filtered = data
        for field, value in filters.items():
            if field in ['name', 'path']:
                # Partial match for text fields
                filtered = [
                    item for item in filtered
                    if value.lower() in str(item.get(field, '')).lower()
                ]
            else:
                # Exact match for enum fields
                filtered = [
                    item for item in filtered
                    if item.get(field) == value
                ]

        return filtered

    @staticmethod
    def apply_sorting(data: List[Dict], sort_field: Optional[str], sort_order: str) -> List[Dict]:
        """
        Apply sorting to a list of data dictionaries.

        Args:
            data: List of dictionaries to sort
            sort_field: Field to sort by
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Sorted list
        """
        if not sort_field:
            return data

        reverse = (sort_order == 'desc')

        # Handle priority sorting with custom order
        if sort_field == 'priority':
            priority_order = {'high': 0, 'medium': 1, 'low': 2}
            return sorted(
                data,
                key=lambda x: priority_order.get(x.get('priority', 'low'), 3),
                reverse=reverse
            )

        # Handle status sorting with custom order
        if sort_field == 'status':
            status_order = {'todo': 0, 'in_progress': 1, 'blocked': 2, 'done': 3}
            return sorted(
                data,
                key=lambda x: status_order.get(x.get('status', 'todo'), 4),
                reverse=reverse
            )

        # Default string sorting
        return sorted(
            data,
            key=lambda x: str(x.get(sort_field, '')).lower(),
            reverse=reverse
        )

    @staticmethod
    def apply_pagination(data: List[Dict], page: Optional[int], per_page: Optional[int]) -> tuple:
        """
        Apply pagination to a list of data dictionaries.

        Args:
            data: List of dictionaries to paginate
            page: Page number (1-indexed)
            per_page: Items per page

        Returns:
            Tuple of (paginated_data, pagination_metadata)
        """
        total = len(data)

        # If no pagination specified, return all data
        if page is None and per_page is None:
            return data, None

        # Set defaults
        page = page or 1
        per_page = per_page or 20

        # Calculate pagination
        start = (page - 1) * per_page
        end = start + per_page
        paginated = data[start:end]

        metadata = {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': (total + per_page - 1) // per_page
        }

        return paginated, metadata
