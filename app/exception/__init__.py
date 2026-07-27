"""Application exceptions."""

import uuid


class NotFoundError(Exception):
    def __init__(self, entity: str, entity_id: uuid.UUID | int | str) -> None:
        super().__init__(f"{entity} not found: {entity_id}")
        self.entity = entity
        self.entity_id = entity_id


class DuplicateError(Exception):
    def __init__(self, entity: str, field: str, value: str) -> None:
        super().__init__(f"{entity} already exists with {field}={value!r}")
        self.entity = entity
        self.field = field
        self.value = value


class InvalidOptionIndexError(Exception):
    """selected_option_index is out of range for the question's options list."""

    def __init__(self, index: int, options_count: int) -> None:
        super().__init__(
            f"selected_option_index={index} is out of range "
            f"for question with {options_count} options"
        )
        self.index = index
        self.options_count = options_count
