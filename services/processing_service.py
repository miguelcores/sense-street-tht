import asyncio
import json
import csv
import io
from typing import List
from datetime import datetime
import random

from models.database import db
from models.schemas import ProcessingResult, UploadStatus

class ProcessingService:
    
    async def trigger_processing(self, upload_id: str, customer_id: str) -> bool:
        """Trigger processing for an upload"""
        upload = await db.get_upload(upload_id, customer_id)
        if not upload:
            return False
        
        # Start background processing
        asyncio.create_task(self._process_file(upload_id))
        return True
    
    async def get_results(self, upload_id: str, customer_id: str) -> List[ProcessingResult]:
        """Get processing results for an upload"""
        upload = await db.get_upload(upload_id, customer_id)
        if not upload:
            return []
        
        return await db.get_processing_results(upload_id)
    
    async def _process_file(self, upload_id: str):
        """Background processing simulation"""
        try:
            # Update status to processing
            await db.update_upload_status(upload_id, UploadStatus.PROCESSING, 0)
            
            # Get file content
            file_content = await db.get_file_content(upload_id)
            upload = db.uploads[upload_id]  # Direct access for demo
            
            # Simulate processing with progress updates
            for progress in [25, 50, 75]:
                await asyncio.sleep(1)  # Simulate work
                await db.update_upload_status(upload_id, UploadStatus.PROCESSING, progress)
            
            # Process the file based on type
            if upload.file_type == 'json':
                results = await self._process_json_file(file_content, upload.filename)
            elif upload.file_type == 'csv':
                results = await self._process_csv_file(file_content, upload.filename)
            else:
                raise ValueError(f"Unsupported file type: {upload.file_type}")
            
            # Save results
            await db.save_processing_results(upload_id, results)
            
            # Mark as completed
            await db.update_upload_status(upload_id, UploadStatus.COMPLETED, 100)
            
        except Exception as e:
            # Mark as failed
            await db.update_upload_status(upload_id, UploadStatus.FAILED, 0)
            print(f"Processing failed for {upload_id}: {str(e)}")
    
    async def _process_json_file(self, content: bytes, filename: str) -> List[ProcessingResult]:
        """Process JSON chat file"""
        data = json.loads(content.decode('utf-8'))
        
        # Mock processing results
        results = []
        
        # Message count analysis
        if isinstance(data, list):
            message_count = len(data)
            participants = set()
            
            for item in data:
                if isinstance(item, dict) and 'sender' in item:
                    participants.add(item['sender'])
        else:
            message_count = 1
            participants = {"unknown"}
        
        results.append(ProcessingResult(
            result_type="message_analysis",
            data={
                "total_messages": message_count,
                "unique_participants": len(participants),
                "participants": list(participants),
                "average_message_length": random.randint(20, 100)
            },
            created_at=datetime.utcnow()
        ))
        
        # Mock sentiment analysis
        results.append(ProcessingResult(
            result_type="sentiment_analysis",
            data={
                "overall_sentiment": random.choice(["positive", "neutral", "negative"]),
                "sentiment_score": round(random.uniform(-1, 1), 2),
                "positive_messages": random.randint(0, message_count//2),
                "negative_messages": random.randint(0, message_count//4),
                "neutral_messages": random.randint(0, message_count//2)
            },
            created_at=datetime.utcnow()
        ))
        
        return results
    
    async def _process_csv_file(self, content: bytes, filename: str) -> List[ProcessingResult]:
        """Process CSV chat file"""
        text_content = content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(text_content))
        
        rows = list(csv_reader)
        results = []
        
        # Basic statistics
        results.append(ProcessingResult(
            result_type="csv_analysis",
            data={
                "total_rows": len(rows),
                "columns": list(rows[0].keys()) if rows else [],
                "file_size_kb": len(content) / 1024
            },
            created_at=datetime.utcnow()
        ))
        
        # Mock conversation metrics
        results.append(ProcessingResult(
            result_type="conversation_metrics",
            data={
                "peak_activity_hour": random.randint(9, 17),
                "most_active_day": random.choice(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]),
                "conversation_threads": random.randint(5, 20),
                "average_response_time_minutes": random.randint(2, 30)
            },
            created_at=datetime.utcnow()
        ))
        
        return results