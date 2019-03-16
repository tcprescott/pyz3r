class misc:
    def chunk(iterator, count):
        itr = iter(iterator)
        while True:
            try:
                yield tuple([next(itr) for i in range(count)])
            except StopIteration:
                return