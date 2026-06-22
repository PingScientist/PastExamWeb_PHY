"""drop_gemini_api_key_from_users

Revision ID: 5f0d3fb0a1c9
Revises: 01075665e961
Create Date: 2026-06-22 19:36:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "5f0d3fb0a1c9"
down_revision: Union[str, Sequence[str], None] = "01075665e961"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("users", "gemini_api_key")


def downgrade() -> None:
    op.add_column(
        "users",
        sa.Column("gemini_api_key", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )
