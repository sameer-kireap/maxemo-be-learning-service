"""BaseRepository providing list_generic and common persistence operations."""

from collections.abc import Callable
from typing import Any, Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.schema.filter import FilterParams
from app.utils.repository.query_builder import QueryBuilder

T = TypeVar("T", bound=Any)


class BaseRepository(Generic[T]):  # noqa: UP046
    """Generic base repository for all entity repositories."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_generic(
        self,
        filter_params: FilterParams,
        filter_map: dict[str, Any],
        search_columns: list[Any],
        sort_map: dict[str, Any],
        default_sort: Any,  # noqa: ANN401
        model: type[T],
        extra_query_builder: Callable[[QueryBuilder, FilterParams], QueryBuilder] | None = None,
        options: list[Any] | None = None,
    ) -> tuple[list[T], int]:
        """Generic list method applying filters, search, sorting, and pagination in one query."""
        builder = QueryBuilder(model)

        if options:
            for opt in options:
                builder.query = builder.query.options(opt)

        builder.apply_filters(filter_params, filter_map)
        builder.apply_search(filter_params.search, search_columns)

        if extra_query_builder:
            builder = extra_query_builder(builder, filter_params)

        builder.apply_sorting(
            filter_params.sort_by,
            filter_params.sort_order,
            sort_map,
            default_sort,
        )

        builder.add_total_count_window()
        builder.apply_pagination(filter_params.offset, filter_params.limit)

        result = await self.db.execute(builder.query)
        rows = result.all()

        if not rows:
            return [], 0

        items: list[T] = [row[0] for row in rows]
        has_total = hasattr(rows[0], "total_count")
        total_count: int = int(rows[0].total_count) if has_total else len(items)

        return items, total_count
