"""
Data models for Project Tracker
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional
import uuid


@dataclass
class Employee:
    """Team member who can log time"""
    id: str
    name: str
    role: str  # LXO, LPO, SME


@dataclass
class TrainingModule:
    """A chapter/module within a course"""
    number: int
    name: str = ""
    status: str = "Not Started"  # Not Started, In Progress, Complete


@dataclass
class Project:
    """A training project/course"""
    id: str
    name: str
    campus: str = ""
    offer: str = ""
    sub_offer: str = ""
    course_id: str = ""  # Corporate course ID (may be empty)
    effort_type: str = ""
    course_type: str = ""
    status: str = "Not Started"
    course_duration_minutes: int = 0
    target_hours: float = 0.0
    lpo: str = ""
    sme: str = ""
    lxo: str = ""
    tms: list = field(default_factory=list)
    tags: list = field(default_factory=list)
    created_at: str = ""
    created_by: str = ""
    modified_at: str = ""
    modified_by: str = ""
    
    @classmethod
    def generate_id(cls) -> str:
        """Generate a unique ID for projects without a course_id"""
        return f"PRJ-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"
    
    def get_file_id(self) -> str:
        """Get the ID to use for the filename"""
        return self.course_id if self.course_id else self.id


@dataclass
class TimeEntry:
    """A single time tracking entry"""
    id: str
    project_id: str
    work_type: str
    hours: int  # Whole hours only
    date: str   # YYYY-MM-DD
    notes: str = ""
    created_at: str = ""
    
    @classmethod
    def create_simple(cls, project_id: str, work_type: str, hours: int, 
                      notes: str = "") -> 'TimeEntry':
        """Create a new time entry with hours"""
        today = date.today().isoformat()
        return cls(
            id=str(uuid.uuid4()),
            project_id=project_id,
            work_type=work_type,
            hours=hours,
            date=today,
            notes=notes,
            created_at=datetime.now().isoformat()
        )
    
    @classmethod
    def create(cls, project_id: str, work_type: str, start_time: datetime, 
               end_time: datetime, notes: str = "") -> 'TimeEntry':
        """Create a new time entry from start/end times (legacy support)"""
        duration_hours = int((end_time - start_time).total_seconds() / 3600)
        if duration_hours < 1:
            duration_hours = 1  # Minimum 1 hour
        return cls(
            id=str(uuid.uuid4()),
            project_id=project_id,
            work_type=work_type,
            hours=duration_hours,
            date=start_time.date().isoformat(),
            notes=notes,
            created_at=datetime.now().isoformat()
        )


@dataclass
class DailyTimeFile:
    """Container for a user's daily time entries"""
    user_id: str
    date: str  # YYYY-MM-DD
    entries: list = field(default_factory=list)


@dataclass 
class TeamData:
    """Shared configuration and lookup tables"""
    work_types: list = field(default_factory=list)
    employees: list = field(default_factory=list)
    campuses: list = field(default_factory=list)
    offers: list = field(default_factory=list)
    sub_offers: list = field(default_factory=list)
    effort_types: list = field(default_factory=list)
    course_types: list = field(default_factory=list)
    project_statuses: list = field(default_factory=list)
    tags: list = field(default_factory=list)
