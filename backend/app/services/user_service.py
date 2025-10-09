from app.repositories.user_repo import UserRepo, DuplicateUserError
from app.models.dto import UserCreateRequest, UserResponse

class EmailInUseError(Exception): ...
class ClerkIdInUseError(Exception): ...

class UserService:
    def __init__(self, repo: UserRepo):
        self.repo = repo

    def signup(self, payload: UserCreateRequest) -> UserResponse:
        # normalize inputs that require uniqueness
        email = payload.email.strip().lower()
        clerk_user_id = payload.clerk_user_id

        # pre-check for DB uniqueness, still enforced in repo
        if self.repo.get_by_email(email):
            raise EmailInUseError("This email is already being used!")
        
        if self.repo.get_by_clerk_id(clerk_user_id):
            raise ClerkIdInUseError("This account already exists!")

        user = self.repo.create(
            clerk_user_id=clerk_user_id,
            first_name=payload.first_name.strip(),
            last_name=payload.last_name.strip(),
            email=email,
        )
        return UserResponse.model_validate(user, from_attributes=True)