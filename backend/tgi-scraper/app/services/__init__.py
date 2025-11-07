from db.uow import UOW


class Service:
    def __init__(self, uow: UOW):
        self.uow: UOW = uow
