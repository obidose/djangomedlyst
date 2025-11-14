# MedLyst - Hospital Patient Management System

A Django-based web application for managing hospital inpatient lists, built with Python and PostgreSQL.

![Patient List](https://github.com/user-attachments/assets/442227e2-f076-44ff-9d38-cd2c5ce15bd7)

## Features

### Patient Management
- Track 200+ patients with comprehensive medical information
- NHI number, arrival datetime, presenting complaint
- Past medical history tracking
- Current specialty and team assignment
- Referral source (ED/Clinic/GP) and referral time

### Clinical Workflow Support
- **Clerking Process**: Track clerking status (Awaiting/In Progress/Completed/Not Required)
- **Post-Take Ward Round (PTWR)**: Monitor PTWR status and assigned doctor
- **Ward Rounds**: Record general ward round stamps
- **Consult Requests**: Request consultations from multiple specialties (Medicine/Surgery/Orthopaedics/Renal/Ophthalmology)
- **Task Management**: Create and track pending tasks with priority levels

### Team Structure
- Emergency Department
- Medical Team A & B
- Surgical Team A & B
- Orthopaedics

### Advanced Filtering
Filter patient lists by:
- Team assignment
- Specialty
- Clerking status
- PTWR status
- Admission type (Acute/Elective)

### Workflow Support
Different patient pathways:
- **ED Patients**: Initially under ED, can be referred to specialty teams
- **Acute Admissions**: Follow full admission process (clerking → PTWR)
- **Elective Patients**: May skip acute admission process
- **Post-Acute**: Completed admission patients can still have ad-hoc ward rounds

## Screenshots

### Patient List View
![Patient List](https://github.com/user-attachments/assets/442227e2-f076-44ff-9d38-cd2c5ce15bd7)

### Patient Detail View
![Patient Detail](https://github.com/user-attachments/assets/8b64fc93-3f56-4242-98ff-194551cce5df)

## Technology Stack

- **Backend**: Django 4.2
- **Database**: PostgreSQL 13+
- **Language**: Python 3.8+

## Installation

### Prerequisites
- Python 3.8 or higher
- PostgreSQL 13 or higher
- pip (Python package manager)

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

3. **Configure PostgreSQL**
   
   Create a PostgreSQL database:
   ```bash
   psql -U postgres
   CREATE DATABASE medlyst_db;
   CREATE USER medlyst_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE medlyst_db TO medlyst_user;
   \q
   ```

4. **Update database settings**
   
   Edit `medlyst_project/settings.py` and update the DATABASES configuration:
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

5. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Generate dummy data**
   
   Create 200 test patients:
   ```bash
   python manage.py generate_dummy_data
   ```

7. **Create admin user (optional)**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   
   Open your browser and navigate to:
   - Main application: http://localhost:8000/
   - Admin panel: http://localhost:8000/admin/

## Usage

### Viewing Patient Lists
1. Navigate to the home page to see all patients
2. Use the filter options to narrow down the list by team, specialty, status, etc.
3. Click "View" on any patient to see detailed information

### Managing Patient Workflows

#### Refer a Patient to a Team
1. Open patient detail page
2. Click "Refer to Team"
3. Select destination team and provide referral notes
4. Submit to update patient's team assignment

#### Update Clerking Status
1. Open patient detail page
2. Click "Update Clerking"
3. Update status and assign a doctor
4. Submit to save changes

#### Record Post-Take Ward Round
1. Open patient detail page
2. Click "Update PTWR"
3. Update status and assign PTWR doctor
4. Submit to save changes

#### Add Ward Round
1. Open patient detail page
2. Click "Add Ward Round"
3. Enter ward round type and notes
4. Assign a doctor and submit

#### Request Consultation
1. Open patient detail page
2. Click "Request Consult"
3. Select specialty and urgency
4. Provide reason for consultation
5. Submit request

#### Add Task
1. Open patient detail page
2. Click "Add Task"
3. Enter task description and priority
4. Optionally assign to a specific doctor
5. Submit to create task

## Data Model

### Patient
- Name, NHI number
- Arrival datetime, referral source and time
- Presenting complaint, past medical history
- Current specialty, team, admission type
- Clerking status and doctor
- PTWR status and doctor

### Ward Round
- Patient reference
- Round type and datetime
- Assigned doctor
- Notes

### Consult Request
- Patient reference
- Requesting and consulting specialty
- Urgency level (Routine/Urgent/Emergency)
- Reason and status

### Pending Task
- Patient reference
- Description and priority (Low/Medium/High/Urgent)
- Status (Pending/In Progress/Completed)
- Assigned to and created by doctors

## Development

### Project Structure
```
djangomedlyst/
├── manage.py
├── requirements.txt
├── medlyst_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── patients/
    ├── models.py          # Data models
    ├── views.py           # View logic
    ├── urls.py            # URL routing
    ├── admin.py           # Admin panel config
    ├── templates/         # HTML templates
    └── management/
        └── commands/
            └── generate_dummy_data.py
```

### Running Tests
```bash
python manage.py test patients
```

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues or questions, please open an issue on GitHub.