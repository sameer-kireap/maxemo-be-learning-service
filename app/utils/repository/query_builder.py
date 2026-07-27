"""QueryBuilder helper for constructing dynamic SQLAlchemy queries."""

from typing import Any

from sqlalchemy import Select, asc, desc, func, or_, select

from app.schema.filter import FilterParams


class QueryBuilder:
    """Builds filtered, searched, sorted, and paginated SQLAlchemy select queries."""

    def __init__(self, model: type[Any]) -> None:
        self.model = model
        self.query: Select[Any] = select(model)

    def apply_filters(
        self,
        filter_params: FilterParams,
        filter_map: dict[str, Any],
    ) -> "QueryBuilder":
        for key, column in filter_map.items():
            val = getattr(filter_params, key, None)
            if val is not None:
                if isinstance(val, str):
                    self.query = self.query.where(column.ilike(f"%{val}%"))
                elif isinstance(val, list):
                    if val:
                        self.query = self.query.where(column.in_(val))
                else:
                    self.query = self.query.where(column == val)
        return self

    def apply_search(
        self,
        search_term: str | None,
        search_columns: list[Any],
    ) -> "QueryBuilder":
        if search_term and search_columns:
            pattern = f"%{search_term}%"
            conditions = [column.ilike(pattern) for column in search_columns]
            self.query = self.query.where(or_(*conditions))
        return self

    def apply_sorting(
        self,
        sort_by: str | None,
        sort_order: str | None,
        sort_map: dict[str, Any],
        default_sort: Any,  # noqa: ANN401
    ) -> "QueryBuilder":
        column = sort_map.get(sort_by) if sort_by else default_sort
        if column is None:
            column = default_sort

        direction = desc if (sort_order and sort_order.lower() == "desc") else asc
        self.query = self.query.order_by(direction(column))
        return self

    def apply_pagination(self, offset: int, limit: int) -> "QueryBuilder":
        self.query = self.query.offset(offset).limit(limit)
        return self

    def add_total_count_window(self) -> "QueryBuilder":
        self.query = self.query.add_columns(func.count().over().label("total_count"))
        return self
