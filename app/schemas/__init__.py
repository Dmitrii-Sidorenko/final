from .user import (
    User,
    UserBase,
    UserCreate,
    UserInDBBase,
    UserUpdate,
    UserUpdateWithPasswordCheck,
    UserWithProjects,
    ChangePassword,
    Token,
)
from .project import (
    Project,
    ProjectBase,
    ProjectCreate,
    ProjectInDBBase,
    ProjectUpdate,
    ProjectFilter,
)

# Вызываем model_rebuild после импорта всех схем
UserWithProjects.model_rebuild()
Project.model_rebuild()