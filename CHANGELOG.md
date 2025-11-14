# Changelog

All notable changes to the MedLyst project are documented in this file.

## [1.0.0] - 2025-11-14

### Added
- 4-category patient workflow system (ED, Acute - In Process, Acute - Admitted, Elective)
- Take List view with sortable columns for acute admission tracking
- Weekend Review list for flagged patients
- Consults management system with status tracking
- Interactive column sorting on take list (name, NHI, location, team, specialty, clerking, PTWR, referral time, arrival time, referral reason)
- Compact inline filters to save screen space
- Priority flagging for high-priority patients
- Weekend review flagging system
- Referral reason tracking and display
- Consult request comments field
- Task management with priority levels
- Ward round documentation (Post-Take and General)
- Team transfer functionality

### Changed
- Updated README.md with comprehensive documentation
- Simplified take list to show only Acute - In Process patients (removed ED category)
- Removed category column from take list (redundant with filtered view)
- Made filters more compact using inline display
- Replaced inline CSS styles with reusable CSS classes (.stat-value, .stat-red, etc.)
- Fixed NHI field display (was showing blank, now correctly displays nhi_number)
- Fixed admission type display (corrected method name)
- Updated empty state messages to reflect current system

### Removed
- IMPLEMENTATION_GUIDE.md (obsolete documentation)
- setup_new_system.sh (obsolete setup script)
- consults_list_fixed.html (duplicate template)
- consults_list_new.html (duplicate template)
- ED Patients card from take list workflow summary (no longer relevant)

### Fixed
- NHI column not populating on take list
- NHI sorting causing FieldError (changed from 'NHI' to 'nhi_number')
- Admission type showing blank (changed from get_patient_type to get_admission_type_display)
- Consult comments not visible on patient detail page
- Template consistency issues with inline styles

### Technical Improvements
- Centralized CSS styling in base.html
- Consistent use of Django's auto-generated display methods
- Clean separation of concerns in models, views, and templates
- Proper field naming conventions (nhi_number vs NHI)
- Removed code duplication across templates

## Project Structure (Post-Cleanup)
- Django 4.2.26
- SQLite (development) / PostgreSQL (production ready)
- Python 3.12+
- 20 URL routes
- 17 template files
- 4 models (Patient, ConsultRequest, WardRound, Task)
- 200 test patients via generate_dummy_data command
