from django.conf import settings
from django.utils.translation import gettext_lazy as _

BIRTH_YEAR_ERROR_MSG = _(f"Tug'ilgan yili {settings.BIRTH_YEAR_MIN} dan katta va {settings.BIRTH_YEAR_MAX} dan kichik bo'lishi kerak.")
