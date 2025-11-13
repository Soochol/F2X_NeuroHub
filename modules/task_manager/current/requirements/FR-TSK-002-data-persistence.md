---
id: FR-TSK-002
uuid: 8e206ef6-0963-4918-aba7-5de48f72256a
title: Task Data Persistence
module: task_manager
type: functional_requirement
priority: High
status: Draft
stakeholders:
  - Task Manager users
  - Desktop application developers
  - Data persistence specialists
gathered_date: 2025-11-13T00:00:00Z
---

# Task Data Persistence

## Overview

This document defines the functional requirements for persistent storage of task data in the Task Manager application. The system must automatically save tasks to a local JSON file and restore them when the application restarts, ensuring users never lose their task data.

## User Story

**As a** Task Manager user
**I want to** have my tasks automatically saved and restored
**So that** my task data persists across application sessions without manual save operations

## Functional Specification

### Inputs

**User Actions**:
- Add new task (triggers auto-save)
- Edit task (title, description, priority, due date, status)
- Delete task (triggers auto-save)
- Complete task (triggers auto-save)
- Application startup (triggers auto-load)

**System Inputs**:
- File system access permissions
- Available disk space
- Existing tasks.json file (if present)
- Corrupted or invalid JSON data (error case)

### Processing

**Storage Location Selection**:
1. Detect operating system (Windows, macOS, Linux)
2. Determine user data directory:
   - **Windows**: `%USERPROFILE%\.simpletaskmanager\`
   - **macOS**: `~/.simpletaskmanager/`
   - **Linux**: `~/.simpletaskmanager/`
3. Create directory if it doesn't exist
4. Set file path: `{user_data_dir}/tasks.json`

**Auto-Save Workflow** (triggered after any task modification):
1. Collect all current tasks from in-memory task list
2. If tasks.json exists → Create backup: `tasks.json.bak`
3. Serialize tasks to JSON format with proper structure
4. Write JSON to tasks.json with atomic write operation
5. If write fails → Keep tasks.json.bak, show error to user
6. If write succeeds → Remove old .bak file, keep new backup
7. Continue application operation regardless of save result

**Auto-Load Workflow** (on application startup):
1. Check if tasks.json exists in user data directory
2. If file exists:
   - Read file contents
   - Parse JSON with error handling
   - Validate JSON structure (version, tasks array)
   - Load tasks into in-memory task list
   - Update UI to display loaded tasks
3. If file doesn't exist:
   - Start with empty task list
   - Create empty tasks.json on first save
4. If JSON is corrupted:
   - Log error details
   - Show user-friendly error message
   - Preserve corrupted file as tasks.json.corrupted
   - Start with empty task list
   - Allow user to continue working

**Backup Management**:
- Before each save, rename existing tasks.json to tasks.json.bak
- Keep only one level of backup (single .bak file)
- If save fails, .bak file remains as last known good state
- User can manually restore from .bak if needed

**Data Validation**:
- Validate JSON structure matches expected schema
- Check for required fields (id, title, created_date, status)
- Validate data types (dates as ISO 8601 strings, status as enum)
- Skip invalid tasks, load valid ones
- Log validation errors

### Outputs

**Visible Outputs**:
- Tasks automatically appear after application restart
- No manual save button needed (auto-save is invisible)
- Error toast notification if save/load fails
- Success indicator in status bar (optional)

**File System Outputs**:
- **tasks.json**: Primary storage file
- **tasks.json.bak**: Backup of previous version
- **tasks.json.corrupted**: Preserved corrupted file (if corruption detected)
- **Directory**: `~/.simpletaskmanager/` created if missing

**JSON File Format**:
```json
{
  "version": "1.0",
  "last_modified": "2025-11-13T10:30:00Z",
  "tasks": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Complete project proposal",
      "description": "Write detailed proposal with budget and timeline",
      "created_date": "2025-11-10T09:00:00Z",
      "due_date": "2025-11-20T17:00:00Z",
      "status": "active",
      "priority": "high"
    },
    {
      "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
      "title": "Review code changes",
      "description": "Review pull request #123",
      "created_date": "2025-11-12T14:30:00Z",
      "due_date": "2025-11-15T18:00:00Z",
      "status": "active",
      "priority": "medium"
    }
  ]
}
```

**Error Outputs**:
- Error message: "Failed to save tasks. Data remains in memory."
- Error message: "Failed to load tasks. Starting with empty list."
- Error message: "Corrupted task file detected. Preserved as tasks.json.corrupted. Starting fresh."
- Log entries with detailed error information

## Business Rules

### BR-TSK-005: Immediate Auto-Save After Modifications
**Description**: All task modifications must trigger immediate save to prevent data loss.

**Rule**:
```
IF user performs ANY task modification (add, edit, delete, complete)
THEN:
  1. Update in-memory task list
  2. Immediately trigger auto-save
  3. Do NOT wait for user exit
  4. Do NOT batch saves
  5. Show brief "Saving..." indicator (< 100ms)
