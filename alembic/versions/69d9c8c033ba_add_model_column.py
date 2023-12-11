"""add model column

Revision ID: 69d9c8c033ba
Revises: 852420ae1f09
Create Date: 2023-12-10 16:37:38.642224

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '69d9c8c033ba'
down_revision: Union[str, None] = '852420ae1f09'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
