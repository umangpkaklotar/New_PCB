from fastapi import APIRouter
from backend.app.db.database import inspections_collection

router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"]
)

@router.get("/stats")
def get_dashboard_stats():
    total_inspections = inspections_collection.count_documents({})
    defective_pcb = inspections_collection.count_documents({"status": "defective"})
    normal_pcb = inspections_collection.count_documents({"status": "normal"})
    
    # Calculate total defects using aggregation
    pipeline = [
        {"$group": {"_id": None, "total": {"$sum": "$total_defects"}}}
    ]
    result = list(inspections_collection.aggregate(pipeline))
    total_defects = result[0]["total"] if result else 0
    
    return {
        "totalInspections": total_inspections,
        "defectivePcb": defective_pcb,
        "normalPcb": normal_pcb,
        "totalDefects": total_defects
    }
