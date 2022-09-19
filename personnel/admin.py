from django.contrib import admin

from personnel.models import (
    Department,
    Position,
    Employee,
    Bonus,
    SickTime,
    Vacation,
)

admin.site.register(Department)
admin.site.register(Position)
admin.site.register(Employee)
admin.site.register(Bonus)
admin.site.register(SickTime)
admin.site.register(Vacation)
