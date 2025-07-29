from typing import Dict, List, Optional
from datetime import datetime
import uuid
from .schemas import Upload, UploadStatus, ProcessingResult

class InMemoryDatabase:
    """Simple in-memory database for the demo"""
    
    def __init__(self):
        self.uploads: Dict[str, Upload] = {}
        self.file_contents: Dict[str, bytes] = {}
        self.processing_results: Dict[str, List[ProcessingResult]] = {}
    
    async def create_upload(self, customer_id: str, filename: str, 
                          file_content: bytes, file_size: int) -> Upload:
        upload_id = str(uuid.uuid4())
        file_type = filename.split('.')[-1].lower()
        
        upload = Upload(
            id=upload_id,
            customer_id=customer_id,
            filename=filename,
            file_type=file_type,
            file_size=file_size,
            upload_timestamp=datetime.utcnow(),
            status=UploadStatus.PENDING
        )
        
        self.uploads[upload_id] = upload
        self.file_contents[upload_id] = file_content
        return upload
    
    async def get_upload(self, upload_id: str, customer_id: str) -> Optional[Upload]:
        upload = self.uploads.get(upload_id)
        if upload and upload.customer_id == customer_id:
            return upload
        return None
    
    async def update_upload_status(self, upload_id: str, status: UploadStatus, 
                                 progress: int = 0) -> bool:
        if upload_id in self.uploads:
            upload = self.uploads[upload_id]
            upload.status = status
            upload.progress = progress
            
            if status == UploadStatus.PROCESSING and not upload.processing_started_at:
                upload.processing_started_at = datetime.utcnow()
            elif status == UploadStatus.COMPLETED:
                upload.processing_completed_at = datetime.utcnow()
                upload.progress = 100
                
            return True
        return False
    
    async def list_uploads(self, customer_id: str, skip: int = 0, 
                         limit: int = 100, status: Optional[str] = None) -> List[Upload]:
        customer_uploads = [
            upload for upload in self.uploads.values() 
            if upload.customer_id == customer_id
        ]
        
        if status:
            customer_uploads = [u for u in customer_uploads if u.status == status]
        
        # Sort by upload timestamp, newest first
        customer_uploads.sort(key=lambda x: x.upload_timestamp, reverse=True)
        
        return customer_uploads[skip:skip + limit]
    
    async def delete_upload(self, upload_id: str, customer_id: str) -> bool:
        upload = await self.get_upload(upload_id, customer_id)
        if upload:
            del self.uploads[upload_id]
            self.file_contents.pop(upload_id, None)
            self.processing_results.pop(upload_id, None)
            return True
        return False
    
    async def get_file_content(self, upload_id: str) -> Optional[bytes]:
        return self.file_contents.get(upload_id)
    
    async def save_processing_results(self, upload_id: str, 
                                    results: List[ProcessingResult]):
        self.processing_results[upload_id] = results
    
    async def get_processing_results(self, upload_id: str) -> List[ProcessingResult]:
        return self.processing_results.get(upload_id, [])

# Global database instance
db = InMemoryDatabase()