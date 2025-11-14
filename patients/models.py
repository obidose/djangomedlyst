from django.db import models
from django.utils import timezone


class Patient(models.Model):
    """Model representing a hospital inpatient"""
    
    # Patient Identification
    name = models.CharField(max_length=200)
    nhi_number = models.CharField(max_length=7, unique=True, help_text="National Health Index number")
    
    # Admission Details
    datetime_of_arrival = models.DateTimeField()
    presenting_complaint = models.TextField()
    summary = models.TextField(blank=True, help_text="Clinical summary")
    past_medical_history = models.TextField(blank=True)
    issues = models.TextField(blank=True, help_text="Current issues and problems")
    
    # Current Status
    SPECIALTY_CHOICES = [
        ('ED', 'Emergency Department'),
        ('MEDICINE', 'Medicine'),
        ('SURGERY', 'Surgery'),
        ('ORTHOPAEDICS', 'Orthopaedics'),
    ]
    
    TEAM_CHOICES = [
        ('ED', 'Emergency Department'),
        ('MEDA', 'Medical Team A'),
        ('MEDB', 'Medical Team B'),
        ('SURGA', 'Surgical Team A'),
        ('SURGB', 'Surgical Team B'),
        ('ORTHO', 'Orthopaedics'),
    ]
    
    current_parent_specialty = models.CharField(max_length=20, choices=SPECIALTY_CHOICES)
    current_responsible_team = models.CharField(max_length=10, choices=TEAM_CHOICES)
    
    # Patient Category
    PATIENT_CATEGORY_CHOICES = [
        ('ED', 'ED Patient'),
        ('ACUTE_INPROCESS', 'Acute - In Process'),
        ('ACUTE_ADMITTED', 'Acute - Admitted'),
        ('ELECTIVE', 'Elective'),
    ]
    
    patient_category = models.CharField(
        max_length=20,
        choices=PATIENT_CATEGORY_CHOICES,
        default='ED',
        help_text="Current patient category in workflow"
    )
    
    # Flags
    priority_flag = models.BooleanField(default=False, help_text="High priority patient")
    weekend_review = models.BooleanField(default=False, help_text="Flagged for weekend review")
    
    # Location Information (Read-only from external system)
    LOCATION_CHOICES = [
        ('ED', 'Emergency Department'),
        ('WARD1', 'Ward 1'),
        ('WARD2', 'Ward 2'),
        ('WARD3', 'Ward 3'),
        ('WARD4', 'Ward 4'),
        ('WARD5', 'Ward 5'),
    ]
    
    location = models.CharField(max_length=10, choices=LOCATION_CHOICES, default='ED')
    bed_number = models.IntegerField(null=True, blank=True, help_text="Bed number (1-16)")
    
    # Referral Information
    REFERRAL_SOURCE_CHOICES = [
        ('ED', 'Emergency Department'),
        ('CLINIC', 'Clinic'),
        ('GP', 'General Practitioner'),
    ]
    
    referral_source = models.CharField(max_length=10, choices=REFERRAL_SOURCE_CHOICES)
    referral_time = models.DateTimeField()
    referral_reason = models.TextField(blank=True, help_text="Reason for referral to specialty")
    referral_to_specialty_datetime = models.DateTimeField(null=True, blank=True, help_text="When referred from ED to specialty")
    
    # Clerking Information
    CLERKING_STATUS_CHOICES = [
        ('AWAITING', 'Awaiting'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('NOT_REQUIRED', 'Not Required'),
    ]
    
    clerking_status = models.CharField(
        max_length=15, 
        choices=CLERKING_STATUS_CHOICES,
        default='NOT_REQUIRED'
    )
    clerking_doctor = models.CharField(max_length=200, blank=True)
    clerking_completed_at = models.DateTimeField(null=True, blank=True)
    
    # Post Take Ward Round (PTWR)
    PTWR_STATUS_CHOICES = [
        ('AWAITING', 'Awaiting'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('NOT_REQUIRED', 'Not Required'),
    ]
    
    post_take_ward_round_status = models.CharField(
        max_length=15,
        choices=PTWR_STATUS_CHOICES,
        default='NOT_REQUIRED'
    )
    ptwr_doctor = models.CharField(max_length=200, blank=True)
    ptwr_completed_at = models.DateTimeField(null=True, blank=True)
    
    # Admission Type
    ADMISSION_TYPE_CHOICES = [
        ('ACUTE', 'Acute'),
        ('ELECTIVE', 'Elective'),
    ]
    
    admission_type = models.CharField(
        max_length=10,
        choices=ADMISSION_TYPE_CHOICES,
        default='ACUTE'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-datetime_of_arrival']
    
    def is_ed_patient(self):
        """Check if patient is in ED category"""
        return self.patient_category == 'ED'
    
    def is_acute_inprocess(self):
        """Check if patient is acute in process"""
        return self.patient_category == 'ACUTE_INPROCESS'
    
    def is_acute_admitted(self):
        """Check if patient is acute admitted (completed admission)"""
        return self.patient_category == 'ACUTE_ADMITTED'
    
    def is_elective(self):
        """Check if patient is elective"""
        return self.patient_category == 'ELECTIVE'
    
    def should_show_admission_workflow(self):
        """Check if patient should see clerking/PTWR options"""
        return self.patient_category == 'ACUTE_INPROCESS'
    
    def is_on_take_list(self):
        """Check if patient should appear on take list"""
        return self.patient_category in ['ED', 'ACUTE_INPROCESS']
    
    def can_complete_admission(self):
        """Check if admission can be marked as complete"""
        return (self.patient_category == 'ACUTE_INPROCESS' and 
                self.clerking_status == 'COMPLETED' and 
                self.post_take_ward_round_status == 'COMPLETED')
    
    def get_location_display_full(self):
        """Get full location display with bed number"""
        location = self.get_location_display()
        if self.bed_number:
            return f"{location} - Bed {self.bed_number}"
        return location
        
    def __str__(self):
        return f"{self.name} - {self.nhi_number}"


class ConsultRequest(models.Model):
    """Model representing a consult request for a patient"""
    
    SPECIALTY_CHOICES = [
        ('MEDICINE', 'Medicine'),
        ('SURGERY', 'Surgery'),
        ('ORTHOPAEDICS', 'Orthopaedics'),
        ('RENAL', 'Renal'),
        ('OPHTHALMOLOGY', 'Ophthalmology'),
    ]
    
    STATUS_CHOICES = [
        ('REQUESTED', 'Requested'),
        ('ACCEPTED', 'Accepted'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('DECLINED', 'Declined'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='consult_requests')
    specialty = models.CharField(max_length=20, choices=SPECIALTY_CHOICES)
    reason = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='REQUESTED')
    requested_by = models.CharField(max_length=200)
    requested_at = models.DateTimeField(default=timezone.now)
    reviewed_by = models.CharField(max_length=200, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    comments = models.TextField(blank=True, help_text="Reviewer comments")
    
    class Meta:
        ordering = ['-requested_at']
        
    def __str__(self):
        return f"{self.specialty} consult for {self.patient.name}"


class WardRound(models.Model):
    """Model representing a ward round entry for a patient"""
    
    WARD_ROUND_TYPE_CHOICES = [
        ('POST_TAKE', 'Post Take Ward Round'),
        ('GENERAL', 'General Ward Round'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='ward_rounds')
    ward_round_type = models.CharField(max_length=15, choices=WARD_ROUND_TYPE_CHOICES)
    doctor = models.CharField(max_length=200)
    notes = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"{self.ward_round_type} - {self.patient.name} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class Task(models.Model):
    """Model representing a pending task for a patient"""
    
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='tasks')
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    assigned_to = models.CharField(max_length=200, blank=True)
    created_by = models.CharField(max_length=200)
    created_at = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.description[:50]} - {self.patient.name}"
