from abc import abstractmethod
from typing import Any
from components import Component, ComponentQuantity, ComponentFactory, Entity, Generic, Type, TypeVar, TConcreteComponent


class SystemProcessing:
    """Class for processing the components of a System."""

    def __init__(self, components: ComponentFactory):
        """Create a new SystemProcessing instance."""
        self.m_components = components
        self.m_dropEntities: [Entity] = []

    def setData(self, data: Any, setterName: str) -> None:
        """Set data by calling the setter method by its name."""
        setter: 'function' = getattr(self, setterName)
        setter(data)

    def onDelete(self, entity: Entity) -> None:
        """Do something when an entity is removed."""
        return

    @abstractmethod
    def run(
        self,
        linkedSystems: {str, 'System'},
        fromIndex: int,
        toIndex: int
    ) -> None:
        """Perform the Components processing. Returns a list of Entity to be removed by the World."""
        pass

    @property
    def dropEntities(self) -> None:
        """Get the entities to be dropped."""
        return self.m_dropEntities


TConcreteSystemProcessing = TypeVar('TConcreteSystemProcessing', bound=SystemProcessing)


class System(Generic[TConcreteComponent]):
    """Base class for defining a System of the ECS architecture."""

    def __init__(
        self,
        name: str,
        componentClass: Type[TConcreteComponent],
        processingClass: Type[TConcreteComponent]
    ):
        """Create a new System instance."""
        self.m_name = name
        self.m_memberClass = componentClass
        self.m_linkedSystems: {str, System} = {}
        self.m_components = ComponentFactory(componentClass)
        self.m_processing = processingClass(self.m_components)
        self.m_multithreadable: bool = True

    def create(self, entity: Entity) -> TConcreteComponent:
        """If the Entity has no Component of the wanted type, it creates a new Component and attach it to the provided
        Entity.
        In the case where the Entity already has a Component of the wanted type and cannot have more than one Component
        of this type, it returns the previously created Component attached to that Entity."""
        quantity: ComponentQuantity = self.m_memberClass.quantity()

        if quantity is ComponentQuantity.ONE:
            listComponents: [Component] = self.m_components.components(entity)

            if len(listComponents) > 0:
                return listComponents[0]

        return self.m_components.create(entity)

    def delete(self, entity: Entity) -> None:
        """Delete the component(s) attached to an Entity."""
        self.m_processing.onDelete(entity)
        self.m_components.delete(entity)

    def link(self, linkedSystem) -> None:
        """Link another System to the current one."""
        name: str = linkedSystem.name
        self.m_linkedSystems[name] = linkedSystem

    def unlink(self, system):
        """Unlink a System from the current one."""
        name: str = system.name

        if name in self.m_linkedSystems:
            self.m_linkedSystems.pop(name)

    @property
    def amountComponents(self) -> int:
        """Get the amount of Components managed by the current System."""
        return self.m_components.countComponents()

    def components(self) -> [Component]:
        """Get all the Components managed by the current System."""
        return self.m_components.allComponents()

    def componentFor(self, entity: Entity) -> Component:
        """Get the first Component found for the given entity."""
        try:
            return next(c for c in self.components() if c.entityValue == entity)
        except:
            return None

    def allComponentsFor(self, entity: Entity) -> [Component]:
        """Get the Components found for the given entity."""
        foundComponents: [Component] = []
        listComponents: [Component] = self.m_components.allComponents()

        for component in listComponents:
            if component.entityValue == entity:
                foundComponents.append(component)

        return foundComponents

    def process(self, fromIndex: int, toIndex: int) -> [Entity]:
        """Run the Components processing. Returns a list of Entity to be removed by the World."""
        return self.m_processing.run(self.m_linkedSystems, fromIndex, toIndex)

    def setProcessingData(self, data: Any, setterName: str) -> None:
        """Set data to the system processing."""
        self.m_processing.setData(data, setterName)

    @property
    def name(self) -> str:
        """Get the name of the System."""
        return self.m_name

    @property
    def multithreadable(self) -> bool:
        """Used to know if the system can be multithreaded or not."""
        return self.m_multithreadable

    @multithreadable.setter
    def multithreadable(self, flag: bool) -> None:
        """Used to set if the system can be multithreaded or not."""
        self.m_multithreadable = flag

    @property
    def processing(self) -> SystemProcessing:
        """Get the SystemProcessing instance of the current System."""
        return self.m_processing

    def __str__(self) -> str:
        """Convert the System to string."""
        return self.m_name

    def debug(self) -> None:
        """Debug the System instance."""
        print(colored("[Debug] {}System".format(self.m_memberClass.__name__), 'magenta'))
        self.m_components.debug()