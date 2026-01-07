class DummyStore:
    _sid = None

    @staticmethod
    def sid(sid = None):

        if sid is not None:
            DummyStore._sid = sid

        return DummyStore._sid


