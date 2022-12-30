import ulid
from sesame.packers import BasePacker


class Packer(BasePacker):
    @staticmethod
    def pack_pk(user_pk, **kwargs):
        return user_pk.bytes

    @staticmethod
    def unpack_pk(data, **kwargs):
        return ulid.from_bytes(data[:16]), data[16:]
