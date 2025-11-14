from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
import random
from datetime import timedelta
from patients.models import Patient, ConsultRequest, WardRound, Task


class Command(BaseCommand):
    help = 'Generate 200 dummy patients for testing'

    def handle(self, *args, **options):
        fake = Faker()
        
        # Clear existing data
        self.stdout.write('Clearing existing patient data...')
        Patient.objects.all().delete()
        
        complaints = [
            'Chest pain', 'Shortness of breath', 'Abdominal pain', 'Headache',
            'Fever', 'Trauma', 'Fall', 'Syncope', 'Confusion', 'Seizure',
            'Back pain', 'Joint pain', 'Weakness', 'Dizziness', 'Nausea and vomiting',
            'Cough', 'Palpitations', 'Wound infection', 'Fracture', 'Laceration'
        ]
        
        pmh_options = [
            'Hypertension', 'Diabetes mellitus', 'Asthma', 'COPD', 'IHD',
            'Heart failure', 'Atrial fibrillation', 'CKD', 'Previous stroke',
            'Osteoarthritis', 'Depression', 'Anxiety', 'Hyperlipidemia',
            'Hypothyroidism', 'Previous MI', 'DVT/PE', 'Cancer', 'None known'
        ]
        
        doctors = [
            'Dr. Smith', 'Dr. Johnson', 'Dr. Williams', 'Dr. Brown', 'Dr. Jones',
            'Dr. Garcia', 'Dr. Miller', 'Dr. Davis', 'Dr. Rodriguez', 'Dr. Martinez',
            'Dr. Anderson', 'Dr. Taylor', 'Dr. Thomas', 'Dr. Moore', 'Dr. Jackson'
        ]
        
        self.stdout.write('Generating 200 patients...')
        
        for i in range(200):
            # Generate random arrival time within the last 30 days
            arrival_time = timezone.now() - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            # Determine admission type
            admission_type = random.choice(['ACUTE', 'ACUTE', 'ACUTE', 'ELECTIVE'])  # 75% acute
            
            # Determine referral source
            referral_source = random.choice(['ED', 'ED', 'CLINIC', 'GP'])  # 50% from ED
            
            # Determine specialty and team based on referral
            if referral_source == 'ED':
                # ED patients start in ED
                initial_specialty = 'ED'
                initial_team = 'ED'
            else:
                # Direct admissions to specialty
                specialty_team_map = {
                    'MEDICINE': ['MEDA', 'MEDB'],
                    'SURGERY': ['SURGA', 'SURGB'],
                    'ORTHOPAEDICS': ['ORTHO'],
                }
                initial_specialty = random.choice(['MEDICINE', 'SURGERY', 'ORTHOPAEDICS'])
                initial_team = random.choice(specialty_team_map[initial_specialty])
            
            # Determine clerking status
            if admission_type == 'ELECTIVE' or referral_source != 'ED':
                # Elective or direct admissions might not need acute process
                if random.random() < 0.3:  # 30% don't need clerking
                    clerking_status = 'NOT_REQUIRED'
                    ptwr_status = 'NOT_REQUIRED'
                else:
                    clerking_status = random.choice(['AWAITING', 'IN_PROGRESS', 'COMPLETED'])
                    ptwr_status = random.choice(['AWAITING', 'IN_PROGRESS', 'COMPLETED'])
            else:
                # Acute admissions from ED usually need full process
                clerking_status = random.choice(['AWAITING', 'IN_PROGRESS', 'COMPLETED'])
                ptwr_status = random.choice(['AWAITING', 'IN_PROGRESS', 'COMPLETED'])
            
            # Generate clerking details if applicable
            clerking_doctor = ''
            clerking_completed_at = None
            if clerking_status == 'COMPLETED':
                clerking_doctor = random.choice(doctors)
                clerking_completed_at = arrival_time + timedelta(hours=random.randint(1, 8))
            elif clerking_status == 'IN_PROGRESS':
                clerking_doctor = random.choice(doctors)
            
            # Generate PTWR details if applicable
            ptwr_doctor = ''
            ptwr_completed_at = None
            if ptwr_status == 'COMPLETED':
                ptwr_doctor = random.choice(doctors)
                if clerking_completed_at:
                    ptwr_completed_at = clerking_completed_at + timedelta(hours=random.randint(2, 12))
                else:
                    ptwr_completed_at = arrival_time + timedelta(hours=random.randint(3, 20))
            elif ptwr_status == 'IN_PROGRESS':
                ptwr_doctor = random.choice(doctors)
            
            # Generate NHI number (format: ABC1234)
            nhi_number = ''.join([
                chr(random.randint(65, 90)) for _ in range(3)
            ]) + ''.join([str(random.randint(0, 9)) for _ in range(4)])
            
            # Create patient
            patient = Patient.objects.create(
                name=fake.name(),
                nhi_number=nhi_number,
                datetime_of_arrival=arrival_time,
                presenting_complaint=random.choice(complaints),
                past_medical_history=', '.join(random.sample(pmh_options, random.randint(0, 4))),
                current_parent_specialty=initial_specialty,
                current_responsible_team=initial_team,
                referral_source=referral_source,
                referral_time=arrival_time - timedelta(hours=random.randint(0, 3)),
                clerking_status=clerking_status,
                clerking_doctor=clerking_doctor,
                clerking_completed_at=clerking_completed_at,
                post_take_ward_round_status=ptwr_status,
                ptwr_doctor=ptwr_doctor,
                ptwr_completed_at=ptwr_completed_at,
                admission_type=admission_type,
            )
            
            # Add some consult requests (30% of patients)
            if random.random() < 0.3:
                num_consults = random.randint(1, 3)
                for _ in range(num_consults):
                    ConsultRequest.objects.create(
                        patient=patient,
                        specialty=random.choice(['MEDICINE', 'SURGERY', 'ORTHOPAEDICS', 'RENAL', 'OPHTHALMOLOGY']),
                        reason=fake.sentence(),
                        status=random.choice(['REQUESTED', 'ACCEPTED', 'IN_PROGRESS', 'COMPLETED']),
                        requested_by=random.choice(doctors),
                        requested_at=arrival_time + timedelta(hours=random.randint(1, 48)),
                    )
            
            # Add ward rounds for completed patients (50% of completed)
            if ptwr_status == 'COMPLETED' and random.random() < 0.5:
                num_rounds = random.randint(1, 5)
                for j in range(num_rounds):
                    WardRound.objects.create(
                        patient=patient,
                        ward_round_type='GENERAL',
                        doctor=random.choice(doctors),
                        notes=fake.paragraph(),
                        timestamp=ptwr_completed_at + timedelta(days=j+1, hours=random.randint(8, 12)),
                    )
            
            # Add tasks (40% of patients)
            if random.random() < 0.4:
                num_tasks = random.randint(1, 3)
                task_descriptions = [
                    'Chase blood results', 'Organize imaging', 'Review medications',
                    'Arrange follow-up', 'Complete discharge summary', 'Update family',
                    'Consult dietitian', 'Physiotherapy referral', 'Social work referral'
                ]
                for _ in range(num_tasks):
                    Task.objects.create(
                        patient=patient,
                        description=random.choice(task_descriptions),
                        priority=random.choice(['LOW', 'MEDIUM', 'HIGH', 'URGENT']),
                        status=random.choice(['PENDING', 'IN_PROGRESS', 'COMPLETED']),
                        created_by=random.choice(doctors),
                        assigned_to=random.choice(doctors) if random.random() < 0.7 else '',
                        created_at=arrival_time + timedelta(hours=random.randint(1, 72)),
                    )
            
            if (i + 1) % 50 == 0:
                self.stdout.write(f'Created {i + 1} patients...')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created 200 patients!'))
        
        # Print summary
        total_patients = Patient.objects.count()
        acute_patients = Patient.objects.filter(admission_type='ACUTE').count()
        elective_patients = Patient.objects.filter(admission_type='ELECTIVE').count()
        
        self.stdout.write(f'\nSummary:')
        self.stdout.write(f'Total patients: {total_patients}')
        self.stdout.write(f'Acute admissions: {acute_patients}')
        self.stdout.write(f'Elective admissions: {elective_patients}')
        self.stdout.write(f'Consult requests: {ConsultRequest.objects.count()}')
        self.stdout.write(f'Ward rounds: {WardRound.objects.count()}')
        self.stdout.write(f'Tasks: {Task.objects.count()}')
