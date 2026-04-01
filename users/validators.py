import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class AtLeastOneDigitPasswordValidator:
    def validate(self, password, user=None):
        if not re.search(r"\d", password or ""):
            raise ValidationError(
                _("Password must contain at least one digit (0-9)."),
                code="password_no_digit",
            )

    def get_help_text(self):
        return _("Your password must contain at least one digit (0-9).")
