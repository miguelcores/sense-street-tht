from typing import List, Optional
from models.database import db
from models.schemas import Upload, DashboardSummaryResponse, UploadStatus
from datetime import datetime

class UploadService:
    
    async def create_upload(self, customer_id: str, filename: str, 
                          file_content: bytes, file_size: int) -> Upload:
        """Create a new upload record"""
        upload = await db.create_upload(customer_id, filename, file_content, file_size)
        
        # Auto-trigger processing
        from services.processing_service import ProcessingService
        processing_service = ProcessingService()
        await processing_service.trigger_processing(upload.id, customer_id)
        
        return upload
    
    async def get_upload(self, upload_id: str, customer_id: str) -> Optional[Upload]:
        """Get a specific upload"""
        return await db.get_upload(upload_id, customer_id)
    
    async def list_uploads(self, customer_id: str, skip: int = 0, 
                         limit: int = 100, status: Optional[str] = None) -> List[Upload]:
        """List uploads for a customer"""
        return await db.list_uploads(customer_id, skip, limit, status)
    
    async def delete_upload(self, upload_id: str, customer_id: str) -> bool:
        """Delete an upload"""
        return await db.delete_upload(upload_id, customer_id)
    
    async def get_customer_summary(self, customer_id: str) -> DashboardSummaryResponse:
        """Get summary statistics for a customer"""
        uploads = await self.list_uploads(customer_id, limit=1000)  # Get all uploads
        
        total_uploads = len(uploads)
        pending_uploads = len([u for u in uploads if u.status == UploadStatus.PENDING])
        completed_uploads = len([u for u in uploads if u.status == UploadStatus.COMPLETED])
        failed_uploads = len([u for u in uploads if u.status == UploadStatus.FAILED])
        total_files_size = sum(u.file_size for u in uploads)
        
        # Uploads today
        today = datetime.utcnow().date()
        uploads_today = len([
            u for u in uploads 
            if u.upload_timestamp.date() == today
        ])
        
        return DashboardSummaryResponse(
            total_uploads=total_uploads,
            pending_uploads=pending_uploads,
            completed_uploads=completed_uploads,
            failed_uploads=failed_uploads,
            total_files_size=total_files_size,
            uploads_today=uploads_today
        )