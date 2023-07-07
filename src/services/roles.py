from typing import List

from fastapi import Depends, HTTPException, status, Request

from src.database.models import User, Role
from src.services.auth import auth_service


class RoleAccess:
    def __init__(self, allowed_roles: List[Role]):
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request, current_user: User = Depends(auth_service.get_current_user)):
        """
        The __call__ function is the function that will be called when a user tries to access an endpoint.
        It takes in two arguments: request and current_user. The request argument is the Request object, which contains
        information about the HTTP request made by a client (e.g., headers, body).
        The current_user argument is provided by FastAPI's Depends() dependency injection system and it represents our
        User object.

        :param self: Access the class attributes
        :param request: Request: Get the request information
        :param current_user: User: Get the current user from the auth_service
        :return: A list of all the users in the database
        :doc-author: Trelent
        """
        print(request.method, request.url)
        print(f'User role {current_user.roles}')
        print(f'Allowed roles: {self.allowed_roles}')
        if current_user.roles not in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Operation is forbidden')
