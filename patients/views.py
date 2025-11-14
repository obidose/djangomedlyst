from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q
from .models import Patient, ConsultRequest, WardRound, Task


def patient_list(request):
    """Display list of all patients with filtering"""
    patients = Patient.objects.all()
    
    # Apply filters
    team_filter = request.GET.get('team')
    specialty_filter = request.GET.get('specialty')
    clerking_filter = request.GET.get('clerking_status')
    ptwr_filter = request.GET.get('ptwr_status')
    admission_filter = request.GET.get('admission_type')
    
    if team_filter:
        patients = patients.filter(current_responsible_team=team_filter)
    if specialty_filter:
        patients = patients.filter(current_parent_specialty=specialty_filter)
    if clerking_filter:
        patients = patients.filter(clerking_status=clerking_filter)
    if ptwr_filter:
        patients = patients.filter(post_take_ward_round_status=ptwr_filter)
    if admission_filter:
        patients = patients.filter(admission_type=admission_filter)
    
    context = {
        'patients': patients,
        'team_filter': team_filter,
        'specialty_filter': specialty_filter,
        'clerking_filter': clerking_filter,
        'ptwr_filter': ptwr_filter,
        'admission_filter': admission_filter,
        'team_choices': Patient.TEAM_CHOICES,
        'specialty_choices': Patient.SPECIALTY_CHOICES,
        'clerking_choices': Patient.CLERKING_STATUS_CHOICES,
        'ptwr_choices': Patient.PTWR_STATUS_CHOICES,
        'admission_choices': Patient.ADMISSION_TYPE_CHOICES,
    }
    
    return render(request, 'patients/patient_list.html', context)


def patient_detail(request, patient_id):
    """Display detailed view of a single patient"""
    patient = get_object_or_404(Patient, id=patient_id)
    
    context = {
        'patient': patient,
        'consult_requests': patient.consult_requests.all(),
        'ward_rounds': patient.ward_rounds.all()[:10],  # Latest 10
        'tasks': patient.tasks.filter(status__in=['PENDING', 'IN_PROGRESS']),
    }
    
    return render(request, 'patients/patient_detail.html', context)


def referral_workflow(request, patient_id):
    """Handle patient referral from ED to specialty team"""
    patient = get_object_or_404(Patient, id=patient_id)
    
    # Only ED patients can be referred
    if not patient.is_ed_patient():
        messages.error(request, 'Only ED patients can be referred to specialty teams')
        return redirect('patient_detail', patient_id=patient.id)
    
    if request.method == 'POST':
        specialty = request.POST.get('specialty')
        team = request.POST.get('team', '')  # Team is optional, can be blank
        referral_reason = request.POST.get('referral_reason')
        
        if specialty:
            patient.current_parent_specialty = specialty
            patient.current_responsible_team = team  # Allow blank team
            patient.referral_reason = referral_reason or ''
            patient.referral_to_specialty_datetime = timezone.now()
            
            # All referrals from ED go to acute admission process
            patient.patient_category = 'ACUTE_INPROCESS'
            # Enable admission workflow
            patient.clerking_status = 'AWAITING'
            patient.post_take_ward_round_status = 'AWAITING'
            
            patient.save()
            team_display = patient.get_current_responsible_team_display() if team else 'No team assigned yet'
            messages.success(request, f'Patient referred to {patient.get_current_parent_specialty_display()} ({team_display})')
            return redirect('patient_detail', patient_id=patient.id)
    
    # Get specialty choices (exclude ED from options)
    specialty_choices = [(code, name) for code, name in Patient.SPECIALTY_CHOICES if code != 'ED']
    team_choices = Patient.TEAM_CHOICES
    
    return render(request, 'patients/referral_workflow.html', {
        'patient': patient,
        'specialty_choices': specialty_choices,
        'team_choices': team_choices,
    })


def clerking_workflow(request, patient_id):
    """Handle clerking workflow"""
    patient = get_object_or_404(Patient, id=patient_id)
    
    # ED patients shouldn't have clerking workflow
    if patient.is_ed_patient():
        messages.error(request, 'Clerking workflow not applicable for ED patients')
        return redirect('patient_detail', patient_id=patient.id)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        doctor = request.POST.get('doctor', '')
        
        patient.clerking_status = status
        patient.clerking_doctor = doctor
        
        if status == 'COMPLETED':
            patient.clerking_completed_at = timezone.now()
        
        patient.save()
        messages.success(request, f'Clerking status updated to {status}')
        return redirect('patient_detail', patient_id=patient.id)
    
    context = {
        'patient': patient,
        'status_choices': Patient.CLERKING_STATUS_CHOICES,
    }
    
    return render(request, 'patients/clerking_workflow.html', context)


