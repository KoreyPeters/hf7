import pendulum
from django.db.models import DateTimeField, DateField


class PendulumDateTimeField(DateTimeField):
    def to_python(self, value):
        dt = super(PendulumDateTimeField, self).to_python(value)
        if dt:
            return pendulum.instance(dt)
        else:
            return dt

    def value_to_string(self, obj):
        value = self.value_from_object(obj)

        if isinstance(value, pendulum.DateTime):
            return value.format("YYYY-MM-DD HH:mm:ss")

        return "" if value is None else value.isoformat()


class PendulumDateField(DateField):
    def to_python(self, value):
        dt = super(PendulumDateField, self).to_python(value)
        if dt:
            return pendulum.instance(dt)
        else:
            return dt

    def value_to_string(self, obj):
        value = self.value_from_object(obj)

        if isinstance(value, pendulum.Date):
            return value.format("YYYY-MM-DD")

        return "" if value is None else value.isoformat()
