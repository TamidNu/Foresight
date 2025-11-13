from fastapi import APIRouter, HTTPException, status

from app.models.dto import PricingRequest, PricingResponse
from app.services.experiments_pricing_engine import ExperimentsPricingEngine

router = APIRouter(prefix="/pricing", tags=["pricing"])


@router.post("/quote", response_model=PricingResponse)
def quote(req: PricingRequest):
    # Validate from_ <= to
    if req.from_ > req.to:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Start date must be before or equal to end date"
        )
    
    # Validate max range (90 days)
    date_range = (req.to - req.from_).days
    if date_range > 90:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Date range cannot exceed 90 days. Requested range: {date_range} days"
        )
    
    # Call ExperimentsPricingEngine and convert date objects to ISO format strings
    engine = ExperimentsPricingEngine()
    items, model_version = engine.quote(
        hotel_id=req.hotel_id,
        room_type_code=req.room_type_code,
        start_date=req.from_.isoformat(),
        end_date=req.to.isoformat()
    )
    
    # Map to PricingResponse DTO
    return PricingResponse(
        items=items,
        modelVersion=model_version
    )