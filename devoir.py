#code below need to be corrected to finish the function

from __future__ import annotations

from functools import reduce


Entity = int
Bitmask = int

class Component: ...
    


class System:
    def __call__(self, world: World, dt: float) -> None:
        ...


class World:
    EMPTY_BITMASK: Bitmask = 0b00000000

    def __init__(self) -> None:
        self.ents = list(range(100))
        self.ents_pool = list(self.ents)
        self.ents_comps = [self.EMPTY_BITMASK] * len(self.ents)

        self.comps = list(range(8))
        self.comps_pool = list(self.comps)
        self.comps_map: dict[type[Component], int] = {}

    def add_entity(self) -> Entity:
        if not len(self.ents_pool):
            raise IndexError(f"Maximum entity count reached {len(self.ents)}")

        ent = self.ents_pool.pop()
        self.ents_comps[ent] = self.EMPTY_BITMASK
        return ent

    def remove_entity(self, ent: Entity) -> None:
        self.ents_comps[ent] = self.EMPTY_BITMASK
        self.ents_pool.append(ent)

    def assign_component(self, ent: Entity, comp: type[Component]) -> None:
        self.ents_comps[ent] |= self.component_bitmask(comp)

    def register_component(self, comp: type[Component]) -> Bitmask:
        if not len(self.comps_pool):
            raise IndexError(f"Maximum component count reached {len(self.comps)}")
        self.comps_map[comp] = self.comps_map.get(comp, self.comps_pool.pop())
        return self.component_bitmask(comp)

    def component_bitmask(self, comp: type[Component]) -> Bitmask:
        return 1 << self.comps_map[comp]

    def query_bitmask(self, *query: type[Component]) -> Bitmask:
        return reduce(lambda a, b: a | b, (self.component_bitmask(comp) for comp in query))

    def query(self, *query: type[Component]) -> list[Entity]:
        bitmask = self.query_bitmask(*query)
        return [i for i, b in enumerate(self.ents_comps) if b ^ bitmask == 0]


if __name__ == "__main__":
    class Id(Component):
        def __init__(self, id: int) -> None:
            super().__init__()
            self.id = id


    class Name(Component):
        def __init__(self, name: str) -> None:
            super().__init__()
            self.name = name


    world = World()
    bm_id = world.register_component(Id)
    bm_na = world.register_component(Name)

    ent_0 = world.add_entity()
    world.assign_component(ent_0, Id)
    world.assign_component(ent_0, Name)

    ent_1 = world.add_entity()
    world.assign_component(ent_1, Id)

    ent_2 = world.add_entity()
    world.assign_component(ent_2, Name)

    ents = world.query(Id, Name)
    print(f"{world.query_bitmask(Id, Name):08b}")
    print(ent_0, ents)

    ents = world.query(Id)
    print(f"{world.query_bitmask(Id):08b}")
    print(ent_0, ent_1, ents)
