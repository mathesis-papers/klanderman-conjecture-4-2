import hashlib
from itertools import combinations, product
import json
from pathlib import Path


def quaternion_product(left, right):
    unit_table = (
        ((0, 0), (1, 0), (2, 0), (3, 0)),
        ((1, 0), (0, 1), (3, 0), (2, 1)),
        ((2, 0), (3, 1), (0, 1), (1, 0)),
        ((3, 0), (2, 0), (1, 1), (0, 1)),
    )
    unit, sign = unit_table[left // 2][right // 2]
    return 2 * unit + ((left % 2 + right % 2 + sign) % 2)


def cyclic_product(order):
    return lambda left, right: (left + right) % order


def symmetric_three_product(left, right):
    left_rotation, left_reflection = divmod(left, 2)
    right_rotation, right_reflection = divmod(right, 2)
    rotation = (left_rotation + (-1) ** left_reflection * right_rotation) % 3
    return 2 * rotation + (left_reflection + right_reflection) % 2


def check_group(name, order, multiply):
    elements = tuple(range(order))
    assert all(multiply(0, element) == element == multiply(element, 0)
               for element in elements)
    assert all(multiply(multiply(left, middle), right) ==
               multiply(left, multiply(middle, right))
               for left, middle, right in product(elements, repeat=3))
    inverse = {element: next(candidate for candidate in elements
                            if multiply(element, candidate) == 0 ==
                            multiply(candidate, element))
               for element in elements}
    subgroups = []
    for size in range(1, order + 1):
        for members in combinations(elements, size):
            subgroup = frozenset(members)
            if 0 in subgroup and all(multiply(left, right) in subgroup
                                     for left, right in product(subgroup, repeat=2)):
                assert all(inverse[element] in subgroup for element in subgroup)
                subgroups.append(subgroup)
    subgroups.sort(key=lambda subgroup: (len(subgroup), sorted(subgroup)))
    bottom, top = frozenset({0}), frozenset(elements)
    identities = {(subgroup, subgroup) for subgroup in subgroups}
    complete = {(source, target) for source, target in product(subgroups, repeat=2)
                if source <= target}
    proper_star = identities | {(bottom, target) for target in subgroups if target != top}
    full_star = identities | {(bottom, target) for target in subgroups}
    proper_complete = identities | {(source, target) for source, target in complete
                                    if target != top}
    intermediate = proper_complete | {(bottom, top)}
    conjugates = {
        (element, subgroup): frozenset(multiply(multiply(element, member), inverse[element])
                                       for member in subgroup)
        for element in elements for subgroup in subgroups
    }

    def is_transfer(relation):
        return (
            identities <= relation <= complete
            and all((source, target) in relation
                    for source, middle in relation for lower, target in relation
                    if middle == lower)
            and all((source & restriction, restriction) in relation
                    for source, target in relation for restriction in subgroups
                    if restriction <= target)
            and all((conjugates[element, source], conjugates[element, target]) in relation
                    for element in elements for source, target in relation)
        )

    def is_saturated(relation):
        return all((middle, target) in relation for source, target in relation
                   for middle in subgroups if source <= middle <= target)

    def compatible(relation, lesser=proper_star):
        return lesser <= relation and all(
            (other, target) in relation
            for source, target in lesser for other in subgroups
            if other <= target and (source & other, source) in relation
        )

    def connected_components(relation):
        unvisited = set(subgroups)
        components = []
        while unvisited:
            component = {next(iter(unvisited))}
            while True:
                expanded = component | {target for source, target in relation
                                        if source in component}
                expanded |= {source for source, target in relation if target in component}
                if expanded == component:
                    break
                component = expanded
            unvisited -= component
            components.append(component)
        return components

    for relation in [proper_star, full_star, proper_complete, intermediate]:
        assert is_transfer(relation)
    assert is_saturated(proper_complete)
    assert compatible(proper_complete) and compatible(intermediate)
    optional = sorted(complete - identities,
                      key=lambda edge: (len(edge[0]), sorted(edge[0]),
                                        len(edge[1]), sorted(edge[1])))
    systems = []
    for mask in range(1 << len(optional)):
        relation = identities | {edge for position, edge in enumerate(optional)
                                 if mask & (1 << position)}
        if is_transfer(relation):
            systems.append(relation)
    generating_systems = [relation for relation in systems
                          if proper_star | {(bottom, top)} <= relation]
    generated = set.intersection(*generating_systems)
    assert generated == full_star
    hull = set.intersection(*(relation for relation in systems
                              if proper_star <= relation and is_saturated(relation)))
    assert hull == proper_complete
    compatible_systems = [relation for relation in systems if compatible(relation)]
    lesser_simply_paired = all(relation == hull or relation == complete
                              for relation in compatible_systems)
    proper_subgroups = [subgroup for subgroup in subgroups if subgroup != top]
    ideal_partners = []
    for mask in range(1 << len(proper_subgroups)):
        ideal = {subgroup for position, subgroup in enumerate(proper_subgroups)
                 if mask & (1 << position)}
        downward = all(lower in ideal for upper in ideal for lower in subgroups
                       if lower <= upper)
        invariant = all(conjugates[element, subgroup] in ideal
                        for element in elements for subgroup in ideal)
        if downward and invariant:
            partner = proper_complete | {(subgroup, top) for subgroup in ideal}
            assert is_transfer(partner)
            ideal_partners.append(partner)
    assert {frozenset(relation) for relation in ideal_partners} == {
        frozenset(relation) for relation in compatible_systems}
    assert [relation for relation in compatible_systems if is_saturated(relation)] == [
        relation for relation in systems if relation in [proper_complete, complete]]
    top_isolated_systems = []
    for lesser in systems:
        if not lesser <= proper_complete:
            continue
        top_isolated_systems.append(lesser)
        saturated_hull = set.intersection(*(relation for relation in systems
                                            if lesser <= relation and is_saturated(relation)))
        assert saturated_hull <= proper_complete
        assert compatible(intermediate, lesser)
        partners = [relation for relation in systems if compatible(relation, lesser)]
        assert all(relation in [saturated_hull, complete] for relation in partners) == (len(subgroups) == 2)
        top_generators = {(source, target) for source, target in lesser if target == top}
        cosaturated_closure = set.intersection(*(relation for relation in systems
                                                if top_generators <= relation))
        assert (cosaturated_closure == lesser) == (lesser == identities)
    for lesser in systems:
        if len(connected_components(lesser)) == 1:
            saturated_hull = set.intersection(*(relation for relation in systems
                                                if lesser <= relation and is_saturated(relation)))
            assert saturated_hull == complete
            assert [relation for relation in systems if compatible(relation, lesser)] == [complete]
    chains = [(lower, upper) for lower, upper in product(subgroups, repeat=2)
              if bottom < lower < upper < top]
    assert compatible(generated) == (not chains)
    assert lesser_simply_paired == (len(subgroups) == 2)
    admissible = []
    for lesser in systems:
        source_hypotheses = {frozenset(component) for component in connected_components(lesser)} == {
            frozenset({top}), frozenset(set(subgroups) - {top})}
        assert source_hypotheses == (proper_star <= lesser <= proper_complete)
        if not proper_star <= lesser <= proper_complete:
            continue
        admissible.append(lesser)
        ordinary = set.intersection(*(relation for relation in systems
                                      if lesser | {(bottom, top)} <= relation))
        assert ordinary == lesser | {(bottom, top)}
        saturated_hull = set.intersection(*(relation for relation in systems
                                            if lesser <= relation and is_saturated(relation)))
        assert saturated_hull == proper_complete
        partners = [relation for relation in systems if compatible(relation, lesser)]
        assert partners == [relation for relation in systems if proper_complete <= relation]
        assert compatible(ordinary, lesser) == is_saturated(lesser) == (lesser == proper_complete)
        assert all(relation in [saturated_hull, complete] for relation in partners) == (len(subgroups) == 2)
    components = connected_components(proper_star)
    assert {frozenset(component) for component in components} == {
        frozenset({top}), frozenset(set(subgroups) - {top})}
    assert all(source == top for source, target in proper_star if target == top)
    result = {
        'group': name,
        'order': order,
        'subgroups': [sorted(subgroup) for subgroup in subgroups],
        'transfer_systems': len(systems),
        'two_component_top_isolated_systems': len(admissible),
        'all_top_isolated_systems': len(top_isolated_systems),
        'conjugation_invariant_proper_subgroup_ideals': len(ideal_partners),
        'saturated_compatible_partners': 2,
        'proper_star_arrows': len(proper_star),
        'generated_arrows': len(generated),
        'hull_arrows': len(hull),
        'intermediate_arrows': len(intermediate),
        'connected_component_sizes': sorted(map(len, components)),
        'compatible_extensions': len(compatible_systems),
        'ordinary_generated_compatible': compatible(generated),
        'proper_star_lesser_simply_paired': lesser_simply_paired,
        'proper_strict_chains': [[sorted(lower), sorted(upper)] for lower, upper in chains],
    }
    if name == 'Q8':
        center, cyclic_four = frozenset({0, 1}), frozenset({0, 1, 2, 3})
        assert bottom < center < cyclic_four < top
        assert (bottom, cyclic_four) in proper_star
        assert (bottom & center, bottom) in generated
        assert (center, cyclic_four) not in generated
        result['compatibility_obstruction'] = {
            'ambient': sorted(cyclic_four), 'lower': sorted(bottom),
            'test_subgroup': sorted(center), 'missing_arrow': [sorted(center), sorted(cyclic_four)]}
    return result


def main():
    results = [check_group('Q8', 8, quaternion_product)]
    for order in [2, 4, 8, 6]:
        results.append(check_group('C' + str(order), order, cyclic_product(order)))
    results.append(check_group('C2xC2', 4, lambda left, right: left ^ right))
    results.append(check_group('S3', 6, symmetric_three_product))
    assert [result['ordinary_generated_compatible'] for result in results] == [False, True, True, False, True, True, True]
    assert [result['proper_star_lesser_simply_paired'] for result in results] == [False, True, False, False, False, False, False]
    print(json.dumps({'arithmetic': 'exact integer arithmetic',
                      'coverage': 'All subgroups and inclusion-refining relations on Q8, C2, C4, C8, C6, C2xC2, S3; component classification, all top-isolated systems, connected systems and conjugation-invariant order ideals.',
                      'checker_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      'results': results}, indent=2))


if __name__ == '__main__':
    main()
