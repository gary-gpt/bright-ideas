"""
API routes for build planning and project management.
"""
from typing import List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from database import get_db
from schemas import BuildPlanCreate, BuildPlanUpdate, BuildPlanResponse, ExportCreate, ExportResponse
from services.planning_service import PlanningService
import json
import zipfile
import io

router = APIRouter(prefix="/planning", tags=["planning"])


@router.post("/", response_model=BuildPlanResponse)
async def create_build_plan(
    plan: BuildPlanCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new build plan for an idea.
    
    Args:
        plan: Build plan creation data
        db: Database session
        
    Returns:
        Created build plan
    """
    service = PlanningService(db)
    
    try:
        db_plan = await service.create_build_plan(plan)
        return db_plan
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create build plan: {str(e)}")


@router.get("/{plan_id}", response_model=BuildPlanResponse)
def get_build_plan(
    plan_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific build plan by ID.
    
    Args:
        plan_id: UUID of the build plan
        db: Database session
        
    Returns:
        Build plan details
    """
    service = PlanningService(db)
    plan = service.get_build_plan(plan_id)
    
    if not plan:
        raise HTTPException(status_code=404, detail="Build plan not found")
    
    return plan


@router.get("/idea/{idea_id}", response_model=List[BuildPlanResponse])
def get_idea_build_plans(
    idea_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get all build plans for an idea.
    
    Args:
        idea_id: UUID of the idea
        db: Database session
        
    Returns:
        List of build plans
    """
    service = PlanningService(db)
    plans = service.get_idea_build_plans(idea_id)
    return plans


@router.put("/{plan_id}", response_model=BuildPlanResponse)
def update_build_plan(
    plan_id: UUID,
    plan_update: BuildPlanUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing build plan.
    
    Args:
        plan_id: UUID of the build plan to update
        plan_update: Updated build plan data
        db: Database session
        
    Returns:
        Updated build plan
    """
    service = PlanningService(db)
    updated_plan = service.update_build_plan(plan_id, plan_update)
    
    if not updated_plan:
        raise HTTPException(status_code=404, detail="Build plan not found")
    
    return updated_plan


@router.post("/{plan_id}/components", response_model=BuildPlanResponse)
def add_plan_component(
    plan_id: UUID,
    component: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Add a component to a build plan.
    
    Args:
        plan_id: UUID of the build plan
        component: Component data to add
        db: Database session
        
    Returns:
        Updated build plan
    """
    service = PlanningService(db)
    updated_plan = service.add_plan_component(plan_id, component)
    
    if not updated_plan:
        raise HTTPException(status_code=404, detail="Build plan not found")
    
    return updated_plan


@router.put("/{plan_id}/phases/{phase_index}", response_model=BuildPlanResponse)
def update_plan_phase(
    plan_id: UUID,
    phase_index: int,
    phase_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Update a specific phase in a build plan.
    
    Args:
        plan_id: UUID of the build plan
        phase_index: Index of the phase to update
        phase_data: Updated phase data
        db: Database session
        
    Returns:
        Updated build plan
    """
    service = PlanningService(db)
    updated_plan = service.update_plan_phase(plan_id, phase_index, phase_data)
    
    if not updated_plan:
        raise HTTPException(status_code=404, detail="Build plan not found or invalid phase index")
    
    return updated_plan


@router.post("/exports/", response_model=ExportResponse)
def create_export(
    export: ExportCreate,
    db: Session = Depends(get_db)
):
    """
    Create an export from a build plan.
    
    Args:
        export: Export creation data
        db: Database session
        
    Returns:
        Created export
    """
    service = PlanningService(db)
    
    try:
        db_export = service.create_export(export)
        return db_export
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{plan_id}/export/markdown")
def export_markdown(
    plan_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Generate and download markdown export from a build plan.
    
    Args:
        plan_id: UUID of the build plan
        db: Database session
        
    Returns:
        ZIP file containing markdown documents
    """
    service = PlanningService(db)
    
    try:
        markdown_files = service.generate_markdown_export(plan_id)
        
        # Create ZIP file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename, content in markdown_files.items():
                zip_file.writestr(filename, content)
        
        zip_buffer.seek(0)
        
        return Response(
            content=zip_buffer.getvalue(),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename=build_plan_{plan_id}_markdown.zip"}
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/{plan_id}/export/json")
def export_json(
    plan_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Generate and download JSON export from a build plan.
    
    Args:
        plan_id: UUID of the build plan
        db: Database session
        
    Returns:
        ZIP file containing JSON documents
    """
    service = PlanningService(db)
    
    try:
        json_files = service.generate_json_export(plan_id)
        
        # Create ZIP file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename, content in json_files.items():
                zip_file.writestr(filename, content)
        
        zip_buffer.seek(0)
        
        return Response(
            content=zip_buffer.getvalue(),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename=build_plan_{plan_id}_json.zip"}
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/{plan_id}/preview/markdown")
def preview_markdown_export(
    plan_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Preview markdown export content without downloading.
    
    Args:
        plan_id: UUID of the build plan
        db: Database session
        
    Returns:
        Dictionary with filenames and preview content
    """
    service = PlanningService(db)
    
    try:
        markdown_files = service.generate_markdown_export(plan_id)
        
        # Return first 500 characters of each file for preview
        preview = {}
        for filename, content in markdown_files.items():
            preview[filename] = {
                "preview": content[:500] + ("..." if len(content) > 500 else ""),
                "full_length": len(content),
                "lines": content.count('\n') + 1
            }
        
        return preview
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preview failed: {str(e)}")