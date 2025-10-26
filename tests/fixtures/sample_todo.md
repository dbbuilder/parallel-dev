# ParallelDev - Sample TODO

## Phase 1: Foundation

### Database Layer
- [ ] High: Create database schema SQL file
- [x] High: Implement db_manager.py with connection management
- [~] Medium: Add database migration support

### Data Models
- [x] High: Create Project model class
- [x] High: Create Task model class
- [ ] Medium: Add model validation methods

### Core Services
- [ ] Critical: Implement recursive directory scanning
- [ ] High: Add project detection logic
- [~] Medium: Implement incremental scanning

## Phase 2: Parsing

### TODO Parser
- [ ] High: Implement TODO.md parser with checkbox detection
- [ ] High: Extract task status ([ ], [x], [~])
- [ ] Medium: Parse task hierarchy (stages, sections, priorities)

### Requirements Parser
- [ ] High: Implement REQUIREMENTS.md parser
- [ ] High: Extract requirements with MoSCoW priorities
- [ ] Low: Handle markdown formatting variations

## Completed Items

### Setup
- [x] High: Initialize project structure
- [x] Medium: Create configuration files
- [x] Low: Setup version control
