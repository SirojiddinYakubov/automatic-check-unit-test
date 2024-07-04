from django.conf import settings
from django.utils.translation import gettext_lazy as _

BIRTH_YEAR_ERROR_MSG = _("Tug'ilgan yili {min_year} dan katta va {max_year} dan kichik bo'lishi kerak.".format(min_year=settings.BIRTH_YEAR_MIN, max_year=settings.BIRTH_YEAR_MAX))
