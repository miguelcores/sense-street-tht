from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class UploadStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Upload(BaseModel):
    id: str
    customer_id: str
    filename: str
    file_type: str
    file_size: int
    upload_timestamp: datetime
    status: UploadStatus
    progress: int = 0
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None

class UploadResponse(BaseModel):
    message: str
    uploads: List[Upload]

class UploadListResponse(BaseModel):
    uploads: List[Upload]
    total: int
    skip: int
    limit: int

class UploadStatusResponse(BaseModel):
    upload_id: str
    status: UploadStatus
    progress: int
    processing_started_at: Optional[datetime]
    processing_completed_at: Optional[datetime]

class ProcessingResult(BaseModel):
    result_type: str
    data: Dict[str, Any]
    created_at: datetime

class ProcessingResultsResponse(BaseModel):
    upload_id: str
    results: List[ProcessingResult]

class DashboardSummaryResponse(BaseModel):
    total_uploads: int
    pending_uploads: int
    completed_uploads: int
    failed_uploads: int
    total_files_size: int
    uploads_today: int

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str