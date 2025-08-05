"""
Service for managing build plans and project planning operations.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from models import BuildPlan, Idea, Export
from schemas import BuildPlanCreate, BuildPlanUpdate, ExportCreate
from services.ai_service import ai_service


class PlanningService:
    """Service for managing build planning operations."""
    
    def __init__(self, db: Session):
        """Initialize planning service with database session."""
        self.db = db
    
    async def create_build_plan(self, plan_data: BuildPlanCreate) -> BuildPlan:
        """
        Create a new build plan for an idea.
        
        Args:
            plan_data: Build plan creation data
            
        Returns:
            Created build plan instance
        """
        # Verify the idea exists
        idea = self.db.query(Idea).filter(Idea.id == plan_data.idea_id).first()
        if not idea:
            raise ValueError(f"Idea with ID {plan_data.idea_id} not found")
        
        # Generate AI-powered build plan if plan_data is minimal
        if not plan_data.plan_data or len(plan_data.plan_data) == 0:
            try:
                ai_plan = await ai_service.generate_build_plan({
                    "title": idea.title,
                    "original_description": idea.original_description,
                    "refined_description": idea.refined_description,
                    "problem_statement": idea.problem_statement,
                    "target_audience": idea.target_audience,
                    "implementation_notes": idea.implementation_notes
                })
                plan_data.plan_data = ai_plan
            except Exception as e:
                # Fallback to basic structure if AI fails
                plan_data.plan_data = self._create_basic_plan_structure(idea)
        
        db_plan = BuildPlan(
            idea_id=plan_data.idea_id,
            plan_data=plan_data.plan_data,
            export_configs={}
        )
        
        self.db.add(db_plan)
        self.db.commit()
        self.db.refresh(db_plan)
        
        # Update idea status to building
        idea.status = "building"
        self.db.commit()
        
        return db_plan
    
    def get_build_plan(self, plan_id: UUID) -> Optional[BuildPlan]:
        """
        Get a build plan by ID.
        
        Args:
            plan_id: UUID of the build plan
            
        Returns:
            Build plan instance or None if not found
        """
        return self.db.query(BuildPlan).filter(BuildPlan.id == plan_id).first()
    
    def get_idea_build_plans(self, idea_id: UUID) -> List[BuildPlan]:
        """
        Get all build plans for an idea.
        
        Args:
            idea_id: UUID of the idea
            
        Returns:
            List of build plans
        """
        return (
            self.db.query(BuildPlan)
            .filter(BuildPlan.idea_id == idea_id)
            .order_by(BuildPlan.created_at.desc())
            .all()
        )
    
    def update_build_plan(
        self, 
        plan_id: UUID, 
        update_data: BuildPlanUpdate
    ) -> Optional[BuildPlan]:
        """
        Update an existing build plan.
        
        Args:
            plan_id: UUID of the build plan to update
            update_data: Updated build plan data
            
        Returns:
            Updated build plan instance or None if not found
        """
        db_plan = self.get_build_plan(plan_id)
        if not db_plan:
            return None
        
        # Update fields that are provided
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(db_plan, field, value)
        
        self.db.commit()
        self.db.refresh(db_plan)
        
        return db_plan
    
    def add_plan_component(
        self, 
        plan_id: UUID, 
        component: Dict[str, Any]
    ) -> Optional[BuildPlan]:
        """
        Add a component to a build plan.
        
        Args:
            plan_id: UUID of the build plan
            component: Component data to add
            
        Returns:
            Updated build plan or None if not found
        """
        db_plan = self.get_build_plan(plan_id)
        if not db_plan:
            return None
        
        if "components" not in db_plan.plan_data:
            db_plan.plan_data["components"] = []
        
        db_plan.plan_data["components"].append(component)
        
        self.db.commit()
        self.db.refresh(db_plan)
        
        return db_plan
    
    def update_plan_phase(
        self, 
        plan_id: UUID, 
        phase_index: int, 
        phase_data: Dict[str, Any]
    ) -> Optional[BuildPlan]:
        """
        Update a specific phase in a build plan.
        
        Args:
            plan_id: UUID of the build plan
            phase_index: Index of the phase to update
            phase_data: Updated phase data
            
        Returns:
            Updated build plan or None if not found
        """
        db_plan = self.get_build_plan(plan_id)
        if not db_plan:
            return None
        
        phases = db_plan.plan_data.get("phases", [])
        if 0 <= phase_index < len(phases):
            phases[phase_index].update(phase_data)
            db_plan.plan_data["phases"] = phases
            
            self.db.commit()
            self.db.refresh(db_plan)
        
        return db_plan
    
    def create_export(self, export_data: ExportCreate) -> Export:
        """
        Create an export from a build plan.
        
        Args:
            export_data: Export creation data
            
        Returns:
            Created export instance
        """
        # Verify the build plan exists
        build_plan = self.get_build_plan(export_data.build_plan_id)
        if not build_plan:
            raise ValueError(f"Build plan with ID {export_data.build_plan_id} not found")
        
        db_export = Export(
            build_plan_id=export_data.build_plan_id,
            export_type=export_data.export_type,
            file_data=export_data.file_data
        )
        
        self.db.add(db_export)
        self.db.commit()
        self.db.refresh(db_export)
        
        return db_export
    
    def generate_markdown_export(self, plan_id: UUID) -> Dict[str, str]:
        """
        Generate a markdown export from a build plan.
        
        Args:
            plan_id: UUID of the build plan
            
        Returns:
            Dictionary with filename as key and markdown content as value
        """
        db_plan = self.get_build_plan(plan_id)
        if not db_plan:
            raise ValueError(f"Build plan with ID {plan_id} not found")
        
        idea = self.db.query(Idea).filter(Idea.id == db_plan.idea_id).first()
        plan_data = db_plan.plan_data
        
        # Generate main project document
        markdown_content = self._generate_project_markdown(idea, plan_data)
        
        # Generate phase documents
        phase_docs = {}
        for i, phase in enumerate(plan_data.get("phases", [])):
            phase_doc = self._generate_phase_markdown(phase, i + 1)
            phase_docs[f"phase_{i+1}_{phase['name'].lower().replace(' ', '_')}.md"] = phase_doc
        
        return {
            "project_plan.md": markdown_content,
            **phase_docs
        }
    
    def generate_json_export(self, plan_id: UUID) -> Dict[str, str]:
        """
        Generate a JSON export from a build plan.
        
        Args:
            plan_id: UUID of the build plan
            
        Returns:
            Dictionary with filename as key and JSON content as value
        """
        import json
        
        db_plan = self.get_build_plan(plan_id)
        if not db_plan:
            raise ValueError(f"Build plan with ID {plan_id} not found")
        
        idea = self.db.query(Idea).filter(Idea.id == db_plan.idea_id).first()
        
        export_data = {
            "idea": {
                "id": str(idea.id),
                "title": idea.title,
                "original_description": idea.original_description,
                "refined_description": idea.refined_description,
                "problem_statement": idea.problem_statement,
                "target_audience": idea.target_audience,
                "tags": idea.tags,
                "status": idea.status
            },
            "build_plan": {
                "id": str(db_plan.id),
                "plan_data": db_plan.plan_data,
                "created_at": db_plan.created_at.isoformat(),
                "updated_at": db_plan.updated_at.isoformat()
            }
        }
        
        return {
            "project_export.json": json.dumps(export_data, indent=2)
        }
    
    def _create_basic_plan_structure(self, idea: Idea) -> Dict[str, Any]:
        """Create a basic plan structure when AI generation fails."""
        return {
            "overview": f"Build plan for: {idea.title}",
            "components": [
                {"name": "Research", "description": "Research and requirements gathering"},
                {"name": "Design", "description": "System design and planning"},
                {"name": "Implementation", "description": "Core development work"},
                {"name": "Testing", "description": "Testing and quality assurance"},
                {"name": "Deployment", "description": "Launch and deployment"}
            ],
            "phases": [
                {
                    "name": "Planning",
                    "duration": "1-2 weeks",
                    "tasks": ["Define requirements", "Create specifications", "Plan architecture"],
                    "deliverables": ["Requirements document", "Technical specifications"]
                },
                {
                    "name": "Development",
                    "duration": "4-6 weeks",
                    "tasks": ["Build core features", "Implement functionality", "Integration testing"],
                    "deliverables": ["Working prototype", "Test results"]
                },
                {
                    "name": "Launch",
                    "duration": "1-2 weeks",
                    "tasks": ["Final testing", "Documentation", "Deployment"],
                    "deliverables": ["Production release", "User documentation"]
                }
            ],
            "success_criteria": [
                "Meets original requirements",
                "Functions as intended",
                "User feedback is positive",
                "Technical performance is acceptable"
            ]
        }
    
    def _generate_project_markdown(self, idea: Idea, plan_data: Dict[str, Any]) -> str:
        """Generate main project markdown document."""
        content = f"""# {idea.title}

