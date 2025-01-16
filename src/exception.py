from fastapi import HTTPException, status


class InactiveUserException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive. Please check your account."
        )

class InternalServerErrorException(HTTPException):
    def __init__(self, error: Exception):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error occurred during service: {str(error)}"
        )
