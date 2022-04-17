from context.base import Base, engine


def initialize_context() -> None:
    Base.metadata.create_all(engine)

    # If necessary, some entities can be added to the context here.