## Project Overview
{idea.refined_description or idea.original_description}

## Problem Statement
{idea.problem_statement or "To be defined"}

## Target Audience
{idea.target_audience or "To be defined"}

## Project Components
"""
        
        for component in plan_data.get("components", []):
            content += f"### {component['name']}\n{component['description']}\n\n"
        
        content += "\n## Development Phases\n"
        
        for i, phase in enumerate(plan_data.get("phases", []), 1):
            content += f"""
### Phase {i}: {phase['name']}
**Duration:** {phase.get('duration', 'TBD')}

**Tasks:**
"""
            for task in phase.get('tasks', []):
                content += f"- {task}\n"
            
            content += "\n**Deliverables:**\n"
            for deliverable in phase.get('deliverables', []):
                content += f"- {deliverable}\n"
            
            content += "\n"
        
        content += "\n## Success Criteria\n"
        for criterion in plan_data.get("success_criteria", []):
            content += f"- {criterion}\n"
        
        return content
    
    def _generate_phase_markdown(self, phase: Dict[str, Any], phase_number: int) -> str:
        """Generate markdown document for a specific phase."""
        content = f"""# Phase {phase_number}: {phase['name']}

## Overview
Duration: {phase.get('duration', 'TBD')}

## Tasks
"""
        
        for task in phase.get('tasks', []):
            content += f"- [ ] {task}\n"
        
        content += "\n## Deliverables\n"
        for deliverable in phase.get('deliverables', []):
            content += f"- {deliverable}\n"
        
        content += "\n## Notes\n_Add your notes and progress updates here._"
        
        return content