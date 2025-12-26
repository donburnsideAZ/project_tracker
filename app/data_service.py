"""
Data service for Project Tracker - handles all file I/O
"""

import json
import os
import getpass
from pathlib import Path
from datetime import datetime, date
from typing import Optional
from dataclasses import asdict

from .models import Project, TimeEntry, DailyTimeFile, TeamData, Employee


class DataService:
    """
    Singleton service for managing all data operations.
    The filesystem is our database - OneDrive handles sync.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._config_dir = Path.home() / ".projecttracker"
        self._config_file = self._config_dir / "config.json"
        self._data_folder: Optional[Path] = None
        self._current_user_id: Optional[str] = None
        self._current_user: Optional[Employee] = None
        
        # Cached data
        self._team_data: Optional[TeamData] = None
        self._projects: dict[str, Project] = {}
        self._today_entries: Optional[DailyTimeFile] = None
        
        # Load config
        self._load_config()
    
    # =========================================================================
    # Configuration
    # =========================================================================
    
    def _load_config(self):
        """Load local config from user's home directory"""
        self._config_dir.mkdir(exist_ok=True)
        
        if self._config_file.exists():
            with open(self._config_file, 'r') as f:
                config = json.load(f)
                if config.get('data_folder'):
                    self._data_folder = Path(config['data_folder'])
    
    def _save_config(self):
        """Save local config"""
        config = {
            'data_folder': str(self._data_folder) if self._data_folder else None,
            'recent_folders': [],
            'window_geometry': None
        }
        with open(self._config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    @property
    def data_folder(self) -> Optional[Path]:
        return self._data_folder
    
    @data_folder.setter
    def data_folder(self, path: Path):
        """Set the data folder and reload all data"""
        self._data_folder = path
        self._save_config()
        self._ensure_folder_structure()
        self.reload_all()
    
    def _ensure_folder_structure(self):
        """Create required subfolders if they don't exist"""
        if not self._data_folder:
            return
        
        (self._data_folder / "projects").mkdir(exist_ok=True)
        (self._data_folder / "time").mkdir(exist_ok=True)
        
        # Create default team_data.json if it doesn't exist
        team_data_file = self._data_folder / "team_data.json"
        if not team_data_file.exists():
            default_team_data = {
                "work_types": [
                    "Planning", "Creation", "Review", "Production",
                    "Admin", "Meetings", "Miscellaneous"
                ],
                "employees": [],
                "project_statuses": ["Not Started", "In Progress", "Complete"],
                "tags": [],
                "team_roles": ["Owner", "Contributor", "Reviewer"],
                "project_fields": [
                    {
                        "key": "category",
                        "label": "Category",
                        "values": []
                    },
                    {
                        "key": "priority",
                        "label": "Priority",
                        "values": ["Low", "Medium", "High"]
                    }
                ]
            }
            with open(team_data_file, 'w') as f:
                json.dump(default_team_data, f, indent=2)
    
    def is_configured(self) -> bool:
        """Check if a data folder has been set"""
        return self._data_folder is not None and self._data_folder.exists()
    
    # =========================================================================
    # User Identification
    # =========================================================================
    
    def get_os_username(self) -> str:
        """Get the current OS username"""
        return getpass.getuser()
    
    def identify_user(self) -> Optional[Employee]:
        """
        Identify the current user from OS username.
        Returns None if not found in team_data.
        """
        if not self._team_data:
            return None
        
        os_user = self.get_os_username()
        for emp_data in self._team_data.employees:
            if isinstance(emp_data, dict) and emp_data.get('id') == os_user:
                self._current_user_id = emp_data['id']
                self._current_user = Employee(**emp_data)
                return self._current_user
        
        return None
    
    def set_current_user(self, employee_id: str):
        """Manually set the current user (when OS lookup fails)"""
        if not self._team_data:
            return
        
        for emp_data in self._team_data.employees:
            if isinstance(emp_data, dict) and emp_data.get('id') == employee_id:
                self._current_user_id = emp_data['id']
                self._current_user = Employee(**emp_data)
                break
    
    @property
    def current_user(self) -> Optional[Employee]:
        return self._current_user
    
    @property
    def current_user_id(self) -> Optional[str]:
        return self._current_user_id or self.get_os_username()
    
    # =========================================================================
    # Team Data
    # =========================================================================
    
    def load_team_data(self) -> Optional[TeamData]:
        """Load shared team configuration"""
        if not self._data_folder:
            return None
        
        team_data_file = self._data_folder / "team_data.json"
        if not team_data_file.exists():
            return None
        
        with open(team_data_file, 'r') as f:
            data = json.load(f)
        
        self._team_data = TeamData(**data)
        return self._team_data
    
    def save_team_data(self, team_data: TeamData):
        """Save team data back to file"""
        if not self._data_folder:
            return
        
        team_data_file = self._data_folder / "team_data.json"
        with open(team_data_file, 'w') as f:
            json.dump(asdict(team_data), f, indent=2)
        
        self._team_data = team_data
    
    @property
    def team_data(self) -> Optional[TeamData]:
        return self._team_data
    
    # =========================================================================
    # Projects
    # =========================================================================
    
    def load_projects(self) -> dict[str, Project]:
        """Load all projects from the projects folder"""
        if not self._data_folder:
            return {}
        
        projects_dir = self._data_folder / "projects"
        if not projects_dir.exists():
            return {}
        
        self._projects = {}
        for file_path in projects_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                project = Project(**data)
                self._projects[project.id] = project
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Error loading project {file_path}: {e}")
        
        return self._projects
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """Get a single project by ID"""
        return self._projects.get(project_id)
    
    def save_project(self, project: Project):
        """Save a project to its JSON file"""
        if not self._data_folder:
            return
        
        # Update modification timestamp
        project.modified_at = datetime.now().isoformat()
        project.modified_by = self.current_user_id
        
        # Use course_id for filename if available, else use generated id
        file_id = project.get_file_id()
        file_path = self._data_folder / "projects" / f"{file_id}.json"
        
        with open(file_path, 'w') as f:
            json.dump(asdict(project), f, indent=2)
        
        self._projects[project.id] = project
    
    def get_all_projects(self) -> list[Project]:
        """Get all projects sorted by current user's last activity"""
        projects = list(self._projects.values())
        
        # Get user's last activity per project
        user_activity = self._get_user_last_activity()
        
        # Sort by user's last activity (desc), then by modified_at as fallback
        def sort_key(p):
            user_last = user_activity.get(p.id, "")
            return (user_last, p.modified_at or "")
        
        projects.sort(key=sort_key, reverse=True)
        return projects
    
    def _get_user_last_activity(self) -> dict[str, str]:
        """
        Get the current user's most recent time entry date for each project.
        Returns dict of project_id -> ISO datetime string
        """
        if not self._data_folder or not self.current_user_id:
            return {}
        
        time_dir = self._data_folder / "time"
        if not time_dir.exists():
            return {}
        
        user_id = self.current_user_id
        activity = {}  # project_id -> latest entry datetime
        
        # Scan only this user's time files
        for file_path in time_dir.glob(f"{user_id}_*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                for entry in data.get('entries', []):
                    project_id = entry.get('project_id')
                    # Use created_at, date, or fall back to legacy end_time
                    entry_time = entry.get('created_at') or entry.get('date') or entry.get('end_time', '')
                    
                    if project_id:
                        if project_id not in activity or entry_time > activity[project_id]:
                            activity[project_id] = entry_time
                            
            except (json.JSONDecodeError, IOError):
                continue
        
        return activity
    
    # =========================================================================
    # Time Entries
    # =========================================================================
    
    def _get_time_file_path(self, user_id: str, entry_date: date) -> Path:
        """Get the path for a user's daily time file"""
        date_str = entry_date.strftime("%Y-%m-%d")
        return self._data_folder / "time" / f"{user_id}_{date_str}.json"
    
    def load_today_entries(self) -> Optional[DailyTimeFile]:
        """Load today's time entries for the current user"""
        if not self._data_folder or not self.current_user_id:
            return None
        
        today = date.today()
        file_path = self._get_time_file_path(self.current_user_id, today)
        
        if not file_path.exists():
            self._today_entries = DailyTimeFile(
                user_id=self.current_user_id,
                date=today.strftime("%Y-%m-%d"),
                entries=[]
            )
            return self._today_entries
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Convert entry dicts to TimeEntry objects
        entries = [TimeEntry(**e) for e in data.get('entries', [])]
        self._today_entries = DailyTimeFile(
            user_id=data['user_id'],
            date=data['date'],
            entries=entries
        )
        return self._today_entries
    
    def save_time_entry(self, entry: TimeEntry):
        """Save a time entry to the appropriate date's file"""
        if not self._data_folder or not self.current_user_id:
            return
        
        # Parse entry date
        entry_date = date.fromisoformat(entry.date)
        
        # Get file path for this entry's date
        file_path = self._get_time_file_path(self.current_user_id, entry_date)
        
        # Load existing entries for that date, or create new
        if file_path.exists():
            with open(file_path, 'r') as f:
                data = json.load(f)
            entries = data.get('entries', [])
        else:
            entries = []
        
        # Add new entry
        entries.append(asdict(entry))
        
        # Save to file
        data = {
            'user_id': self.current_user_id,
            'date': entry.date,
            'entries': entries
        }
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        # If this was for today, update the cached entries
        if entry_date == date.today():
            self.load_today_entries()
    
    def get_today_total_hours(self) -> int:
        """Get total hours logged today"""
        if not self._today_entries:
            return 0
        return sum(e.hours for e in self._today_entries.entries)
    
    def get_project_total_hours(self, project_id: str) -> int:
        """Get total hours logged for a project across all users"""
        if not self._data_folder:
            return 0
        
        total_hours = 0
        time_dir = self._data_folder / "time"
        
        if not time_dir.exists():
            return 0
        
        for file_path in time_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                for entry in data.get('entries', []):
                    if entry.get('project_id') == project_id:
                        # Support both new 'hours' field and legacy 'duration_minutes'
                        if 'hours' in entry:
                            total_hours += entry.get('hours', 0)
                        elif 'duration_minutes' in entry:
                            total_hours += entry.get('duration_minutes', 0) // 60
            except (json.JSONDecodeError, TypeError):
                continue
        
        return total_hours
    
    # =========================================================================
    # Starred Projects (per-user)
    # =========================================================================
    
    def _get_starred_file_path(self) -> Path:
        """Get path to current user's starred projects file"""
        return self._data_folder / f"{self.current_user_id}_starred.json"
    
    def get_starred_projects(self) -> set[str]:
        """Get set of starred project IDs for current user"""
        if not self._data_folder or not self.current_user_id:
            return set()
        
        file_path = self._get_starred_file_path()
        if not file_path.exists():
            return set()
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                return set(data.get('starred', []))
        except (json.JSONDecodeError, IOError):
            return set()
    
    def set_project_starred(self, project_id: str, starred: bool):
        """Star or unstar a project for the current user"""
        if not self._data_folder or not self.current_user_id:
            return
        
        current_starred = self.get_starred_projects()
        
        if starred:
            current_starred.add(project_id)
        else:
            current_starred.discard(project_id)
        
        file_path = self._get_starred_file_path()
        with open(file_path, 'w') as f:
            json.dump({'starred': list(current_starred)}, f, indent=2)
    
    def is_project_starred(self, project_id: str) -> bool:
        """Check if a project is starred by the current user"""
        return project_id in self.get_starred_projects()
    
    # =========================================================================
    # Reload
    # =========================================================================
    
    def reload_all(self):
        """Reload all data from the filesystem"""
        if not self.is_configured():
            return
        
        self.load_team_data()
        self.identify_user()
        self.load_projects()
        self.load_today_entries()


# Global instance
data_service = DataService()