```

**Rationale**: Prevents data loss from application crashes, system shutdowns, or power failures.

### BR-TSK-006: Graceful Degradation on Save Failure
**Description**: Save failures must not crash the application or lose in-memory data.

**Rule**:
```
IF auto-save fails (disk full, permission denied, I/O error)
THEN:
  1. Keep tasks in memory (continue normal operation)
  2. Show non-blocking error notification to user
  3. Preserve last successful backup (.bak file)
  4. Retry save on next modification
  5. Log error details for debugging
  6. Do NOT terminate application
```

**Rationale**: Users should be able to continue working even if file system has temporary issues.

### BR-TSK-007: Corrupted File Handling with Data Preservation
**Description**: Corrupted JSON files must be preserved for recovery, not deleted.

**Rule**:
```
IF JSON parsing fails during load
THEN:
  1. Rename corrupted file to tasks.json.corrupted (with timestamp suffix if needed)
  2. Show error message: "Previous task file corrupted. Preserved as tasks.json.corrupted. Starting fresh."
  3. Start application with empty task list
  4. Allow user to manually inspect/recover corrupted file
  5. Log corruption details (line number, error message)
  6. Do NOT delete corrupted data
```

**Rationale**: Allows users or support to attempt manual data recovery from corrupted files.

### BR-TSK-008: Performance Limit - Maximum 1000 Tasks
**Description**: Enforce maximum task count to maintain performance and file size.

**Rule**:
```
IF task count reaches 1000
THEN:
  1. Disable "Add Task" button
  2. Show message: "Maximum task limit (1000) reached. Please archive or delete old tasks."
  3. Allow deletion and editing of existing tasks
  4. Suggest exporting old tasks (future feature)
```

**Rationale**: Large JSON files (>10,000 tasks) cause slow load times and high memory usage. 1000 tasks is reasonable limit.

### BR-TSK-009: Atomic Write Operations
**Description**: File writes must be atomic to prevent partial write corruption.

**Rule**:
```
WHEN saving tasks.json:
  1. Write to temporary file: tasks.json.tmp
  2. Verify write success
  3. Atomically rename tasks.json.tmp to tasks.json (overwrites old file)
  4. If rename fails, keep old tasks.json intact
```

**Rationale**: Prevents corruption from interrupted writes (crash, power loss during save).

### BR-TSK-010: Cross-Platform Path Handling
**Description**: File paths must work correctly on Windows, macOS, and Linux.

**Rule**:
```
WHEN determining user data directory:
  - Use Path from pathlib (not string concatenation)
  - Use Path.home() for user home directory
  - Use Path.mkdir(parents=True, exist_ok=True) for directory creation
  - Do NOT hardcode path separators (/, \)
  - Test on all three platforms
