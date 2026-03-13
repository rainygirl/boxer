from ninja import NinjaAPI
from accounts.auth import JWTAuth
from accounts.api import router as accounts_router
from projects.api import router as projects_router
from tasks.api import router as tasks_router
from notifications.api import router as notifications_router

api = NinjaAPI(
    title='Boxer API',
    version='1.0.0',
    auth=JWTAuth(),
    urls_namespace='api',
)

api.add_router('/auth/', accounts_router, tags=['Auth'])
api.add_router('/projects/', projects_router, tags=['Projects'])
api.add_router('/tasks/', tasks_router, tags=['Tasks'])
api.add_router('/notifications/', notifications_router, tags=['Notifications'])
