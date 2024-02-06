from entities import Entity, EntityFactory
from systems import System, Type, TConcreteComponent, TConcreteSystemProcessing
from jobs import Job


class World:
    """Entry class for using the ecs instances. Handles interactions between these instances as automatic data
    suppression. For example, it removes all the components attached to an entity when this one is deleted."""

    def __init__(self):
        """Create a new World instance."""
        self.m_entities: EntityFactory = EntityFactory()
        self.m_entityList: [Entity] = []
        self.m_systems: {str, System} = {}
        self.m_jobs: {str, Job} = {}

    def __del__(self):
        """Clear data on World destruction."""
        self.clear()

    def clear(self):
        """Clear all data of the current World."""
        while len(self.m_entityList) > 0:
            self.delete(self.m_entityList[0])

    def createEntity(self) -> Entity:
        """Create an Entity instance."""
        newEntity: Entity = self.m_entities.create()
        self.m_entityList.append(newEntity)
        return newEntity

    def system(
        self,
        name: str,
        componentClass: Type[TConcreteComponent] = None,
        processingClass: Type[TConcreteSystemProcessing] = None
    ) -> System:
        """Get a System by its name."""
        if name not in self.m_systems:
            if componentClass is not None and processingClass is not None:
                self.m_systems[name] = System(name, componentClass, processingClass)
        return self.m_systems[name]

    def addJob(self, jobName: str, systemNames: [str], threadCount: int = 4) -> None:
        """Get a Job used to run systems concurrently."""
        if jobName not in self.m_jobs:
            systems: [System] = [sys for sys in self.m_systems.values() if sys.name in systemNames]
            self.m_jobs[jobName] = Job(jobName, systems, max(1, threadCount))

    def delete(self, entity: Entity) -> None:
        """Delete an Entity and all its attached Components."""
        for name in self.m_systems:
            if self.m_entities.has(entity):
                self.m_systems[name].delete(entity)
        self.m_entities.delete(entity)

        try:
            self.m_entityList.remove(entity)
        except:
            pass

    def run(self):
        """Run all the registered Systems in the World."""
        for jobName in self.m_jobs:
            job: Job = self.m_jobs[jobName]
            job.execute()

            # Clear the entities before running the next job.
            clearEntitiesList: [Entity] = job.dropEntity
            for entity in clearEntitiesList:
                self.delete(entity)

    def stop(self) -> None:
        """Stop all the Jobs."""
        for jobName in self.m_jobs:
            job: Job = self.m_jobs[jobName]
            job.stop()

    def debug(self) -> None:
        """Debug the World instance."""
        self.m_entities.debug()
        for name in self.m_systems:
            self.m_systems[name].debug()