def ptwr_workflow(request, patient_id):
    """Handle post-take ward round process"""
    patient = get_object_or_404(Patient, id=patient_id)
    
    # ED patients shouldn't have PTWR workflow
    if patient.is_ed_patient():
        messages.error(request, 'Post-take ward round workflow not applicable for ED patients')
        return redirect('patient_detail', patient_id=patient.id)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        doctor = request.POST.get('doctor', '')
        notes = request.POST.get('notes', '')
        
        patient.post_take_ward_round_status = status
        patient.ptwr_doctor = doctor
        
        if status == 'COMPLETED':
            patient.ptwr_completed_at = timezone.now()
            # Create ward round record
            WardRound.objects.create(
                patient=patient,
                ward_round_type='POST_TAKE',
                doctor=doctor,
                notes=notes,
                timestamp=timezone.now()
            )
        
        patient.save()
        messages.success(request, f'Post-take ward round status updated to {status}')
        return redirect('patient_detail', patient_id=patient.id)
    
    context = {
        'patient': patient,
        'status_choices': Patient.PTWR_STATUS_CHOICES,
    }
    
    return render(request, 'patients/ptwr_workflow.html', context)


def general_ward_round(request, patient_id):
    """Add a general ward round entry"""
    patient = get_object_or_404(Patient, id=patient_id)
    
    if request.method == 'POST':
        doctor = request.POST.get('doctor')
        notes = request.POST.get('notes')
        
        WardRound.objects.create(
            patient=patient,
            ward_round_type='GENERAL',
            doctor=doctor,
            notes=notes,
            timestamp=timezone.now()
        )
        
        messages.success(request, 'Ward round recorded')
        return redirect('patient_detail', patient_id=patient.id)
    
    context = {
        'patient': patient,
    }
    
    return render(request, 'patients/general_ward_round.html', context)


def consult_request(request, patient_id):
    """Request a consult for a patient"""
    patient = get_object_or_404(Patient, id=patient_id)
    
    if request.method == 'POST':
        specialty = request.POST.get('specialty')
        reason = request.POST.get('reason')
        requested_by = request.POST.get('requested_by')
        
        ConsultRequest.objects.create(
            patient=patient,
            specialty=specialty,
            reason=reason,
            requested_by=requested_by,
            requested_at=timezone.now()
        )
        
        messages.success(request, f'{specialty} consult requested')
        return redirect('patient_detail', patient_id=patient.id)
    
    context = {
        'patient': patient,
        'specialty_choices': ConsultRequest.SPECIALTY_CHOICES,
    }
    
    return render(request, 'patients/consult_request.html', context)


def add_task(request, patient_id):
    """Add a task for a patient"""
    patient = get_object_or_404(Patient, id=patient_id)
    
    if request.method == 'POST':
        description = request.POST.get('description')
        priority = request.POST.get('priority')
        assigned_to = request.POST.get('assigned_to', '')
        created_by = request.POST.get('created_by')
        
        Task.objects.create(
            patient=patient,
            description=description,
            priority=priority,
            assigned_to=assigned_to,
            created_by=created_by,
            created_at=timezone.now()
        )
        
        messages.success(request, 'Task added')
        return redirect('patient_detail', patient_id=patient.id)
    
    context = {
        'patient': patient,
        'priority_choices': Task.PRIORITY_CHOICES,
    }
    
    return render(request, 'patients/add_task.html', context)


def complete_admission(request, patient_id):
    """Mark admission as complete - move from ACUTE_INPROCESS to ACUTE_ADMITTED"""
    patient = get_object_or_404(Patient, id=patient_id)
    
    # Only acute in-process patients can complete admission
    if not patient.is_acute_inprocess():
        messages.error(request, 'Only patients in acute admission process can be marked as complete')
        return redirect('patient_detail', patient_id=patient.id)
    
    if not patient.can_complete_admission():
        messages.error(request, 'Both clerking and PTWR must be completed before completing admission')
        return redirect('patient_detail', patient_id=patient.id)
    
    if request.method == 'POST':
        patient.patient_category = 'ACUTE_ADMITTED'
        patient.save()
        messages.success(request, 'Admission marked as complete - patient moved to Acute Admitted category')
        return redirect('patient_detail', patient_id=patient.id)
    
    context = {
        'patient': patient,
    }
    
    return render(request, 'patients/complete_admission.html', context)


