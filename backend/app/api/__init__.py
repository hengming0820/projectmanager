from .auth import router as auth_router
from .users import router as users_router
from .projects import router as projects_router
from .tasks import router as tasks_router
from .performance import router as performance_router
from .menu import router as menu_router
from .roles import router as roles_router
from .collaboration import router as collaboration_router
from .upload import router as upload_router
from .articles import router as articles_router
from .files import router as files_router

# 导出所有路由对象，方便在 main.py 中使用
auth = auth_router
users = users_router
projects = projects_router
tasks = tasks_router
performance = performance_router
menu = menu_router
roles = roles_router
collaboration = collaboration_router
upload = upload_router
articles = articles_router
files = files_router