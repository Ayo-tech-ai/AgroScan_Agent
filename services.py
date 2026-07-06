# services.py
# This file is for additional service integrations.
# Currently, all services are handled in database.py.
# This file can be used for future service extensions.

from database import FarmRecordService
from config import DATABASE_NAME

# Export FarmRecordService for use in other modules
__all__ = ['FarmRecordService', 'DATABASE_NAME']
