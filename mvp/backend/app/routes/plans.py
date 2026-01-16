"""
Plans routes 
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from ..schemas.plans import PlanCreate,PlanResponse,PlanUpdate
from ..models import User, UserRole
from app.core.dependencies import get_current_user
from ..models.plans import Plans
from sqlalchemy import desc
router = APIRouter(prefix = "/api/plans", tags = ["plans"])

@router.post("",response_model = PlanResponse)
def create_plans(
    request: PlanCreate,
    current_user : User = Depends(get_current_user),
    db: Session = Depends(get_db)):
    '''Create plans for users  (route available for superadmin only)'''
    if current_user.role!=UserRole.SUPERADMIN:
        raise HTTPException(status_code = 403,detail = "Admin access required")
    
    plans = Plans(
        name = request.name,
        code = request.code,
        description = request.description,
        credits = request.credits,
        price = request.price,
        features = request.features,
    )
    db.add(plans)
    db.commit()
    db.refresh(plans)

    return plans

@router.get("",response_model = list[PlanResponse])
def list_plans(current_user: User = Depends(get_current_user),db: Session = Depends(get_db)):
    '''List of plans only active plans visible to normal users'''

    if current_user.role!= UserRole.SUPERADMIN:
        query = db.query(Plans).filter(Plans.is_active).order_by(desc(Plans.created_at)) 
    else:
        query = db.query(Plans).order_by(desc(Plans.created_at))

    return query

@router.put("/{plan_id}",response_model = PlanResponse)
def update_plans(plan_id: int, plan_data: PlanUpdate,current_user: User = Depends(get_current_user),db: Session = Depends(get_db)):
    '''Update plans by superadmin only'''
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(status_code = 403, detail= "Admin access only")
    
    plan = db.query(Plans).filter(Plans.id==plan_id).first()
    
    if not plan:
        raise HTTPException(status_code = 404, detail = "Plan not found")
    
     # Update fields
    update_data = plan_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(plan, field, value)
    
    db.commit()
    db.refresh(plan)
    
    return plan

@router.delete("/{plan_id}")
def delete_plan(plan_id: int,current_user: User =Depends(get_current_user),db: Session= Depends(get_db)):
    '''Delete plan by superadmin only'''
    if current_user.role!= UserRole.SUPERADMIN:
        raise HTTPException(status_code = 403, detail= 'Admin access only')
    
    plan = db.query(Plans).filter(Plans.id==plan_id).first()

    if not plan:
        raise HTTPException(status_code= 404, detail = "Not found")
    
    db.delete(plan)
    db.commit()

    return {"message" : "Plan deleted successfully"}

@router.get("/public", response_model=list[PlanResponse])
def list_public_plans(db: Session = Depends(get_db)):

    return (
        db.query(Plans)
        .filter(Plans.is_active)
        .order_by(Plans.price)
        .all()
    )


    

    

