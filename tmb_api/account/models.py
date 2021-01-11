import six

from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from tmb_test.TMB_test_git.tmb_api.encryption import AESCipher
from tmb_test.TMB_test_git.tmb_api.tmb_api import settings


class Account(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator() if six.PY3 else ASCIIUsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )

    email = models.EmailField(
        verbose_name='Email address',
        max_length=255,
        db_index=True,
        null=True,
        blank=True
    )

    title = models.CharField(max_length=64, blank=True)
    first_name = models.CharField(max_length=120, db_index=True, blank=True)
    middle_name = models.CharField(max_length=120, db_index=True, blank=True)
    last_name = models.CharField(max_length=120, db_index=True, blank=True)
    id_card = models.CharField(max_length=255, blank=True, null=True)  # Encrypt

    @property
    def id_card_decrypt(self):
        if self.id_card:
            if len(self.id_card) > 13:
                try:
                    return AESCipher(settings.SECRET_KEY).decrypt(self.id_card)
                except:
                    return '-'
            else:
                return self.id_card
        return '-'
