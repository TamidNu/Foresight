from fastapi import APIRouter, Depends
# from app.models.dto import PricingRequest, PricingResponse # TODO: make these DTOs
# from app.services.ml_service import MLService # TODO: make this service

router = APIRouter(prefix="/pricing", tags=["pricing"])

@router.get("/price") # need to be implemented after you have the pricing service and the DTOs
def price(request: PricingRequest = Depends(PricingRequest)):
    return MLService.price(request)


@router.post("/quote", response_model=PricingResponse) # need to be implemented after you have the pricing service and the DTOs
def quote(req: PricingRequest, svc: MLService = Depends(get_ml_service)):
    return svc.quote(req)