from ninja import Router
from ninja.security import HttpBearer
from django.contrib.auth import authenticate
from django.db import IntegrityError
from .models import User
from .schemas import (
    RegisterSchema,
    LoginSchema,
    MagicLinkRequestSchema,
    MagicLinkVerifySchema,
    UserSchema,
    TokenSchema,
    MessageSchema,
    PasswordResetRequestSchema,
    PasswordResetConfirmSchema,
    AccountDeleteSchema,
)
from .utils import (
    create_access_token,
    get_user_from_token,
    create_magic_link,
    send_magic_link_email,
    verify_magic_link,
    create_password_reset_token,
    send_password_reset_email,
    verify_password_reset_token,
)

router = Router()


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            user = get_user_from_token(token)
            return user
        except (ValueError, User.DoesNotExist):
            return None


@router.post("/register", response={201: TokenSchema, 400: MessageSchema})
def register(request, payload: RegisterSchema):
    """Register a new user with email and password."""
    try:
        user = User.objects.create_user(
            email=payload.email.lower(),
            password=payload.password,
        )

        access_token = create_access_token(user)

        return 201, {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "is_active": user.is_active,
                "date_joined": user.date_joined,
            }
        }

    except IntegrityError:
        return 400, {"message": "User with this email already exists"}


@router.post("/login", response={200: TokenSchema, 401: MessageSchema})
def login(request, payload: LoginSchema):
    """Login with email and password."""
    user = authenticate(
        request,
        username=payload.email.lower(),
        password=payload.password
    )

    if user is None:
        return 401, {"message": "Invalid email or password"}

    if not user.is_active:
        return 401, {"message": "Account is inactive"}

    access_token = create_access_token(user)

    return 200, {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "is_active": user.is_active,
            "date_joined": user.date_joined,
        }
    }


@router.post("/magic-link/request", response={200: MessageSchema, 404: MessageSchema})
def request_magic_link(request, payload: MagicLinkRequestSchema):
    """Request a magic link to be sent to the user's email."""
    try:
        user = User.objects.get(email=payload.email.lower(), is_active=True)
    except User.DoesNotExist:
        return 404, {"message": "No active account found with this email"}

    magic_link = create_magic_link(user)

    frontend_url = request.headers.get('Origin', 'http://localhost:4321')
    send_magic_link_email(user, magic_link, frontend_url)

    return 200, {"message": "Magic link sent to your email"}


@router.post("/magic-link/verify", response={200: TokenSchema, 400: MessageSchema})
def verify_magic_link_endpoint(request, payload: MagicLinkVerifySchema):
    """Verify a magic link token and log the user in."""
    try:
        user = verify_magic_link(payload.token)
    except ValueError as e:
        return 400, {"message": str(e)}

    access_token = create_access_token(user)

    return 200, {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "is_active": user.is_active,
            "date_joined": user.date_joined,
        }
    }


@router.get("/me", response={200: UserSchema, 401: MessageSchema}, auth=AuthBearer())
def get_current_user(request):
    """Get the current authenticated user."""
    return 200, {
        "id": request.auth.id,
        "email": request.auth.email,
        "is_active": request.auth.is_active,
        "date_joined": request.auth.date_joined,
    }


@router.post("/password-reset/request", response={200: MessageSchema, 404: MessageSchema})
def request_password_reset(request, payload: PasswordResetRequestSchema):
    """Request a password reset email."""
    try:
        user = User.objects.get(email=payload.email.lower(), is_active=True)
    except User.DoesNotExist:
        # Don't reveal if email exists or not for security
        return 200, {"message": "If an account exists with this email, a password reset link has been sent"}

    reset_token = create_password_reset_token(user)
    frontend_url = request.headers.get('Origin', 'http://localhost:4321')
    send_password_reset_email(user, reset_token, frontend_url)

    return 200, {"message": "If an account exists with this email, a password reset link has been sent"}


@router.post("/password-reset/confirm", response={200: MessageSchema, 400: MessageSchema})
def confirm_password_reset(request, payload: PasswordResetConfirmSchema):
    """Confirm password reset and set new password."""
    try:
        user = verify_password_reset_token(payload.token, payload.new_password)
        return 200, {"message": "Password has been reset successfully"}
    except ValueError as e:
        return 400, {"message": str(e)}


@router.post("/account/delete", response={200: MessageSchema, 400: MessageSchema, 401: MessageSchema}, auth=AuthBearer())
def delete_account(request, payload: AccountDeleteSchema):
    """Soft delete the current user's account (requires password confirmation)."""
    user = request.auth

    # Verify password
    if not user.check_password(payload.password):
        return 401, {"message": "Invalid password"}

    # Soft delete the account
    user.soft_delete()

    return 200, {"message": "Account has been deleted successfully"}
