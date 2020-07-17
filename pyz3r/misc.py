import bisect


def chunk(iterator, count):
    itr = iter(iterator)
    while True:
        try:
            yield tuple([next(itr) for i in range(count)])
        except StopIteration:
            return


def seek_patch_data(patches, offset, num_bytes):
    offsetlist = []
    for patch in patches:
        for key, value in patch.items():
            offsetlist.append(int(key))
    offsetlist_sorted = sorted(offsetlist)
    i = bisect.bisect_left(offsetlist_sorted, offset)
    if i:
        if offsetlist_sorted[i] == offset:
            seek = str(offset)
            for patch in patches:
                if seek in patch:
                    return patch[seek][:num_bytes]
        else:
            left_slice = offset - offsetlist_sorted[i - 1]
            for patch in patches:
                seek = str(offsetlist_sorted[i - 1])
                if seek in patch:
                    return patch[seek][left_slice:left_slice + num_bytes]
    raise ValueError


def convert_randomizer_settings(web_dict):
    """
    Convert web/JS randomizer presets to API compatible presets

    There is no API from ALTTPR website to provide API compatible generation
    configs.  There is, however, an API for web/JS compatible presets.  This
    method converts those presets so that they can be used with this library.
    """
    return {
            "glitches": web_dict.get("glitches_required"),
            "item_placement": web_dict.get("item_placement"),
            "dungeon_items": web_dict.get("dungeon_items"),
            "accessibility": web_dict.get("accessibility"),
            "goal": web_dict.get("goal"),
            "crystals": {
                "ganon": web_dict.get("ganon_open"),
                "tower": web_dict.get("tower_open"),
                },
            "mode": web_dict.get("world_state"),
            "entrances": web_dict.get("entrance_shuffle"),
            "hints": web_dict.get("hints"),
            "weapons": web_dict.get("weapons"),
            "item": {
                "pool": web_dict.get("item_pool"),
                "functionality": web_dict.get("item_functionality"),
                },
            "lang": "en",
            "enemizer": {
                "boss_shuffle": web_dict.get("boss_shuffle"),
                "enemy_shuffle": web_dict.get("enemy_shuffle"),
                "enemy_damage": web_dict.get("enemy_damage"),
                "enemy_health": web_dict.get("enemy_health"),
                }
           }
