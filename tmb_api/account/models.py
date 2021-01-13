import six

from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from .encryption import AESCipher, SECRET_KEY, AUTH_USER_MODEL, SESSION_ENGINE


from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class AccountManager(BaseUserManager):

    def create_user(self, username, password):
        if username is None:
            raise ValueError('The given username must be set')

        user = self.model(
            username=username
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, is_accepted_active_consent=True):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """

        user = self.create_user(username, password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator() if six.PY3 else ASCIIUsernameValidator()
    USERNAME_FIELD = 'username'
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
    code = models.CharField(max_length=32, db_index=True, blank=True, null=True, default=None)
    title = models.CharField(max_length=64, blank=True)
    first_name = models.CharField(max_length=120, db_index=True, blank=True)
    middle_name = models.CharField(max_length=120, db_index=True, blank=True)
    last_name = models.CharField(max_length=120, db_index=True, blank=True)
    id_card = models.CharField(max_length=255, blank=True, null=True)  # Encrypt
    department = models.CharField(max_length=255, blank=True, default='', null=True)
    salary = models.CharField(max_length=255, db_index=True)
    phone = models.CharField(max_length=10, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    is_admin = models.BooleanField(default=False)

    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    datetime_create = models.DateTimeField(auto_now_add=True, db_index=True)
    datetime_update = models.DateTimeField(auto_now=True, db_index=True)

    objects = AccountManager()

    USERNAME_FIELD = 'username'

    class Meta:
        ordering = ['-is_active', '-id']

    @property
    def id_card_decrypt(self):
        if self.id_card:
            if len(self.id_card) > 13:
                try:
                    return AESCipher(SECRET_KEY).decrypt(self.id_card)
                except:
                    return '-'
            else:
                return self.id_card
        return '-'


class MemberType(models.Model):
    TYPE_CHOICES = (
        (1, 'Silver'),
        (2, 'Gold'),
        (3, 'Platinum'),
        (9001, 'hyper_diamond')
    )

    account = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    type = models.IntegerField(choices=TYPE_CHOICES, default=1)
    datetime_create = models.DateTimeField(auto_now_add=True, db_index=True)
    datetime_update = models.DateTimeField(auto_now=True, db_index=True)


class Session(models.Model):
    account = models.ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=models.CASCADE)
    session_key = models.CharField(max_length=255, db_index=True)
    token = models.TextField(null=True, blank=True)
    datetime_create = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        default_permissions = ()
        ordering = ['-datetime_create']

    @staticmethod
    def push(account, session_key, token=None):
        from importlib import import_module
        # single sign on toggle
        is_single = True
        if is_single:
            session = Session.objects.filter(account=account).first()
            if session is not None:
                if session.session_key != session_key:
                    session_store = import_module(SESSION_ENGINE).SessionStore
                    s = session_store(session_key=session.session_key)
                    s.delete()
                    session.session_key = session_key
                    session.token = token
                    session.save()
            else:
                Session.objects.create(account=account, session_key=session_key, token=token)
        else:
            Session.objects.create(account=account, session_key=session_key, token=token)

    @staticmethod
    def remove(account_id, session_key=None):
        from importlib import import_module
        from django.conf import settings
        # single sign on toggle
        is_single = True
        session_store = import_module(settings.SESSION_ENGINE).SessionStore
        if is_single or session_key is None:
            for session in Session.objects.filter(account_id=account_id):
                _session = session_store(session.session_key)
                _session.delete()
                session.delete()
        else:
            for session in Session.objects.filter(account_id=account_id, session_key=session_key):
                _session = session_store(session.session_key)
                _session.delete()
                session.delete()
