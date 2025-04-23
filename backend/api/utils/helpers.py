from sqlalchemy.orm import Session
from api.models import models

def get_last_bpmn_data_for_user(db: Session, user_id: int, project_id: int) -> models.BPMNData:
    """
    Retrieve the last saved BPMN data associated with the given project and user.

    Parameters:
    - db: Database session.
    - user_id: ID of the user.
    - project_id: ID of the project.

    Returns:
    - BPMNData object.
    """
 
    return (
        db.query(models.BPMNData)
        .join(models.Project)
        .filter(models.Project.user_id == user_id)
        .filter(models.Project.id == project_id)
        .order_by(models.BPMNData.created_at.desc())
        .first()
    )


def get_last_bpmn_extraction_for_user(db: Session, user_id: int, project_id: int) -> models.BPMNExtraction:
    """
    Retrieve the last saved BPMN Extraction associated with the given project and user.

    Parameters:
    - db: Database session.
    - user_id: ID of the user.
    - project_id: ID of the project.

    Returns:
    - BPMNExtraction object.
    """

    return (
        db.query(models.BPMNExtraction)
        .join(models.Project)
        .filter(models.Project.user_id == user_id)
        .filter(models.Project.id == project_id)
        .order_by(models.BPMNExtraction.created_at.desc())
        .first()
    )
