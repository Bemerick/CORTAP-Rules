"""
Projects API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import List
from decimal import Decimal

from app.database.connection import get_db
from app.models import Project, ProjectAnswer, SubArea, Section, ProjectApplicability
from app.schemas import (
    ProjectSchema,
    ProjectCreateSchema,
    ProjectUpdateSchema,
    ProjectAnswersSchema,
    ProjectApplicabilityResultSchema,
    ProjectLOESummarySchema,
    SectionLOESummary,
    SubAreaSchema
)

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=List[ProjectSchema])
def get_projects(db: Session = Depends(get_db)):
    """Get all projects"""
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    return projects


@router.post("", response_model=ProjectSchema, status_code=201)
def create_project(project: ProjectCreateSchema, db: Session = Depends(get_db)):
    """Create a new project"""
    # Check if project name already exists
    existing = db.query(Project).filter(Project.name == project.name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Project with name '{project.name}' already exists")

    new_project = Project(
        name=project.name,
        description=project.description,
        grantee_name=project.grantee_name,
        grant_number=project.grant_number,
        review_type=project.review_type
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return new_project


@router.get("/{project_id}", response_model=ProjectSchema)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get a specific project"""
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


@router.put("/{project_id}", response_model=ProjectSchema)
def update_project(project_id: int, project_update: ProjectUpdateSchema, db: Session = Depends(get_db)):
    """Update a project"""
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project_update.name:
        # Check if new name conflicts with another project
        existing = db.query(Project).filter(
            Project.name == project_update.name,
            Project.id != project_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Project name already exists")
        project.name = project_update.name

    if project_update.description is not None:
        project.description = project_update.description

    db.commit()
    db.refresh(project)

    return project


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Delete a project"""
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()

    return None


@router.post("/{project_id}/answers", response_model=ProjectApplicabilityResultSchema)
def submit_project_answers(
    project_id: int,
    answers_data: ProjectAnswersSchema,
    db: Session = Depends(get_db)
):
    """Submit answers for a project and calculate applicable sub-areas"""
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Delete existing answers and applicability
    db.query(ProjectAnswer).filter(ProjectAnswer.project_id == project_id).delete()
    db.query(ProjectApplicability).filter(ProjectApplicability.project_id == project_id).delete()

    # Insert new answers
    for question_key, answer_value in answers_data.answers.items():
        project_answer = ProjectAnswer(
            project_id=project_id,
            question_key=question_key,
            answer_value=answer_value
        )
        db.add(project_answer)

    db.commit()

    # Calculate applicable sub-areas using database function
    result = db.execute(
        text("SELECT sub_area_id FROM get_applicable_sub_areas(:project_id)"),
        {"project_id": project_id}
    )

    applicable_sub_area_ids = [row[0] for row in result]

    # Insert applicability records
    for sub_area_id in applicable_sub_area_ids:
        applicability = ProjectApplicability(
            project_id=project_id,
            sub_area_id=sub_area_id,
            is_applicable=True
        )
        db.add(applicability)

    db.commit()

    # Get detailed sub-area information
    sub_areas = db.query(SubArea).filter(SubArea.id.in_(applicable_sub_area_ids)).all()

    # Format as ApplicableSubArea objects
    applicable_sub_areas = []
    for sa in sub_areas:
        applicable_sub_areas.append({
            'section_id': sa.section_id,
            'section_name': sa.section.title if sa.section else '',
            'sub_area_id': sa.id,
            'question': sa.question or '',
            'basic_requirement': sa.basic_requirement or '',
            'loe_hours': float(sa.loe_hours) if sa.loe_hours else 0.0,
            'loe_confidence': sa.loe_confidence or 'medium',
            'loe_confidence_score': sa.loe_confidence_score or 0
        })

    return ProjectApplicabilityResultSchema(
        project_id=project.id,
        applicable_count=len(applicable_sub_areas),
        applicable_sub_areas=applicable_sub_areas
    )


@router.get("/{project_id}/applicable-sub-areas", response_model=ProjectApplicabilityResultSchema)
def get_project_applicable_sub_areas(project_id: int, db: Session = Depends(get_db)):
    """Get applicable sub-areas for a project"""
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get applicable sub-areas
    sub_areas = db.query(SubArea).join(
        ProjectApplicability,
        SubArea.id == ProjectApplicability.sub_area_id
    ).filter(
        ProjectApplicability.project_id == project_id,
        ProjectApplicability.is_applicable == True
    ).order_by(SubArea.section_id, SubArea.id).all()

    # Format as ApplicableSubArea objects
    applicable_sub_areas = []
    for sa in sub_areas:
        applicable_sub_areas.append({
            'section_id': sa.section_id,
            'section_name': sa.section.title if sa.section else '',
            'sub_area_id': sa.id,
            'question': sa.question or '',
            'basic_requirement': sa.basic_requirement or '',
            'loe_hours': float(sa.loe_hours) if sa.loe_hours else 0.0,
            'loe_confidence': sa.loe_confidence or 'medium',
            'loe_confidence_score': sa.loe_confidence_score or 0
        })

    return ProjectApplicabilityResultSchema(
        project_id=project_id,
        applicable_count=len(applicable_sub_areas),
        applicable_sub_areas=applicable_sub_areas
    )


@router.get("/{project_id}/loe-summary", response_model=ProjectLOESummarySchema)
def get_project_loe_summary(project_id: int, db: Session = Depends(get_db)):
    """Get LOE summary for a project"""
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get summary by section
    section_summaries = db.query(
        Section.id,
        Section.title,
        func.count(SubArea.id).label('applicable_sub_areas'),
        func.sum(SubArea.loe_hours).label('section_hours'),
        func.avg(SubArea.loe_confidence_score).label('avg_confidence')
    ).join(SubArea, Section.id == SubArea.section_id)\
    .join(ProjectApplicability, SubArea.id == ProjectApplicability.sub_area_id)\
    .filter(
        ProjectApplicability.project_id == project_id,
        ProjectApplicability.is_applicable == True
    ).group_by(Section.id, Section.title)\
    .order_by(func.sum(SubArea.loe_hours).desc().nullslast())\
    .all()

    sections = [
        SectionLOESummary(
            section_id=s.id,
            section_name=s.title,
            sub_area_count=s.applicable_sub_areas,
            total_hours=float(s.section_hours) if s.section_hours else 0.0,
            avg_confidence_score=float(s.avg_confidence) if s.avg_confidence else 0.0
        )
        for s in section_summaries
    ]

    # Calculate totals
    total_sub_areas = sum(s.sub_area_count for s in sections)
    total_hours = sum(s.total_hours for s in sections)
    avg_confidence = sum(s.avg_confidence_score * s.sub_area_count for s in sections) / total_sub_areas if total_sub_areas > 0 else 0.0

    return ProjectLOESummarySchema(
        project_id=project.id,
        project_name=project.name,
        total_sub_areas=total_sub_areas,
        total_hours=total_hours,
        avg_confidence_score=avg_confidence,
        sections=sections
    )
