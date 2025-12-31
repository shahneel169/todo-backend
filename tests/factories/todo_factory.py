from datetime import date, timedelta

import factory
from app.schemas.todo import TodoCreate, TodoUpdate
from factory import Factory


class TodoCreateFactory(Factory):
    "Factory for creating TodoCreate schemas"

    class Meta:
        model = TodoCreate

    title = factory.Faker("sentence", nb_words=4)
    completed = False
    due_date = factory.LazyFunction(lambda: date.today() + timedelta(days=7))


class TodoUpdateFactory(Factory):
    "Factory for creating TodoUpdate schema"

    class Meta:
        model = TodoUpdate

    title = factory.Faker("sentence", nb_words=4)
    completed = factory.Faker("boolean")
    due_date = factory.LazyFunction(lambda: date.today() + timedelta(days=7))
