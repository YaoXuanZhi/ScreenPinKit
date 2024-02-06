from enum import Enum
from typing import TypeVar, Generic, List, Type
from entities import Entity


class ComponentQuantity(Enum):
    """Available quantity of a Component type on a single Entity."""
    ONE = 0
    MANY = 1


class Component:
    """Base class for defining a Component of the ecs architecture."""

    def __init__(self, entity: Entity) -> None:
        """Create a new Component instance."""
        self.m_entity: Entity = entity

    @classmethod
    def quantity(cls) -> ComponentQuantity:
        """Get the quantity of the Component type a single Entity can bear."""
        return ComponentQuantity.ONE

    @property
    def entity(self) -> Entity:
        """Get the Entity to which the current Component is attached to."""
        return self.m_entity

    @property
    def entityValue(self) -> int:
        """Get the value of the Entity to which the current Component is attached to."""
        return self.m_entity.value

    def hasValidEntity(self) -> bool:
        """Check if the Entity owning the Component is valid."""
        return self.m_entity.isValid

    def __str__(self):
        return '{} {}'.format(__class__, str(self.m_entity))


TConcreteComponent = TypeVar('TConcreteComponent', bound=Component)


class ComponentFactory(Generic[TConcreteComponent]):
    """Factory to generate and destroy Component instances."""

    def __init__(self, memberClass: Type[TConcreteComponent]) -> None:
        """Create a new ComponentFactory instance.
         There should be only one ComponentFactory in a application."""
        self.m_components: List[TConcreteComponent] = []
        self.m_memberClass = memberClass

    def create(self, entity: Entity) -> TConcreteComponent:
        """Create a new Component instance and store it in the ComponentFactory."""
        newComponent: TConcreteComponent = self.m_memberClass(entity)
        self.m_components.append(newComponent)
        return newComponent

    def countComponents(self) -> int:
        """Get the amount of Components for all Entities."""
        return len(self.m_components)

    def allComponents(self):
        """Get all the Components from all Entities."""
        return self.m_components

    def components(self, entity: Entity) -> [TConcreteComponent]:
        """Get all the Components attached to an Entity."""
        return [component for component in self.m_components if component.entity == entity]

    def delete(self, entity: Entity) -> None:
        """Delete the Component instances bearing the entity and remove them from the ComponentFactory."""
        self.m_components = [component for component in self.m_components if component.entity != entity]

    def debug(self) -> None:
        """Show the content of the ComponentFactory in a terminal."""
        print(colored("[Debug] {}Factory: it contains {} components".format(
                self.m_memberClass.__name__,
                len(self.m_components)
            ), 'cyan')
        )

        for component in self.m_components:
            print(colored('{} = {} attached to {}'.format(
                    self.m_memberClass.__name__,
                    component,
                    component.entityValue
                ), 'cyan')
            )