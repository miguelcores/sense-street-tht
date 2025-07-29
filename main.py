# File: main.py
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import List, Optional
from datetime import datetime
import json
import csv
import io

from config import get_settings
from models.schemas import *
from services.upload_service import UploadService
from services.processing_service import ProcessingService
from dependencies import get_upload_service, get_processing_service

# Initialize FastAPI app
app = FastAPI(
    title="Chat Upload API",
    description="A SaaS API for uploading and processing chat files",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

settings = get_settings()

# Health Check Endpoint
@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0"
    )

# Upload Endpoints
@app.post("/api/v1/uploads", response_model=UploadResponse)
async def upload_files(
    customer_id: str = Form(...),
    files: List[UploadFile] = File(...),
    upload_service: UploadService = Depends(get_upload_service)
):
    """Upload one or multiple chat files"""
    try:
        uploads = []
        
        for file in files:
            # Validate file
            if not file.filename.endswith(('.json', '.csv')):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported file type: {file.filename}"
                )
            
            # Read and validate file content
            content = await file.read()
            if len(content) > settings.max_file_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"File {file.filename} exceeds maximum size limit"
                )
            
            # Validate file format
            await _validate_chat_file(content, file.filename)
            
            # Create upload record
            upload = await upload_service.create_upload(
                customer_id=customer_id,
                filename=file.filename,
                file_content=content,
                file_size=len(content)
            )
            uploads.append(upload)
        
        return UploadResponse(
            message=f"Successfully uploaded {len(uploads)} files",
            uploads=uploads
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/api/v1/uploads", response_model=UploadListResponse)
async def list_uploads(
    customer_id: str,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    upload_service: UploadService = Depends(get_upload_service)
):
    """List uploads for a customer with pagination and filtering"""
    uploads = await upload_service.list_uploads(
        customer_id=customer_id,
        skip=skip,
        limit=limit,
        status=status
    )
    
    return UploadListResponse(
        uploads=uploads,
        total=len(uploads),
        skip=skip,
        limit=limit
    )

@app.get("/api/v1/uploads/{upload_id}/status", response_model=UploadStatusResponse)
async def get_upload_status(
    upload_id: str,
    customer_id: str,
    upload_service: UploadService = Depends(get_upload_service)
):
    """Get processing status of a specific upload"""
    upload = await upload_service.get_upload(upload_id, customer_id)
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    return UploadStatusResponse(
        upload_id=upload_id,
        status=upload.status,
        progress=upload.progress,
        processing_started_at=upload.processing_started_at,
        processing_completed_at=upload.processing_completed_at
    )

@app.get("/api/v1/uploads/{upload_id}/results", response_model=ProcessingResultsResponse)
async def get_processing_results(
    upload_id: str,
    customer_id: str,
    processing_service: ProcessingService = Depends(get_processing_service)
):
    """Get processed results for an upload"""
    results = await processing_service.get_results(upload_id, customer_id)
    if not results:
        raise HTTPException(status_code=404, detail="Results not found")
    
    return ProcessingResultsResponse(
        upload_id=upload_id,
        results=results
    )

@app.post("/api/v1/uploads/{upload_id}/process")
async def trigger_processing(
    upload_id: str,
    customer_id: str,
    processing_service: ProcessingService = Depends(get_processing_service)
):
    """Manually trigger processing for an upload"""
    success = await processing_service.trigger_processing(upload_id, customer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    return {"message": "Processing started", "upload_id": upload_id}

@app.delete("/api/v1/uploads/{upload_id}")
async def delete_upload(
    upload_id: str,
    customer_id: str,
    upload_service: UploadService = Depends(get_upload_service)
):
    """Delete an upload and its associated data"""
    success = await upload_service.delete_upload(upload_id, customer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    return {"message": "Upload deleted successfully"}

@app.get("/api/v1/dashboard/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    customer_id: str,
    upload_service: UploadService = Depends(get_upload_service)
):
    """Get summary statistics for dashboard"""
    summary = await upload_service.get_customer_summary(customer_id)
    return summary

# Utility function for file validation
async def _validate_chat_file(content: bytes, filename: str):
    """Validate that the uploaded file is a valid chat file"""
    try:
        if filename.endswith('.json'):
            data = json.loads(content.decode('utf-8'))
            if not isinstance(data, (list, dict)):
                raise ValueError("JSON must be an object or array")
        elif filename.endswith('.csv'):
            text_content = content.decode('utf-8')
            csv_reader = csv.reader(io.StringIO(text_content))
            # Just check if it's valid CSV
            list(csv_reader)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format in {filename}: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
