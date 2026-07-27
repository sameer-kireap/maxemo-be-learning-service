"""QueryBuilder helper for constructing dynamic SQLAlchemy queries."""

from typing import Any

from sqlalchemy import Select, asc, desc, func, or_, select

from app.constant.sort import SortOrder
from app.schema.filter import FilterParams


class QueryBuilder:
    """Builds filtered, searched, sorted, and paginated SQLAlchemy select queries."""

    def __init__(self, model: type[Any], base_query: Select[Any] | None = None) -> None:
        self.model = model
        self.query: Select[Any] = base_query if base_query is not None else select(model)

    def apply_filters(
        self,
        filter_params: FilterParams[Any],
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
        sort_by: Any,  # noqa: ANN401
        sort_order: SortOrder | str | None,
        sort_map: dict[Any, Any],
        default_sort: Any,  # noqa: ANN401
    ) -> "QueryBuilder":
        column = sort_map.get(sort_by) if sort_by is not None else None
        if column is None:
            column = default_sort

        is_desc = (
            sort_order == SortOrder.DESC
            or (isinstance(sort_order, str) and sort_order.lower() == "desc")
        )
        direction = desc if is_desc else asc
        self.query = self.query.order_by(direction(column))
        return self

    def apply_pagination(self, offset: int, limit: int) -> "QueryBuilder":
        self.query = self.query.offset(offset).limit(limit)
        return self

    def add_total_count_window(self) -> "QueryBuilder":
        self.query = self.query.add_columns(func.count().over().label("total_count"))
        return self

    def build(self) -> Select[Any]:
        return self.query
