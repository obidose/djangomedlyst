from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
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
    """Handle patient referral to specialty team"""
    patient = get_object_or_404(Patient, id=patient_id)
    
    if request.method == 'POST':
        new_specialty = request.POST.get('specialty')
        new_team = request.POST.get('team')
        
        if new_specialty and new_team:
            patient.current_parent_specialty = new_specialty
            patient.current_responsible_team = new_team
            patient.referral_time = timezone.now()
            
            # If referred from ED to a specialty, trigger acute admission process
            if new_specialty != 'ED':
                patient.clerking_status = 'AWAITING'
                patient.post_take_ward_round_status = 'AWAITING'
            
            patient.save()
            messages.success(request, f'Patient referred to {new_team}')
            return redirect('patient_detail', patient_id=patient.id)
    
    context = {
        'patient': patient,
        'team_choices': Patient.TEAM_CHOICES,
        'specialty_choices': Patient.SPECIALTY_CHOICES,
    }
    
    return render(request, 'patients/referral_workflow.html', context)


def clerking_workflow(request, patient_id):
    """Handle patient clerking process"""
    patient = get_object_or_404(Patient, id=patient_id)
    
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
