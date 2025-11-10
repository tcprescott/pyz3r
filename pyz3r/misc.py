"""Miscellaneous utility functions for pyz3r."""

from typing import Iterator, TypeVar, Tuple, List, Dict, Any, Generator
import bisect

T = TypeVar('T')


def chunk(iterator: Iterator[T], count: int) -> Generator[Tuple[T, ...], None, None]:
    """Split an iterator into chunks of a specified size.
    
    Args:
        iterator: The iterator to chunk.
        count: The size of each chunk.
        
    Yields:
        Tuples containing `count` items from the iterator.
    """
    itr = iter(iterator)
    while True:
        try:
            yield tuple([next(itr) for i in range(count)])
        except StopIteration:
            return


def seek_patch_data(patches: List[Dict[str, List[int]]], offset: int, num_bytes: int) -> List[int]:
    """Seek and extract bytes from patch data at a specific offset.
    
    Args:
        patches: List of patch dictionaries containing offset-to-bytes mappings.
        offset: The byte offset to seek to.
        num_bytes: Number of bytes to extract.
        
    Returns:
        A list of bytes at the specified offset.
        
    Raises:
        ValueError: If the offset is not found in the patches.
    """
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


def convert_randomizer_settings(web_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Convert web/JS randomizer presets to API compatible presets.

    There is no API from ALTTPR website to provide API compatible generation
    configs. There is, however, an API for web/JS compatible presets. This
    method converts those presets so that they can be used with this library.
    
    Args:
        web_dict: Dictionary containing web/JS format settings.
        
    Returns:
        Dictionary in API-compatible format.
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

def mergedicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Generator[Tuple[str, Any], None, None]:
    """Recursively merge two dictionaries.
    
    Values from dict2 override values from dict1. Nested dictionaries are merged recursively.
    Inspired by https://stackoverflow.com/questions/7204805/how-to-merge-dictionaries-of-dictionaries
    
    Args:
        dict1: First dictionary.
        dict2: Second dictionary (takes precedence).
        
    Yields:
        Tuples of (key, merged_value) for all keys in both dictionaries.
    """
    for k in set(dict1.keys()).union(dict2.keys()):
        if k in dict1 and k in dict2:
            if isinstance(dict1[k], dict) and isinstance(dict2[k], dict):
                yield (k, dict(mergedicts(dict1[k], dict2[k])))
            else:
                # If one of the values is not a dict, you can't continue merging it.
                # Value from second dict overrides one in first and we move on.
                yield (k, dict2[k])
                # Alternatively, replace this with exception raiser to alert you of value conflicts
        elif k in dict1:
            yield (k, dict1[k])
        else:
            yield (k, dict2[k])