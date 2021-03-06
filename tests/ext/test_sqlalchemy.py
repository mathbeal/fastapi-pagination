from typing import Iterator

from fastapi import Depends, FastAPI
from pytest import fixture
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from fastapi_pagination import Page, PaginationParams
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination.limit_offset import Page as LimitOffsetPage
from fastapi_pagination.limit_offset import (
    PaginationParams as LimitOffsetPaginationParams,
)

from ..base import (
    BasePaginationTestCase,
    SafeTestClient,
    UserOut,
    limit_offset_params,
    page_params,
)
from ..utils import faker


@fixture(scope="session")
def engine(database_url):
    return create_engine(database_url)


@fixture(scope="session")
def SessionLocal(engine):
    return sessionmaker(autocommit=True, autoflush=True, bind=engine)


@fixture(scope="session")
def Base(engine):
    return declarative_base(bind=engine)


@fixture(scope="session")
def User(Base):
    class User(Base):
        __tablename__ = "users"

        id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(String, nullable=False)

    return User


@fixture(scope="session")
def app(Base, User, SessionLocal):
    app = FastAPI()

    @app.on_event("startup")
    def on_startup():
        Base.metadata.create_all()

        session = SessionLocal()

        session.add_all([User(name=faker.name()) for _ in range(100)])

        session.flush()
        session.close()

    def get_db() -> Iterator[Session]:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    @app.get("/implicit", response_model=Page[UserOut], dependencies=[Depends(page_params)])
    def route(db: Session = Depends(get_db)):
        return paginate(db.query(User))

    @app.get("/explicit", response_model=Page[UserOut])
    def route(params: PaginationParams = Depends(), db: Session = Depends(get_db)):
        return paginate(db.query(User), params)

    @app.get(
        "/implicit-limit-offset",
        response_model=LimitOffsetPage[UserOut],
        dependencies=[Depends(limit_offset_params)],
    )
    def route(db: Session = Depends(get_db)):
        return paginate(db.query(User))

    @app.get("/explicit-limit-offset", response_model=LimitOffsetPage[UserOut])
    def route(params: LimitOffsetPaginationParams = Depends(), db: Session = Depends(get_db)):
        return paginate(db.query(User), params)

    return app


class TestSQLAlchemy(BasePaginationTestCase):
    @fixture(scope="session")
    def client(self, app):
        with SafeTestClient(app) as c:
            yield c

    @fixture(scope="session")
    def entities(self, SessionLocal, User):
        session = SessionLocal()
        try:
            return session.query(User).all()
        finally:
            session.close()
