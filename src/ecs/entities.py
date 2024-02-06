class Entity:
    """Obscur ID type for an Entity."""

    # Class members.
    CurrentID: int = 0
    AvailableIDs: set = set()

    # Object methods.
    def __init__(self, value: int) -> None:
        """Creation of a new ID instance."""
        self.m_value: int = value

    def __del__(self) -> None:
        """Destruction of the ID instance."""
        self.m_value = None

    @property
    def isValid(self) -> bool:
        """Check if the ID is valid (ie. with a defined value) or not (None)."""
        return self.m_value is not None

    @property
    def value(self) -> int:
        """Get the value of an ID."""
        return self.m_value

    # Class methods.
    @staticmethod
    def Generate() -> 'Entity':
        """Generate a new ID either by incrementing the CurrentID or getting an
        ID from the AvailableIDs list."""
        if len(Entity.AvailableIDs) == 0:
            newID = Entity.CurrentID
            Entity.CurrentID += 1
            return Entity(newID)
        else:
            return Entity(Entity.AvailableIDs.pop())

    @staticmethod
    def Free(entity: 'Entity') -> None:
        """Free an ID by keeping its value in AvailableIDs and setting it to
        None, making it invalid."""
        if not entity.m_value in Entity.AvailableIDs:
            Entity.AvailableIDs.add(entity.m_value)
            entity.m_value = None
        else:
            raise ValueError("ID already used! {}".format(Entity.AvailableIDs))

    # Operators and converters.
    def __eq__(self, other) -> bool:
        """Test if two IDs are equal."""
        return self.m_value == other.m_value

    def __ne__(self, other) -> bool:
        """Test if two IDs are different."""
        return self.m_value != other.m_value

    def __str__(self):
        """Convert the current ID to string representation"""
        return "EntityID #{}".format(self.m_value)


class EntityFactory:
    """Factory to generate and destroy Entity instances."""

    def __init__(self) -> None:
        """Create a new EntityFactory instance. There should be only one EntityFactory in a application."""
        self.m_entities: [int] = []

    def create(self) -> Entity:
        """Create a new Entity instance and store it in the EntityFactory."""
        newEntity: Entity = Entity.Generate()
        self.m_entities.append(newEntity.value)
        self.m_entities.sort()
        return newEntity

    def delete(self, entity: Entity) -> None:
        """Delete an Entity instance and remove it from the EntityFactory."""
        try:
            self.m_entities.remove(entity.value)
            Entity.Free(entity)
        except:
            return

    def has(self, entity: Entity) -> bool:
        """Check if the given Entity exists."""
        return entity.value in self.m_entities

    def debug(self) -> None:
        """Show the content of the EntityFactory in a terminal."""
        print(colored("[Debug] EntityFactory: {}".format(self.m_entities), 'green'))
