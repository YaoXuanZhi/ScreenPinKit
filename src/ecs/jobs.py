import random
import threading
from entities import Entity
from systems import System

class ThreadJob(threading.Thread):
    """A thread for running Job."""

    def __init__(
        self,
        condition: threading.Condition,
        syncBarrier: threading.Barrier
    ) -> None:
        """Create a new ThreadJob instance."""
        threading.Thread.__init__(self)
        self.m_condition: threading.Condition = condition
        self.m_syncBarrier: threading.Barrier = syncBarrier
        self.m_continue: bool = True
        self.m_systems: {System} = {}
        self.m_fromToComponents: {System, [int, int]} = {}
        self.m_dropEntities: [Entity] = []

    def setProcessedSystems(self, systems: [System]) -> None:
        """Add a System to be processed by the ThreadJob."""
        self.m_systems = dict.fromkeys(systems)

    def setFromToComponents(self, system: System, fromIndex: int, toIndex: int) -> None:
        """Set the limits of execution of the thread for each System."""
        if system in self.m_systems:
            self.m_fromToComponents[system] = [fromIndex, toIndex]

    def stop(self) -> None:
        """Stop the thread as soon as possible."""
        self.m_continue = False

    def run(self) -> None:
        """Method representing the thread’s activity. Inherited from the parent class Thread."""
        while self.m_continue:
            with self.m_condition:
                self.m_condition.wait()
            self.processSystems()
            self.m_syncBarrier.wait()

    def processSystems(self) -> None:
        """Process the systems in the component index bounds."""
        self.m_dropEntities.clear()

        for system in self.m_fromToComponents:
            fromIndex: int = self.m_fromToComponents[system][0]
            toIndex: int = self.m_fromToComponents[system][1]
            system.process(fromIndex, toIndex)
            self.m_dropEntities.extend(system.processing.dropEntities)

    @property
    def dropEntities(self) -> [Entity]:
        """Get the Entities to be removed"""
        return self.m_dropEntities


class Job:
    """A Job groups systems that can run in parallel and threads to execute them."""

    def __init__(self, name: str, systems: [System], threadCount) -> None:
        """Create a new Job."""
        self.m_name: str = name
        self.m_condition: threading.Condition = threading.Condition()
        self.m_syncBarrier: threading.Barrier = threading.Barrier(threadCount + 1)
        self.m_systems: [System] = list(dict.fromkeys(systems))
        self.m_threads: [ThreadJob] = []
        self.m_dropEntities: [Entity] = []
        self.__createThreads(threadCount)
        self.__startThreads()

    def execute(self) -> None:
        """Execute the Job tasks."""
        self.m_dropEntities.clear()
        self.__defineThreadsCharge()

        # Make the threads run their loop.
        with self.m_condition:
            self.m_condition.notifyAll()

        # Wait all threads have done their loop.
        self.m_syncBarrier.wait()

        # Fill the drop entities list.
        for thread in self.m_threads:
            self.m_dropEntities.extend(thread.dropEntities)

    def stop(self) -> None:
        """Stop the Job and all its threads."""
        for thread in self.m_threads:
            thread.stop()

    @property
    def dropEntity(self) -> []:
        """Get the Entities that the World should delete."""
        return self.m_dropEntities

    @property
    def name(self) -> str:
        """Get the name of the Job."""
        return self.m_name

    def __createThreads(self, threadCount: int ) -> None:
        """Create the threads of the Job."""
        for index in range(0, threadCount):
            newThread: ThreadJob = ThreadJob(self.m_condition, self.m_syncBarrier)
            self.m_threads.append(newThread)

    def __startThreads(self) -> None:
        """Start the threads of the Job."""
        for thread in self.m_threads:
            thread.setProcessedSystems(self.m_systems)
            thread.start()

    def __defineThreadsCharge(self):
        """Define the work load for each thread on each system."""
        amountThreads: int = len(self.m_threads)
        threadCharge: {System, []} = {}

        for system in self.m_systems:
            amountComponents: int = system.amountComponents

            if system.multithreadable:
                amountComponentsPerThread: int = int(amountComponents / amountThreads)
                extraAmountComponents: int = int(amountComponents % amountThreads)
                threadIndexWithExtra: int = random.randrange(0, amountThreads)
                threadCharge[system] = [amountComponentsPerThread] * amountThreads
                threadCharge[system][threadIndexWithExtra] = amountComponentsPerThread + extraAmountComponents
            else:
                threadCharge[system] = [amountComponents]

        for system in threadCharge:
            fromIndex: int = 0
            toIndex: int = 0
            amountsComponentsPerThread: int = threadCharge[system]
            amountThreadsForSystem: int = len(threadCharge[system])

            for threadIndex in range(amountThreadsForSystem):
                thread: ThreadJob = self.m_threads[threadIndex]
                amountComponentsForThread: int = amountsComponentsPerThread[threadIndex]
                toIndex = toIndex + amountComponentsForThread
                thread.setFromToComponents(system, fromIndex, toIndex)
                fromIndex = fromIndex + amountComponentsForThread

    def __str__(self) -> str:
        """Convert the Job to string."""
        return self.m_name
