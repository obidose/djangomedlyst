# MedLyst - Hospital Patient Management System

A Django-based web application for managing hospital inpatient workflows, designed for acute medical and surgical admissions.

![Patient List](https://github.com/user-attachments/assets/442227e2-f076-44ff-9d38-cd2c5ce15bd7)

## Features

### Patient Categories

The system supports a comprehensive 4-category workflow:

1. **ED Patients** - Patients in Emergency Department awaiting specialty referral
2. **Acute - In Process** - Active admissions undergoing clerking and post-take ward rounds
3. **Acute - Admitted** - Completed admissions under specialty team care
4. **Elective** - Planned admissions that bypass the acute workflow

### Core Views

- **Patient List** - Complete patient roster with filtering by team, specialty, status, and category
- **Take List** - Focused view of acute in-process patients with sortable columns for admission workflow tracking
- **Weekend Review** - Dedicated list of patients flagged for weekend review
- **Consults List** - Centralized consultation request management with status tracking

### Clinical Workflow

- **Referral System** - Refer ED patients to specialty teams with timestamp and reason tracking
- **Clerking Process** - Track clerking status (Awaiting/In Progress/Completed) with assigned doctor
- **Post-Take Ward Round (PTWR)** - Monitor PTWR completion with timestamps and doctor assignment
- **Admission Completion** - Transition patients from active workflow to admitted status
- **Ward Rounds** - Record post-take and general ward round entries with notes
- **Consult Requests** - Multi-specialty consultation system with status updates and comments
- **Task Management** - Create and track clinical tasks with priority levels

### Specialty Teams

- **Medicine** - Medical Team A & B
- **Surgery** - Surgical Team A & B
- **Orthopaedics**
- **Renal**
- **Ophthalmology**

### Advanced Features

- **Sortable Columns** - Interactive column sorting on take list (name, NHI, location, team, specialty, clerking, PTWR, referral time, arrival time, referral reason)
- **Priority Flagging** - Mark high-priority patients
- **Weekend Review** - Flag patients requiring weekend review
- **Team Transfers** - Move patients between specialty teams
- **Comprehensive Filtering** - Filter by multiple criteria simultaneously
- **Inline Compact Filters** - Space-efficient filter controls

## Screenshots

### Patient List View
![Patient List](https://github.com/user-attachments/assets/442227e2-f076-44ff-9d38-cd2c5ce15bd7)

### Patient Detail View
![Patient Detail](https://github.com/user-attachments/assets/8b64fc93-3f56-4242-98ff-194551cce5df)

## Technology Stack

- **Framework**: Django 4.2.26
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Language**: Python 3.12+
- **Frontend**: Django Templates with custom CSS

## Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- PostgreSQL 13+ (for production deployment)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/obidose/djangomedlyst.git
   cd djangomedlyst
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

4. **Generate test data** (200 patients across all categories)
   ```bash
   python manage.py generate_dummy_data
   ```

5. **Start the development server**
   ```bash
   python manage.py runserver
   ```

6. **Access the application**
   
   Open your browser to http://localhost:8000/

### PostgreSQL Configuration (Optional)

For production deployment with PostgreSQL:

1. Create a PostgreSQL database:
   ```bash
   psql -U postgres
   CREATE DATABASE medlyst_db;
   CREATE USER medlyst_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE medlyst_db TO medlyst_user;
   \q
   ```

2. Update `medlyst_project/settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'medlyst_db',
           'USER': 'medlyst_user',
           'PASSWORD': 'your_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

3. Run migrations and start the server as shown above.

## User Guide

### Patient Workflow

#### 1. ED Patient Referral
- **View**: Patient detail page for ED category patients
- **Action**: Click "Refer to Specialty Team"
- **Process**: Select specialty team, enter referral reason
- **Result**: Patient transitions to "Acute - In Process" category

#### 2. Clerking
- **View**: Patient detail page for acute in-process patients
- **Action**: Click "Update Clerking"
- **Process**: Set status (Awaiting/In Progress/Completed), assign doctor, add timestamp
- **Result**: Clerking status updated, visible on take list

#### 3. Post-Take Ward Round (PTWR)
- **View**: Patient detail page for acute in-process patients
- **Action**: Click "Update PTWR"
- **Process**: Set status, assign PTWR doctor, add timestamp
- **Result**: PTWR status updated, visible on take list

#### 4. Complete Admission
- **View**: Patient detail page (available when both clerking and PTWR are completed)
- **Action**: Click "Complete Admission"
- **Process**: Confirm completion
- **Result**: Patient transitions to "Acute - Admitted" category

#### 5. Team Changes
- **View**: Patient detail page for admitted/elective patients
- **Action**: Click "Change Specialty"
- **Process**: Select new specialty and team
- **Result**: Patient reassigned to new team

#### 6. Consultation Requests
- **View**: Patient detail page or Consults List
- **Action**: Click "Request Consult"
- **Process**: Select specialty, enter reason and urgency
- **Result**: Consult request created, appears in consults list
- **Follow-up**: Update consult status via consults list (Requested/Accepted/In Progress/Completed/Declined)

#### 7. Ward Rounds
- **View**: Patient detail page
- **Action**: Click "Add Ward Round"
- **Process**: Enter notes, assign doctor
- **Result**: Ward round entry created with timestamp

#### 8. Task Management
- **View**: Patient detail page
- **Action**: Click "Add Task"
- **Process**: Enter description, set priority, optionally assign doctor
- **Result**: Task created, appears in patient's task list
- **Follow-up**: Edit or complete tasks from patient detail page

### Take List Features

The **Take List** provides a focused view of patients in the acute admission workflow:

- Shows only "Acute - In Process" patients
- Displays workflow summary cards (Awaiting Clerking, In Progress, Awaiting PTWR, etc.)
- **Sortable columns**: Click any column header to sort (ascending/descending)
  - Patient name, NHI, Location, Team, Specialty
  - Clerking status, PTWR status
  - Referral time, Arrival time, Referral reason
- **Compact filters**: Team, Specialty, Clerking Status, PTWR Status
- **Visual indicators**: Priority flags (⚠), Weekend review badges (📅)

### Weekend Review List

- View all patients flagged for weekend review
- Filter by team, specialty, category, location
- Summary cards showing patient count by specialty
- One-click access to patient details and ward rounds

## Data Model

### Patient
Core patient information and workflow state:
- **Demographics**: Name, NHI number, date of birth, bed number
- **Admission Details**: Arrival datetime, admission type (Acute/Elective), location
- **Referral Info**: Referral source, referral time, referral to specialty datetime, referral reason
- **Clinical**: Presenting complaint, past medical history, summary
- **Assignment**: Current specialty, responsible team, patient category
- **Workflow Status**: Clerking status/doctor/timestamp, PTWR status/doctor/timestamp
- **Flags**: Priority flag, weekend review flag

### ConsultRequest
Consultation tracking:
- **Patient**: Foreign key to Patient
- **Specialty**: Target specialty for consultation
- **Reason**: Clinical indication for consult
- **Status**: Requested/Accepted/In Progress/Completed/Declined
- **Requestor**: Requesting doctor name
- **Reviewer**: Reviewing doctor name (optional)
- **Timestamps**: Requested at, reviewed at
- **Comments**: Reviewer feedback

### WardRound
Ward round documentation:
- **Patient**: Foreign key to Patient
- **Type**: Post-Take or General
- **Doctor**: Assigned clinician
- **Datetime**: Round timestamp
- **Notes**: Clinical notes and plan

### Task
Clinical task management:
- **Patient**: Foreign key to Patient
- **Description**: Task details
- **Priority**: Low/Medium/High/Urgent
- **Status**: Pending/In Progress/Completed
- **Assignment**: Created by, assigned to (doctor names)
- **Timestamps**: Created at, completed at

## Project Structure

```
djangomedlyst/
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── db.sqlite3                   # SQLite database (development)
├── medlyst_project/
│   ├── __init__.py
│   ├── settings.py             # Django settings
│   ├── urls.py                 # Root URL configuration
│   ├── wsgi.py                 # WSGI application
│   └── asgi.py                 # ASGI application
└── patients/
    ├── __init__.py
    ├── models.py               # Patient, ConsultRequest, WardRound, Task models
    ├── views.py                # View functions for all pages
    ├── urls.py                 # App-level URL routing
    ├── admin.py                # Django admin configuration
    ├── apps.py                 # App configuration
    ├── tests.py                # Unit tests
    ├── management/
    │   └── commands/
    │       └── generate_dummy_data.py  # Test data generator
    ├── migrations/             # Database migrations
    │   ├── 0001_initial.py
    │   └── ...
    └── templates/
        └── patients/
            ├── base.html                   # Base template
            ├── patient_list.html           # Main patient list
            ├── patient_detail.html         # Patient detail page
            ├── take_list.html              # Take list view
            ├── weekend_review_list.html    # Weekend review list
            ├── consults_list.html          # Consults list
            ├── referral_workflow.html      # Referral form
            ├── change_specialty.html       # Team change form
            ├── clerking_workflow.html      # Clerking update form
            ├── ptwr_workflow.html          # PTWR update form
            ├── complete_admission.html     # Admission completion
            ├── general_ward_round.html     # Ward round form
            ├── consult_request.html        # Consult request form
            ├── update_consult.html         # Consult status update
            ├── add_task.html               # Task creation form
            ├── edit_task.html              # Task edit form
            ├── edit_patient_info.html      # Patient info editor
            └── update_team.html            # Team update form
```

## Key Features by View

| View | URL | Description | Key Features |
|------|-----|-------------|--------------|
| Patient List | `/` | All patients | Filters by team, specialty, clerking, PTWR, admission type |
| Take List | `/take-list/` | Acute in-process only | Sortable columns, workflow summary, compact filters |
| Weekend Review | `/weekend-review/` | Weekend flagged patients | Specialty summary, multiple filters |
| Consults List | `/consults/` | All consultation requests | Status filtering, specialty filtering |
| Patient Detail | `/patient/<id>/` | Individual patient | Full clinical info, actions, history |

## Development

### Running Tests
```bash
python manage.py test patients
```

### Database Commands

**Create migrations after model changes:**
```bash
python manage.py makemigrations
```

**Apply migrations:**
```bash
python manage.py migrate
```

**Reset database and regenerate test data:**
```bash
python manage.py flush
python manage.py generate_dummy_data
```

### Admin Panel

Create a superuser to access the Django admin panel at `/admin/`:
```bash
python manage.py createsuperuser
```

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Run tests to ensure nothing breaks
5. Commit your changes (`git commit -am 'Add new feature'`)
6. Push to the branch (`git push origin feature/your-feature`)
7. Create a Pull Request

## License

This project is open source and available under the MIT License.

## Acknowledgments

Built with Django and designed for clinical workflow efficiency in hospital settings.