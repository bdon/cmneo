from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def get_queryset(self):
        """Exclude soft-deleted users from default queryset"""
        return super().get_queryset().filter(deleted_at__isnull=True)

    def all_with_deleted(self):
        """Get all users including soft-deleted ones"""
        return super().get_queryset()

    def deleted_only(self):
        """Get only soft-deleted users"""
        return super().get_queryset().filter(deleted_at__isnull=False)

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email)

        # Check if email exists in non-deleted accounts
        if self.get_queryset().filter(email=email).exists():
            raise ValueError('A user with this email already exists')

        user = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, db_index=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.email

    @property
    def is_deleted(self):
        """Check if user is soft-deleted"""
        return self.deleted_at is not None

    def soft_delete(self):
        """Soft delete the user account"""
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save()

    def hard_delete(self):
        """Permanently delete the user (use with caution)"""
        super().delete()


class MagicLink(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='magic_links')
    token = models.CharField(max_length=255, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'magic_links'
        ordering = ['-created_at']

    def __str__(self):
        return f"Magic link for {self.user.email}"

    def is_valid(self):
        return (
            self.used_at is None and
            timezone.now() < self.expires_at
        )


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=255, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'password_reset_tokens'
        ordering = ['-created_at']

    def __str__(self):
        return f"Password reset token for {self.user.email}"

    def is_valid(self):
        return (
            self.used_at is None and
            timezone.now() < self.expires_at
        )
