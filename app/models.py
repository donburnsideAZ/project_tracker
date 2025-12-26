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
    role: str  # Can be any role defined by the team


@dataclass
class ProjectField:
    """A custom project field definition"""
    key: str        # Internal key (e.g., "campus", "department")
    label: str      # Display label (e.g., "Campus", "Department")
    values: list = field(default_factory=list)  # Allowed values


@dataclass
class TrainingModule:
    """A chapter/module within a course - for chunking guide"""
    number: int
    name: str = ""
    status: str = "Not Started"  # Not Started, In Progress, Complete


@dataclass
class Project:
    """A project to track time against"""
    id: str
    name: str
    project_id: str = ""  # External/corporate ID (may be empty)
    status: str = "Not Started"
    target_hours: float = 0.0
    
    # Team assignments (employee IDs)
    team_assignments: dict = field(default_factory=dict)  # role_key -> employee_id
    
    # Dynamic custom fields (populated from team_data.project_fields)
    custom_fields: dict = field(default_factory=dict)  # field_key -> value
    
    # Chunking guide (optional)
    tms: list = field(default_factory=list)
    tags: list = field(default_factory=list)
    
    # Project notes (HTML formatted)
    notes: str = ""
    
    # Metadata
    created_at: str = ""
    created_by: str = ""
    modified_at: str = ""
    modified_by: str = ""
    
    # Legacy fields (for backwards compatibility during migration)
    campus: str = ""
    offer: str = ""
    sub_offer: str = ""
    course_id: str = ""
    effort_type: str = ""
    course_type: str = ""
    course_duration_minutes: int = 0
    lpo: str = ""
    sme: str = ""
    lxo: str = ""
    
    @classmethod
    def generate_id(cls) -> str:
        """Generate a unique ID for projects without an external ID"""
        return f"PRJ-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"
    
    def get_file_id(self) -> str:
        """Get the ID to use for the filename"""
        # Prefer project_id, fall back to course_id (legacy), then internal id
        return self.project_id or self.course_id or self.id
    
    def get_custom_field(self, key: str, default: str = "") -> str:
        """Get a custom field value, checking both new and legacy locations"""
        # Check custom_fields dict first
        if key in self.custom_fields:
            return self.custom_fields[key]
        # Fall back to legacy attributes
        if hasattr(self, key):
            return getattr(self, key, default)
        return default
    
    def set_custom_field(self, key: str, value: str):
        """Set a custom field value"""
        self.custom_fields[key] = value


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
                      notes: str = "", entry_date: str = None) -> 'TimeEntry':
        """Create a new time entry with hours"""
        if entry_date is None:
            entry_date = date.today().isoformat()
        return cls(
            id=str(uuid.uuid4()),
            project_id=project_id,
            work_type=work_type,
            hours=hours,
            date=entry_date,
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
    project_statuses: list = field(default_factory=list)
    tags: list = field(default_factory=list)
    
    # Dynamic project fields - replaces hardcoded campuses, offers, etc.
    project_fields: list = field(default_factory=list)  # List of ProjectField dicts
    
    # Team role definitions (what roles can be assigned to projects)
    team_roles: list = field(default_factory=list)  # e.g., ["LXO", "LPO", "SME"]
    
    # Optional 4th tab configuration
    # {"enabled": True, "type": "chunking_guide", "label": "Chunking Guide"}
    optional_tab: dict = field(default_factory=dict)
    
    # Legacy fields (for backwards compatibility during migration)
    campuses: list = field(default_factory=list)
    offers: list = field(default_factory=list)
    sub_offers: list = field(default_factory=list)
    effort_types: list = field(default_factory=list)
    course_types: list = field(default_factory=list)
    
    def get_project_field(self, key: str) -> Optional[dict]:
        """Get a project field definition by key"""
        for pf in self.project_fields:
            if isinstance(pf, dict) and pf.get('key') == key:
                return pf
        return None
    
    def get_field_values(self, key: str) -> list:
        """Get values for a project field, checking both new and legacy locations"""
        # Check project_fields first
        pf = self.get_project_field(key)
        if pf:
            return pf.get('values', [])
        # Fall back to legacy attributes
        if hasattr(self, key):
            return getattr(self, key, [])
        return []
