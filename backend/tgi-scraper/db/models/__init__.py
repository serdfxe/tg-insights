from math import isnan
from sqlalchemy import orm


class Base(orm.DeclarativeBase):
    """Base database model."""

    def as_dict(self):
        return {
            c.name: (
                getattr(self, c.name)
                if not (
                    isinstance(getattr(self, c.name), float)
                    and isnan(getattr(self, c.name))
                )
                else None
            )
            for c in self.__table__.columns
        }
