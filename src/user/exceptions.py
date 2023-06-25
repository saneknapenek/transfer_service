from typing import Any, Dict, Optional

from fastapi import HTTPException, status



class UserNotFound(HTTPException):
    
    def __init__(self, headers: Dict[str, str] | None = None) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
            headers=headers
        )
