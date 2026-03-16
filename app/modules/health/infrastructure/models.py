from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import Base


class AlembicModel(Base):
    __tablename__ = "alembic_version"

    version_num: Mapped[str] = mapped_column(String, primary_key=True)
