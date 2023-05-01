from ulid import ULID

import pendulum
from proto.datetime_helpers import DatetimeWithNanoseconds


def default(obj):
    if isinstance(obj, pendulum.DateTime):
        return obj.to_rfc3339_string()
    elif isinstance(obj, DatetimeWithNanoseconds):
        return obj.isoformat()
    elif isinstance(obj, ULID):
        return obj.str
