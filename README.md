# Project Tracker

Time tracking for training development projects.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

## First Run

On first launch, you'll be prompted to select a data folder. This should be:
- A shared folder (like OneDrive) for team collaboration
- Or a local folder for personal use

The app will create the required folder structure:
```
YourDataFolder/
├── team_data.json      # Shared config (work types, employees, etc.)
├── projects/           # Project JSON files
└── time/               # Time entry JSON files
```

## Development

Project structure:
```
project_tracker/
├── main.py                 # Entry point
├── requirements.txt
└── app/
    ├── __init__.py
    ├── models.py           # Data classes
    ├── data_service.py     # File I/O singleton
    ├── main_window.py      # Main window with navigation
    └── screens/
        ├── home_screen.py          # Home screen with timer
        ├── admin_screen.py         # Admin screen for lookups
        ├── project_detail_screen.py # Project detail with tabs
        └── reports_screen.py       # Reports with export
```

## What's Implemented

- ✅ Project structure and data layer
- ✅ Home screen with timer display
- ✅ Clock In / Clock Out functionality
- ✅ Manual time entry
- ✅ Project list with hours logged
- ✅ JSON persistence (team_data, projects, time entries)
- ✅ Close warning when timer running
- ✅ OS username detection
- ✅ Admin screen with sidebar navigation
- ✅ CRUD for all lookup tables (employees, work types, etc.)
- ✅ Import from CSV/JSON for lookup tables
- ✅ Data folder selector
- ✅ Project Detail screen with tabs
- ✅ Details tab (view/edit all project fields)
- ✅ TMs / Chunking tab (dynamic - add/edit/delete TMs)
- ✅ Time Log tab (all entries for project)
- ✅ Create new project flow
- ✅ Reports screen with filtering
- ✅ Summary cards (total hours, projects, avg/day, ratio)
- ✅ By Project breakdown table
- ✅ By Work Type bar chart
- ✅ Export to CSV, Excel, JSON (PowerBI-ready)

## Future Enhancements

- Import projects from existing Excel tracking sheets
- Recent folders quick-switch
- Lead time calculation
- More report grouping options (by day, by user)
