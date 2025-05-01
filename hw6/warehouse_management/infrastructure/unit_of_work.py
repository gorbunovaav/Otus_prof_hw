#todo
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from contextlib import AbstractContextManager
from domain.repositories import ProductRepository, OrderRepository
from infrastructure.repositories import SqlAlchemyProductRepository, SqlAlchemyOrderRepository


class AbstractUnitOfWork(ABC, AbstractContextManager):
    products: ProductRepository
    orders: OrderRepository

    @abstractmethod
    def commit(self):
        ...

    @abstractmethod
    def rollback(self):
        ...


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.session: Session | None = None

    def __enter__(self):
        self.session = self.session_factory()
        self.products = SqlAlchemyProductRepository(self.session)
        self.orders = SqlAlchemyOrderRepository(self.session)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
