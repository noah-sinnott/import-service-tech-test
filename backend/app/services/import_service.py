from sqlalchemy.orm import Session
from typing import List
import asyncio
import random

from ..database import SessionLocal
from ..config import settings
from ..repositories.job_repository import JobRepository
from ..repositories.item_repository import ItemRepository
from .external_api_service import ExternalApiService


class ImportService:
    """Service for handling data import operations"""
    
    @staticmethod
    async def process_import_job(job_id: int, sources: List[str]) -> None:
        """Background task to process import job"""
        db = SessionLocal()
        job_repo = JobRepository(db)
        
        try:
            item_repo = ItemRepository(db)
            external_api = ExternalApiService()
            
            job = job_repo.get_by_id(job_id)
            if not job:
                return
            
            job_repo.update_status(job_id, "Running")
            
            # Simulate random failure - 1 in 10 jobs fail
            if random.randint(1, 10) == 1:
                await asyncio.sleep(2)
                raise Exception("Random test failure - 10% chance simulation")
            
            # Simulate delay
            await asyncio.sleep(settings.simulate_delay_seconds)
            
            # Process each source
            for source in sources:
                if source == "products":
                    products = await external_api.fetch_products(limit=30)
                    for product in products:
                        item_repo.create(
                            job_id=job.id,
                            source="products",
                            remote_id=product.get("id"),
                            payload=product
                        )
                        db.commit()
                        # Add delay between items to show progress
                        await asyncio.sleep(0.2)
                elif source == "carts":
                    carts = await external_api.fetch_carts(limit=20)
                    for cart in carts:
                        item_repo.create(
                            job_id=job.id,
                            source="carts",
                            remote_id=cart.get("id"),
                            payload=cart
                        )
                        db.commit()
                        # Add delay between items to show progress
                        await asyncio.sleep(0.2)
            
            job_repo.update_status(job_id, "Completed")
            
        except Exception as e:
            # Rollback any pending transaction before updating status
            db.rollback()
            # Delete any partially imported items from failed attempt
            item_repo.delete_by_job(job_id)
            job_repo.update_status(job_id, "Failed", str(e))
        finally:
            db.close()