```

**Rationale**: Ensures consistent behavior across operating systems.

## Acceptance Criteria

### AC-TSK-002-01: Auto-Save After Task Addition

**Given**: Application is running with empty task list
**When**: User adds new task "Buy groceries" with priority "medium" and due date "2025-11-15"
**Then**:
- Task appears in UI immediately
- Auto-save triggers within 100ms
- tasks.json file is created in `~/.simpletaskmanager/`
- File contains task data with correct JSON structure
- File version field is "1.0"
- Task ID is valid UUID
- Timestamps are in ISO 8601 format

**Test Data**:
```json
{
  "version": "1.0",
  "last_modified": "2025-11-13T10:30:00Z",
  "tasks": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Buy groceries",
      "description": "",
      "created_date": "2025-11-13T10:30:00Z",
      "due_date": "2025-11-15T00:00:00Z",
      "status": "active",
      "priority": "medium"
    }
  ]
}
```

**Verification**:
- Assert file exists at expected path
- Parse JSON and verify structure
- Assert task count == 1
- Assert task title == "Buy groceries"

### AC-TSK-002-02: Auto-Load on Application Restart

**Given**: tasks.json exists with 3 tasks
**When**: User closes application and restarts it
**Then**:
- Application reads tasks.json during startup
- All 3 tasks appear in task list
- Task details match saved data (title, description, dates, priority, status)
- Task order is preserved
- UI displays tasks within 500ms of launch

**Test Data**:
```json
{
  "version": "1.0",
  "tasks": [
    {"id": "uuid-1", "title": "Task 1", "status": "active", "priority": "high"},
    {"id": "uuid-2", "title": "Task 2", "status": "completed", "priority": "low"},
    {"id": "uuid-3", "title": "Task 3", "status": "active", "priority": "medium"}
  ]
}
```

**Verification**:
- Assert task list contains 3 tasks
- Assert task titles match
- Assert task priorities match
- Assert task statuses match

### AC-TSK-002-03: Corrupted JSON Handling

**Given**: tasks.json contains invalid JSON (missing closing brace, invalid characters)
**When**: User launches application
**Then**:
- JSON parsing fails
- Application catches exception
- Corrupted file renamed to tasks.json.corrupted (with timestamp)
- Error toast displays: "Previous task file corrupted. Preserved as tasks.json.corrupted. Starting fresh."
- Application starts with empty task list
- User can add new tasks normally
- Corrupted file remains for manual inspection

**Test Data**:
```json
{
  "version": "1.0",
  "tasks": [
    {"id": "uuid-1", "title": "Task 1"  // Missing closing brace
```

**Verification**:
- Assert tasks.json.corrupted file exists
- Assert task list is empty
- Assert error message displayed
- Assert application remains running

### AC-TSK-002-04: Backup Creation Before Save

**Given**: tasks.json exists with 2 tasks
**When**: User adds a third task (triggering auto-save)
**Then**:
- Before writing new tasks.json, existing file is copied to tasks.json.bak
- New tasks.json is written with 3 tasks
- Both tasks.json and tasks.json.bak exist
- tasks.json.bak contains previous state (2 tasks)
- tasks.json contains current state (3 tasks)

**Test Data**:
```python
# Before save
tasks_before = 2

# After save
tasks_after = 3
backup_tasks = 2  # Backup has previous state
```

**Verification**:
- Assert tasks.json.bak exists
- Parse both files
- Assert tasks.json has 3 tasks
- Assert tasks.json.bak has 2 tasks

### AC-TSK-002-05: Save Failure Graceful Handling

**Given**: Application is running with 2 tasks
**When**: Disk becomes full or write permission denied
**Then**:
- Auto-save attempt fails
- Application catches I/O exception
- Error notification displays: "Failed to save tasks. Data remains in memory."
- Tasks remain visible in UI (in-memory data intact)
- User can continue working (add, edit tasks in memory)
- Application does NOT crash
- tasks.json.bak remains unchanged (last known good state preserved)

**Test Data**:
```python
# Simulate write failure
simulate_disk_full()  # or simulate_permission_denied()

# Expected behavior
tasks_in_memory = 2
application_running = True
error_notification_shown = True
```

**Verification**:
- Assert application still running
- Assert task list visible with 2 tasks
- Assert error notification displayed
- Assert no data loss in memory

### AC-TSK-002-06: Cross-Platform Path Handling - Windows

**Given**: Running on Windows 10/11
**When**: Application starts
**Then**:
- User data directory is `C:\Users\{username}\.simpletaskmanager\`
- Directory is created if missing
- tasks.json path uses Windows path format
- File operations succeed

**Test Data**:
```python
import os
expected_path = os.path.expanduser(r"~\.simpletaskmanager\tasks.json")
```

**Verification**:
- Assert Path.home() resolves correctly
- Assert directory exists after startup
- Assert tasks.json uses correct path separator

### AC-TSK-002-07: Cross-Platform Path Handling - macOS/Linux

**Given**: Running on macOS or Linux
**When**: Application starts
**Then**:
- User data directory is `/home/{username}/.simpletaskmanager/` or `/Users/{username}/.simpletaskmanager/`
- Directory is created if missing
- tasks.json path uses Unix path format
- File operations succeed

**Test Data**:
```python
import os
expected_path = os.path.expanduser("~/.simpletaskmanager/tasks.json")
```

**Verification**:
- Assert Path.home() resolves correctly
- Assert directory exists after startup
- Assert tasks.json uses correct path separator

### AC-TSK-002-08: Task Count Limit Enforcement

**Given**: Application has 999 tasks loaded
**When**: User adds 1 more task (reaching 1000 limit)
**Then**:
- Task is added successfully
- Auto-save completes
- "Add Task" button becomes disabled
- Warning message displays: "Maximum task limit (1000) reached. Please archive or delete old tasks."
- User can still edit and delete existing tasks

**Test Data**:
```python
initial_task_count = 999
final_task_count = 1000
add_button_enabled = False
```

**Verification**:
- Assert task count == 1000
- Assert "Add Task" button disabled
- Assert warning message displayed

### AC-TSK-002-09: Atomic Write Prevents Corruption

**Given**: Application is saving tasks during power loss simulation
**When**: Power failure occurs mid-write (simulated)
**Then**:
- Temporary file tasks.json.tmp is abandoned
- Original tasks.json remains intact (not corrupted)
- On next application start, tasks.json loads successfully
- No data corruption occurred

**Test Data**:
```python
# Simulate interrupted write
simulate_power_loss_during_write()

# Expected outcome
tasks_json_intact = True
tasks_json_corrupted = False
```

**Verification**:
- Assert tasks.json is valid JSON after interruption
- Assert no partial writes in tasks.json
- Assert data loads correctly on restart

### AC-TSK-002-10: Timestamp Accuracy in JSON

**Given**: User adds task at specific time
**When**: Task is saved to JSON
**Then**:
- created_date matches actual task creation time (within 1 second accuracy)
- due_date matches user-specified date
- last_modified timestamp matches save time
- All timestamps use ISO 8601 format with timezone (UTC)

**Test Data**:
```json
{
  "id": "uuid-123",
  "title": "Test Task",
  "created_date": "2025-11-13T10:30:45Z",
  "due_date": "2025-11-20T00:00:00Z",
  "last_modified": "2025-11-13T10:30:45Z"
}
```

**Verification**:
- Assert timestamps are ISO 8601 compliant
- Assert created_date within 1 second of actual creation time
- Assert timezone is UTC (Z suffix)

## Non-Functional Requirements

### Performance

- **Save Time**: Auto-save must complete within 100ms for up to 1000 tasks
- **Load Time**: Application startup with 1000 tasks must complete within 500ms
- **File Size**: tasks.json with 1000 tasks should be < 500 KB
- **Memory Usage**: In-memory task storage should use < 10 MB for 1000 tasks

### Reliability

- **Data Integrity**: Zero data loss on normal application exit
- **Crash Recovery**: Minimal data loss (last unsaved change only) on crash
- **Backup Reliability**: tasks.json.bak must always be valid, loadable file
- **Error Recovery**: 100% application uptime despite save/load failures

### Usability

- **Invisible Saves**: User should not need to manually trigger saves
- **Fast Feedback**: Save operation should feel instant (no blocking UI)
- **Clear Error Messages**: Non-technical users should understand error notifications
- **No Data Loss Anxiety**: Users should trust that data is always saved

### Security

- **No Sensitive Data Exposure**: Task data stored in user's home directory (standard practice)
- **File Permissions**: tasks.json readable/writable only by owner (Unix: 600, Windows: ACL)
- **No Network Transmission**: All data remains local (no cloud sync in MVP)

### Maintainability

- **Simple Format**: JSON format is human-readable and easy to debug
- **Version Field**: JSON includes version field for future migration support
- **Extensibility**: Additional task fields can be added without breaking old versions

## Dependencies

### Technical Dependencies

- **Python**: 3.8+ (pathlib, json modules)
- **PySide6**: Not required for persistence (plain Python file I/O)
- **Operating System**: Windows 10+, macOS 12+, Linux with standard filesystem

### Document Dependencies

- **Depends On**:
  - FR-TSK-001 (Task Management - defines task data structure)
- **Required By**:
  - AC-TSK-002 (Acceptance Test Plan for Data Persistence)
  - Future: FR-TSK-005 (Task Export/Import)

## Constraints

### Technical Constraints

- Must use JSON format (not binary, not database)
- Must use standard Python libraries (no third-party persistence libraries)
- Must work offline (no cloud storage in MVP)
- Must handle Unicode task titles (support multiple languages)

### Business Constraints

- Must be file-based (not database) for MVP simplicity
- Must store in user directory (not system directory, no admin privileges)
- Must be human-readable (users can manually inspect/edit JSON)

### Regulatory Constraints

- None (local-only personal productivity app)

## Open Questions

None - all requirements clarified during requirements gathering session.

## Revision History

| Version | Date       | Author              | Changes                        |
|---------|------------|---------------------|--------------------------------|
| 1.0     | 2025-11-13 | Requirements Agent  | Initial requirements document  |
