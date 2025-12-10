# Time Tracker Project - Conversation Recap

**Date:** December 6, 2025

## The Problem

Don's team at Axway is in "Excel hell" - project tracking data is scattered across hundreds of spreadsheets in a OneDrive folder structure (20-25 root folders representing LMS catalogs/product lines, with potentially hundreds of subfolders containing project tracking sheets).

**Current pain points:**
- Time tracking requires manually entering data into spreadsheets buried deep in folder structures
- No central visibility across projects
- Double-entry: logging time somewhere, then transcribing to project sheets
- Hard to answer "where did my time go this week?" without drilling through dozens of folders
- Team wants to eventually feed this data into PowerBI

## The Spreadsheet Structure

Examined `2025_Tech_B2B_Training_Project_Tracking.xlsx` which contains:

**Timesheet tab (main tracking):**
- Course info: Campus, Offer, Sub Offer, Course ID, Course Name, Effort Type, Course Type, Status, Duration (view hours)
- Time by phase: Catalog Planning, Raw Content, Production, Availability
- Time by role within phases: SME, CA, Voiceover, Visual Design, Subtitles, AU Review, etc.
- Calculated fields: Total per phase, Grand Total, Ratio (total hours ÷ view hours), Lead Time

**Chunking Guide tabs:** Break courses into TMs (training modules) for production tracking - no time data, just status

**Key metric:** Ratio = Total Hours Spent ÷ Course Duration (view hours) - efficiency measure

## Proposed Solution

A personal time tracking app modeled after FlowPath's architecture - simple, local-first, solves Don's immediate problem without trying to replace the team system.

### Core Concept

**Timer-based time capture** tied to courses, with reporting and export.

The insight: Time tracking is inherently cross-project. Can't answer aggregate questions by drilling into folders. Need one place that captures time as it happens, then export/transcribe as needed.

### Proposed Screens (3-5 total)

1. **Timer Screen (Home)**
   - Course dropdown (populated from local DB or imported)
   - Big Start/Stop button
   - Running clock display
   - Today's entries list below

2. **Courses Screen**
   - Add/edit/archive courses
   - Fields: name, target view hours
   - Simple list view

3. **Reports Screen**
   - Date range picker
   - Entries grouped by course with totals
   - Ratio calculation (hours spent ÷ view hours)
   - Export to CSV/Excel

### Data Model

```
courses
├── id
├── name
├── view_hours (target duration)
├── archived (boolean)
└── created_at

time_entries
├── id
├── course_id (FK)
├── start_time
├── end_time
├── notes (optional)
└── calculated: duration
```

**Possible future addition:** work_type field (Voiceover, Visual Design, etc.) to map to spreadsheet columns

### Technical Approach

- Use FlowPath as the template (PyQt6, QStackedWidget, DataService singleton, SQLite)
- Same architectural patterns, simpler domain
- No screenshots, markdown, or nested steps needed
- openpyxl for Excel import/export (already familiar from Voxsmith)

### Import Capability

Can import course list from:
- Existing project tracking Excel files (pull Course Name + Duration from Timesheet tab)
- Simple CSV (name, view_hours)

"Point at a spreadsheet and slurp the courses out" flow is feasible.

## Key Decisions/Constraints

- **Personal tool first** - not trying to solve the team problem
- **Manager requirement:** Data should live with projects (but time tracking is inherently cross-project, so this tool fills a gap)
- **No direct write-back** to team spreadsheets (at least initially) - export clean numbers, manually transcribe
- **PowerBI compatibility** is a future consideration for the team

## The Pitch (If Needed)

> "The project-level tracking sheets are valuable for project-level visibility. But they're not designed for cross-project time reporting or feeding PowerBI. A lightweight app that tracks time centrally - using the same data model as the sheets - gives us accurate capture at the source and clean exports for both project sheets *and* aggregate reporting."

## Next Steps

- [ ] Sleep on it
- [ ] Decide if this is worth pursuing as a project
- [ ] If yes: sketch UI mockups
- [ ] If yes: scaffold from FlowPath structure
- [ ] If yes: build minimal timer + course list first

## Files Referenced

- `/mnt/user-data/uploads/2025_Tech_B2B_Training_Project_Tracking.xlsx` - Team project tracking template
- `/mnt/user-data/uploads/Flowpath.zip` - FlowPath source code as architectural reference
