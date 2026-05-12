from typing import Type, List, Optional, Generic

from database.database import Database, T


class RepositoryBase(Generic[T]):

    def __init__(self, database: Database, model_class: Type[T]):
        self.db = database
        self.model_class: Type[T] = model_class

    def add_many(self, model_instances: List[T]) -> List[T]:
        try:
            with self.db.get_session() as session:
                session.add_all(model_instances)
                session.commit()
                for instance in model_instances:
                    session.refresh(instance)
                return model_instances
        except Exception as e:
            print(f"Error al agregar las instancias: {e}")
            raise

    def add(self, model_instance: T) -> T:
        try:
            with self.db.get_session() as session:
                session.add(model_instance)
                session.commit()
                session.refresh(model_instance)
                return model_instance
        except Exception as e:
            print(f"Error al agregar la instancia: {e}")
            raise

    def get_by_id(self, id: int) -> Optional[T]:
        try:
            with self.db.get_session() as session:
                return session.get(self.model_class, id)
        except Exception as e:
            print(f"Error al obtener la instancia por ID: {e}")
            raise

    def get_all(self) -> List[T]:
        try:
            with self.db.get_session() as session:
                return session.query(self.model_class).all()
        except Exception as e:
            print(f"Error al obtener todas las instancias: {e}")
            raise

    def update(self, model_instance: T) -> T:
        try:
            with self.db.get_session() as session:
                merged = session.merge(model_instance)
                session.commit()
                session.refresh(merged)
                return merged
        except Exception as e:
            print(f"Error al actualizar la instancia: {e}")
            raise

    def delete(self, model_instance: T) -> None:
        try:
            with self.db.get_session() as session:
                attached = (
                    session.merge(model_instance)
                    if model_instance not in session
                    else model_instance
                )
                session.delete(attached)
                session.commit()
        except Exception as e:
            print(f"Error al eliminar la instancia: {e}")
            raise
