from typing import cast

from harness.collect import Row


# A row holding only the columns a test reads.
def partial_row(**cells: object) -> Row:
    return cast(Row, cells)