def take_list(request):
    """Display take list - acute in-process patients only"""
    # Get only ACUTE_INPROCESS patients
    patients = Patient.objects.filter(
        patient_category='ACUTE_INPROCESS'
    )
    
    # Handle sorting
    sort_by = request.GET.get('sort', 'referral_to_specialty_datetime')
    sort_order = request.GET.get('order', 'asc')
    
    # Valid sort fields
    valid_sorts = {
        'name': 'name',
        'nhi': 'nhi_number',
        'location': 'location',
        'team': 'current_responsible_team',
        'specialty': 'current_parent_specialty',
        'clerking': 'clerking_status',
        'ptwr': 'post_take_ward_round_status',
        'referred': 'referral_to_specialty_datetime',
        'arrival': 'datetime_of_arrival',
    }
    
    if sort_by in valid_sorts:
        field = valid_sorts[sort_by]
        if sort_order == 'desc':
            field = '-' + field
        patients = patients.order_by(field, 'datetime_of_arrival')
    else:
        patients = patients.order_by('referral_to_specialty_datetime', 'datetime_of_arrival')
    
    # Apply filters
    team_filter = request.GET.get('team')
    specialty_filter = request.GET.get('specialty')
    clerking_filter = request.GET.get('clerking_status')
    ptwr_filter = request.GET.get('ptwr_status')
    priority_filter = request.GET.get('priority')
    
    if team_filter:
        patients = patients.filter(current_responsible_team=team_filter)
    if specialty_filter:
        patients = patients.filter(current_parent_specialty=specialty_filter)
    if clerking_filter:
        patients = patients.filter(clerking_status=clerking_filter)
    if ptwr_filter:
        patients = patients.filter(post_take_ward_round_status=ptwr_filter)
    if priority_filter == 'true':
        patients = patients.filter(priority_flag=True)
    
    # Organize by workflow stage
    ed_patients = patients.filter(patient_category='ED').count()
    awaiting_clerking = patients.filter(
        patient_category='ACUTE_INPROCESS',
        clerking_status='AWAITING'
    ).count()
    clerking_in_progress = patients.filter(clerking_status='IN_PROGRESS').count()
    awaiting_ptwr = patients.filter(
        clerking_status='COMPLETED',
        post_take_ward_round_status='AWAITING'
    ).count()
    ptwr_in_progress = patients.filter(post_take_ward_round_status='IN_PROGRESS').count()
    ready_to_complete = patients.filter(
        patient_category='ACUTE_INPROCESS',
        clerking_status='COMPLETED',
        post_take_ward_round_status='COMPLETED'
    ).count()
    
    context = {
        'patients': patients,
        'team_filter': team_filter,
        'specialty_filter': specialty_filter,
        'clerking_filter': clerking_filter,
        'ptwr_filter': ptwr_filter,
        'priority_filter': priority_filter,
        'sort_by': sort_by,
        'sort_order': sort_order,
        'team_choices': Patient.TEAM_CHOICES,
        'specialty_choices': Patient.SPECIALTY_CHOICES,
        'clerking_choices': Patient.CLERKING_STATUS_CHOICES,
        'ptwr_choices': Patient.PTWR_STATUS_CHOICES,
        'workflow_stats': {
            'ed_patients': ed_patients,
            'awaiting_clerking': awaiting_clerking,
            'clerking_in_progress': clerking_in_progress,
            'awaiting_ptwr': awaiting_ptwr,
            'ptwr_in_progress': ptwr_in_progress,
            'ready_to_complete': ready_to_complete,
        }
    }
    
    return render(request, 'patients/take_list.html', context)


