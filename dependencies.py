from functools import lru_cache
from services.upload_service import UploadService
from services.processing_service import ProcessingService

@lru_cache()
def get_upload_service():
    return UploadService()

@lru_cache()
def get_processing_service():
    return ProcessingService()