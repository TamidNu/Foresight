from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.dto import UserCreateRequest, UserResponse
from app.repositories.database import get_db
from app.repositories.user_repo import UserRepo, DuplicateUserError
from app.services.user_service import UserService, EmailInUseError, UsernameInUseError

router = APIRouter(prefix="/users", tags=["users"])

def _svc(db: Session = Depends(get_db)) -> UserService:
    return UserService(UserRepo(db))

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: UserCreateRequest, svc: UserService = Depends(_svc)):
    try:
        return svc.signup(payload)
    except EmailInUseError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except UsernameInUseError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except DuplicateUserError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))