def change_specialty(request, patient_id):
    """Change patient specialty/team (for admitted patients)"""
    patient = get_object_or_404(Patient, id=patient_id)
    
    # Only for non-ED patients
    if patient.is_ed_patient():
        messages.error(request, 'ED patients must use the referral workflow')
        return redirect('patient_detail', patient_id=patient.id)
    
    if request.method == 'POST':
        new_specialty = request.POST.get('specialty')
        
        if new_specialty:
            # Auto-assign team based on specialty
            import random
            specialty_team_map = {
                'MEDICINE': ['MEDA', 'MEDB'],
                'SURGERY': ['SURGA', 'SURGB'],
                'ORTHOPAEDICS': ['ORTHO'],
            }
            new_team = random.choice(specialty_team_map.get(new_specialty, ['MEDA']))
            
            patient.current_parent_specialty = new_specialty
            patient.current_responsible_team = new_team
            patient.save()
            
            messages.success(request, f'Specialty changed to {patient.get_current_parent_specialty_display()} ({patient.get_current_responsible_team_display()})')
            return redirect('patient_detail', patient_id=patient.id)
    
    specialty_choices = [(code, name) for code, name in Patient.SPECIALTY_CHOICES if code != 'ED']
    
    context = {
        'patient': patient,
        'specialty_choices': specialty_choices,
    }
    
    return render(request, 'patients/change_specialty.html', context)


def toggle_priority(request, patient_id):
    """Toggle priority flag for patient"""
    patient = get_object_or_404(Patient, id=patient_id)
    patient.priority_flag = not patient.priority_flag
    patient.save()
    
    status = "enabled" if patient.priority_flag else "disabled"
    messages.success(request, f'Priority flag {status}')
    return redirect('patient_detail', patient_id=patient.id)


def toggle_weekend_review(request, patient_id):
    """Toggle weekend review flag for patient"""
    patient = get_object_or_404(Patient, id=patient_id)
    patient.weekend_review = not patient.weekend_review
    patient.save()
    
    status = "enabled" if patient.weekend_review else "disabled"
    messages.success(request, f'Weekend review flag {status}')
    return redirect('patient_detail', patient_id=patient.id)


def consults_list(request):
    """Display all consultation requests with specialty breakdown"""
    consults = ConsultRequest.objects.all().select_related('patient')
    
    # Apply filters
    status_filter = request.GET.get('status')
    specialty_filter = request.GET.get('specialty')
    
    if status_filter:
        consults = consults.filter(status=status_filter)
    if specialty_filter:
        consults = consults.filter(specialty=specialty_filter)
    
    # Get counts by status
    requested_count = ConsultRequest.objects.filter(status='REQUESTED').count()
    accepted_count = ConsultRequest.objects.filter(status='ACCEPTED').count()
    in_progress_count = ConsultRequest.objects.filter(status='IN_PROGRESS').count()
    completed_count = ConsultRequest.objects.filter(status='COMPLETED').count()
    declined_count = ConsultRequest.objects.filter(status='DECLINED').count()
    
    # Get counts by specialty
    specialty_counts = {}
    for code, name in ConsultRequest.SPECIALTY_CHOICES:
        count = ConsultRequest.objects.filter(specialty=code).exclude(status='COMPLETED').count()
        if count > 0:
            specialty_counts[name] = count
    
    context = {
        'consults': consults,
        'status_filter': status_filter,
        'specialty_filter': specialty_filter,
        'specialty_choices': ConsultRequest.SPECIALTY_CHOICES,
        'status_choices': ConsultRequest.STATUS_CHOICES,
        'requested_count': requested_count,
        'accepted_count': accepted_count,
        'in_progress_count': in_progress_count,
        'completed_count': completed_count,
        'declined_count': declined_count,
        'specialty_counts': specialty_counts,
    }
    
    return render(request, 'patients/consults_list.html', context)


