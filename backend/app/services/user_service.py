from app.repositories.user_repo import UserRepo, DuplicateUserError
from app.models.dto import UserCreateRequest, UserResponse

class EmailInUseError(Exception): ...
class UsernameInUseError(Exception): ...

class UserService:
    def __init__(self, repo: UserRepo):
        self.repo = repo

    def signup(self, payload: UserCreateRequest) -> UserResponse:
        # normalize inputs that require uniqueness
        email = payload.email.strip().lower()
        username = payload.username.strip().lower()

        # pre-check for DB uniqueness, still enforced in repo
        if self.repo.get_by_email(email):
            raise EmailInUseError("email already in use")
        if self.repo.get_by_username(username):
            raise UsernameInUseError("username already in use")

        phone_int = int(payload.phone_number)

        user = self.repo.create(
            first_name=payload.first_name.strip(),
            last_name=payload.last_name.strip(),
            username=username,
            password=payload.password,
            email=email,
            phone_number=phone_int,
        )
        return UserResponse.model_validate(user, from_attributes=True)