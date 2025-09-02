from . import configuration


def binary_is_413(binary_hash) -> int:
    return get_binary_hash_index(binary_hash) >= 0


def binary_is_520(binary_hash) -> int:
    return get_binary_hash_index(binary_hash) >= 1


def binary_is_561(binary_hash) -> int:
    return get_binary_hash_index(binary_hash) >= 2


def binary_is_602(binary_hash) -> int:
    return get_binary_hash_index(binary_hash) >= 3


def get_binary_hash_index(binary_hash) -> int:
    # get the index of current hash
    return list(configuration.KNOWN_BINARY_HASH.keys()).index(binary_hash)
