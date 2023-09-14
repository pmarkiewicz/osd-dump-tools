from bisect import bisect_left


def find_slots(sequence: list[int], start: int, end: int) -> list[int]:
    """
        return list of subslots from sequence in range start:end
    """
    n1 = bisect_left(sequence, start)
    n2 = bisect_left(sequence, end)

    if n1 == 0 and n2 == 0:
        return []
    if n1 == 0:
        if start == sequence[0]:
            # special case when first element is same as start
            # return sequence[n1:n2]
            return list(range(n1, n2))
        else:
            # return [None] + sequence[n1:n2]
            return [None] + list(range(n1, n2))
    if n2 == 0:
        print('Missing end sequence')
        return []

    if n1 >= len(sequence):
        return []
    
    if start == sequence[n1]:
        # another special case first element is same as start
        return list(range(n1, n2))

    # return sequence[n1-1:n2]
    return list(range(n1-1, n2))
