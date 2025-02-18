import uuid

def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except:
        return False


def get_applicable_filters(
    filters,
    POSSIBLE_DIRECT_FILTERS = None,
    POSSIBLE_INDIRECT_FILTERS = None,
):
    if POSSIBLE_DIRECT_FILTERS is None:
        POSSIBLE_DIRECT_FILTERS = ()
    if POSSIBLE_INDIRECT_FILTERS is None:
        POSSIBLE_INDIRECT_FILTERS = ()
    direct_filters = {}
    indirect_filters = {}
    for key, val in filters.items():
        if key in POSSIBLE_DIRECT_FILTERS:
            direct_filters[key] = val
        if key in POSSIBLE_INDIRECT_FILTERS:
            indirect_filters[key] = val
    for type in [
        "id",
        "status",
    ]:
        if type in direct_filters:
            if isinstance(direct_filters[type], str):
                if not is_valid_uuid(direct_filters[type]):
                    del direct_filters[type]
            elif isinstance(direct_filters[type], list):
                for key in direct_filters[type]:
                    if isinstance(key, int):
                        continue
                    if not is_valid_uuid(key):
                        direct_filters[type].remove(key)

    return (direct_filters, indirect_filters)
