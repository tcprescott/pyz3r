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