def update_consult_status(request, consult_id):
    """Update consult request status with reviewer details"""
    consult = get_object_or_404(ConsultRequest, id=consult_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        reviewed_by = request.POST.get('reviewed_by', '')
        comments = request.POST.get('comments', '')
        
        consult.status = new_status
        consult.reviewed_by = reviewed_by
        consult.comments = comments
        
        if new_status in ['ACCEPTED', 'IN_PROGRESS', 'COMPLETED', 'DECLINED']:
            consult.reviewed_at = timezone.now()
        
        consult.save()
        messages.success(request, f'Consult status updated to {consult.get_status_display()}')
        return redirect('consults_list')
    
    context = {
        'consult': consult,
        'status_choices': ConsultRequest.STATUS_CHOICES,
    }
    
    return render(request, 'patients/update_consult.html', context)


def edit_patient_info(request, patient_id):
    """Edit patient clinical information"""
    patient = get_object_or_404(Patient, id=patient_id)
    
    if request.method == 'POST':
        patient.presenting_complaint = request.POST.get('presenting_complaint', '')
        patient.summary = request.POST.get('summary', '')
        patient.past_medical_history = request.POST.get('past_medical_history', '')
        patient.issues = request.POST.get('issues', '')
        patient.save()
        
        messages.success(request, 'Patient information updated successfully')
        return redirect('patient_detail', patient_id=patient.id)
    
    return render(request, 'patients/edit_patient_info.html', {'patient': patient})


def edit_task(request, task_id):
    """Edit or update task status"""
    task = get_object_or_404(Task, id=task_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update':
            task.description = request.POST.get('description', task.description)
            task.priority = request.POST.get('priority', task.priority)
            task.status = request.POST.get('status', task.status)
            task.assigned_to = request.POST.get('assigned_to', task.assigned_to)
            
            if task.status == 'COMPLETED' and not task.completed_at:
                task.completed_at = timezone.now()
            
            task.save()
            messages.success(request, 'Task updated successfully')
        elif action == 'complete':
            task.status = 'COMPLETED'
            task.completed_at = timezone.now()
            task.save()
            messages.success(request, 'Task marked as completed')
        elif action == 'delete':
            patient_id = task.patient.id
            task.delete()
            messages.success(request, 'Task deleted')
            return redirect('patient_detail', patient_id=patient_id)
        
        return redirect('patient_detail', patient_id=task.patient.id)
    
    return render(request, 'patients/edit_task.html', {
        'task': task,
        'priority_choices': Task.PRIORITY_CHOICES,
        'status_choices': Task.STATUS_CHOICES,
    })


def update_team(request, patient_id):
    """Update patient's team assignment"""
    patient = get_object_or_404(Patient, id=patient_id)
    
    # ED patients shouldn't have team updates (they get referred)
    if patient.is_ed_patient():
        messages.error(request, 'ED patients must be referred to a specialty first')
        return redirect('patient_detail', patient_id=patient.id)
    
    if request.method == 'POST':
        team = request.POST.get('team', '')
        patient.current_responsible_team = team
        patient.save()
        
        team_display = patient.get_current_responsible_team_display() if team else 'No team assigned'
        messages.success(request, f'Team updated to {team_display}')
        return redirect('patient_detail', patient_id=patient.id)
    
    # Get team choices (exclude ED)
    team_choices = [(code, name) for code, name in Patient.TEAM_CHOICES if code != 'ED']
    
    return render(request, 'patients/update_team.html', {
        'patient': patient,
        'team_choices': team_choices,
    })


def weekend_review_list(request):
    """Display weekend review list - patients flagged for weekend review"""
    # Get patients with weekend_review flag set to True
    patients = Patient.objects.filter(weekend_review=True)
    
    # Apply filters
    team_filter = request.GET.get('team')
    specialty_filter = request.GET.get('specialty')
    category_filter = request.GET.get('category')
    location_filter = request.GET.get('location')
    
    if team_filter:
        patients = patients.filter(current_responsible_team=team_filter)
    if specialty_filter:
        patients = patients.filter(current_parent_specialty=specialty_filter)
    if category_filter:
        patients = patients.filter(patient_category=category_filter)
    if location_filter:
        patients = patients.filter(location=location_filter)
    
    # Organize by specialty
    specialty_counts = {}
    for patient in patients:
        specialty = patient.get_current_parent_specialty_display() if patient.current_parent_specialty else 'Unassigned'
        specialty_counts[specialty] = specialty_counts.get(specialty, 0) + 1
    
    context = {
        'patients': patients,
        'team_filter': team_filter,
        'specialty_filter': specialty_filter,
        'category_filter': category_filter,
        'location_filter': location_filter,
        'team_choices': Patient.TEAM_CHOICES,
        'specialty_choices': Patient.SPECIALTY_CHOICES,
        'category_choices': [(code, name) for code, name in Patient.PATIENT_CATEGORY_CHOICES if code != 'ED'],
        'location_choices': Patient.LOCATION_CHOICES,
        'specialty_counts': specialty_counts,
        'total_count': patients.count(),
    }
    
    return render(request, 'patients/weekend_review_list.html', context)
