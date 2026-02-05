import os
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User, Group
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from decimal import Decimal, InvalidOperation
from . import models
from django.contrib.auth import authenticate, login, logout
from datetime import date
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

#Phase 4 Done

#Determine if the user is a Student.
def is_student(user):
    return user.groups.filter(name="Students").exists()

#Determine if the user is a TA.
def is_ta(user):
    return user.groups.filter(name="Teaching Assistants").exists()

#Determine if the user is an anonymous.
def is_anonynous(user):
    return not user.is_authenticated

#Determine if the user is david.
def is_supervisor(user):
    return user.is_superuser

def pick_grader(assignment):
    group = models.Group.objects.get(name="Teaching Assistants")
    ta = group.user_set.annotate(total_assigned=Count('graded_set')).order_by('total_assigned').first()
    return ta

@login_required
def index(request):
    allAssignments = models.Assignment.objects.all().order_by('id')
    context = {
        'allAssignments':allAssignments
    }

    return render(request, "index.html", context)

@user_passes_test(is_ta)
@login_required
def submissions(request, assignment_id):
    errors = {}
    generic_errors = {}
    if request.method == "POST":
        grades = {}
        grades = extract_grades(request.POST)
        assignment_title = models.Assignment.objects.get(id=assignment_id).title

        for submission_id, grade in grades.items():
            submission = models.Submission.objects.filter(id=submission_id).first()
            if not submission:
                generic_errors.setdefault(submission_id, []).append(
                    f"Submission with id {submission_id} doesn't exist."
                )
                continue
            if (submission.assignment.title != assignment_title):
                generic_errors.setdefault(submission_id, []).append(
                    f"The submission id {submission_id} doesn't match with any assignment {assignment_title}"
                )
                continue
            submissionMaxPoints = submission.assignment.points
            if (grade == ""):
                submission.score = None
            else:
                try:
                    if (Decimal(grade) > submissionMaxPoints or Decimal(grade) < 0):
                        errors.setdefault(submission_id, []).append(
                            f"Grade must be more than 0 and less than {submissionMaxPoints}"
                        )
                        continue
                    else: 
                        submission.score = Decimal(grade)
                except InvalidOperation:
                    errors.setdefault(submission_id, []).append(
                        f"Grade must be a numerical value."
                    )
                    continue
            try:
                submission.change_grade(request.user, grade)
                submission.save()
            except PermissionDenied:
                errors.setdefault(submission_id, []).append("You are not authorized to grade this submission.")
                continue

        if not errors and not generic_errors:
            return redirect(f"/{assignment_id}/submissions/")

    try:
        assignment = models.Assignment.objects.get(id=assignment_id)
        grader = User.objects.get(username="g")
    except:
        raise Http404("Page not found.")

    studentDataCollection = []

    #Submssions are assigned to you.
    assignment = models.Assignment.objects.get(id=assignment_id)
    assignedSubmissions = models.Submission.objects.filter(assignment=assignment, grader=grader)    
    assignmentPoints = models.Assignment.objects.get(id=assignment_id).points

    for element in assignedSubmissions:
        studentDataCollection.append({
            'submission' : element,
            'submission_id' : element.id,
            'studentName' : models.User.objects.get(username = element.author).get_full_name(),
            'studentScore' : element.score
        })

    studentDataCollection.sort(key=lambda x: x['studentName'])
   
    context = {
        'assignmentTitle': assignment.title,
        'assignmentPoints': assignmentPoints,
        'studentDataCollection' : studentDataCollection,
        'assignment_id' : assignment_id, 
        'errors': errors,
        'generic_errors' : generic_errors
    }

    return render(request, "submissions.html", context)

@login_required
def assignment(request, assignment_id):
    #1-Student, 2-TA, 3-Anonymous, 4-Supervisor. 
    whichUser = [False, False, False, False]

    user = request.user

    file_error = ""
    isDue = False

    try:
        assignment = models.Assignment.objects.get(id=assignment_id)
    except models.Assignment.DoesNotExist:
        print("Assignment not found.")

    try:
        alice_submission = models.Submission.objects.filter(assignment=assignment, author__username=user).first()
    except models.Submission.DoesNotExist:
        print("Submission doesn't exist.")

    assignmentDueDate = assignment.deadline
    currentDate = date.today()
    if currentDate > assignmentDueDate:
        isDue = True

    #Determine if the user is a Student or TA.
    if (is_student(user)):
        whichUser[0] = True
    elif (is_ta(user)):
        whichUser[1] = True
    elif (is_anonynous(user)):
        whichUser[2] = True
    elif (is_supervisor(user)):
        whichUser[3] = True

    if request.method == "POST":
        file = request.FILES.get('file_input')
        if file:
            if file.size > 64 * 1024 * 1024:
                file_error = "File size exceeded 64 MiB."
            elif not file.name.endswith(".pdf"):
                file_error = "The uploaded file is not the right format."
            elif not next(file.chunks()).startswith(b'%PDF-'):
                file_error = "The uploaded file is not a valid PDF file."
            else:
                if alice_submission:
                    alice_submission.file = file
                else:
                    alice_submission = models.Submission.objects.create(
                        assignment = assignment,
                        author = models.User.objects.get(username=user),
                        grader = pick_grader(assignment),
                        score = None,
                        file = file
                    )
                
                if (isDue):
                    return HttpResponseBadRequest("The assignment is already due.")
                else:
                    alice_submission.save()
            
                return redirect(f"/{ assignment_id }/")
    
    if(whichUser[1] or whichUser[3]):
        #Get the original Assignment and count how many Submissions there are.
        try:
            allSubmissionsCount = assignment.submissions.all().count()
            grader = User.objects.get(username=user)
        except:
            raise Http404("Page not found.")
        
        assignmentTitle = assignment.title
        assignmentDeadline = assignment.deadline
        assignmentPoints = assignment.points

        #Count how many students are assigned to you.
        allGradedAssignmentsCount = grader.graded_set.filter(assignment=assignment).count()

        #Count how many Students are there.
        allStudentsCount = models.Group.objects.get(name="Students").user_set.count()

        context = {
            'assignment': assignment,
            'assignment_points': assignmentPoints,
            'allSubmissionsCount': allSubmissionsCount,
            'allStudentsCount': allStudentsCount,
            'allGradedAssignmentsCount': allGradedAssignmentsCount,
            'assignmentTitle': assignmentTitle,
            'assignmentDeadline': assignmentDeadline,
            'assignmentId': assignment_id,
            'whichUser' : whichUser
        }
    elif (whichUser[0]):
        assignmentTitle = assignment.title
        assignmentDeadline = assignment.deadline
        assignmentPoints = assignment.points

        #Count how many Students are there.
        allStudentsCount = models.Group.objects.get(name="Students").user_set.count()

        studentAssignmentGrade = models.Submission.objects.filter(assignment=assignment, author=user).first()

        #Check if the assignment is graded.
        if studentAssignmentGrade and studentAssignmentGrade.score is not None:
            filename = models.Submission.objects.get(assignment=assignment, author=user).file.name

            displayScore = round(studentAssignmentGrade.score, 0)
            displayPercentage = round(100/Decimal(assignment.points)*Decimal(studentAssignmentGrade.score))

            status = ("Your submission, " + filename + " received " + str(displayScore) + "/" 
            + str(assignment.points) + " (" + str(displayPercentage) + "%).")

            appendingScore=str(studentAssignmentGrade.score)
        #Check if the assignment is submitted but not graded.
        elif studentAssignmentGrade:
            filename = models.Submission.objects.get(assignment=assignment, author=user).file.name
            status = "Your submission, " + filename + ", is being graded."
            print(status)
        #Check if the assignment is submitted but not due yet.
        elif studentAssignmentGrade and (currentDate <= assignmentDueDate):
            filename = models.Submission.objects.get(assignment=assignment, author=user).file.name
            status = "Your current submission is " + filename
        #Check if the assignment is not submitted but not due yet.
        elif currentDate <= assignmentDueDate:
            status = "No current submission."
        #Check if the assignment is not submitted and already due.
        elif not studentAssignmentGrade and currentDate > assignmentDueDate:
            status = "You did not submit this assignment and received 0 points."

        context = {
            'assignment': assignment,
            'assignment_points': assignmentPoints,
            'allStudentsCount': allStudentsCount,
            'assignmentTitle': assignmentTitle,
            'assignmentDeadline': assignmentDeadline,
            'assignmentId': assignment_id,
            'alice_submission' : alice_submission,
            'whichUser' : whichUser,
            'status' : status,
            'isDue' : isDue,
            'fileError' : file_error
        }
    elif (whichUser[2]):
        assignmentTitle = assignment.title
        assignmentDeadline = assignment.deadline
        assignmentPoints = assignment.points

        context = {
            'assignment': assignment,
            'assignment_points': assignmentPoints,
            'assignmentTitle': assignmentTitle,
            'assignmentDeadline': assignmentDeadline,
            'assignmentId': assignment_id,
            'whichUser' : whichUser
        }

    return render(request, "assignment.html", context)

def login_form(request):
    username = None
    password = None

    next_url = request.GET.get('next', '/profile/')
    generic_errors = {}

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        if not username or not password:
            generic_errors.setdefault("empty_fields", []).append("Username and password are required.")
        else:
            authenticated_user = authenticate(request, username=username, password=password)

            if authenticated_user is not None:
                login(request, authenticated_user)

                if url_has_allowed_host_and_scheme(next_url, None):
                    return redirect(next_url)
                else:
                    return redirect('/')
            else:
                generic_errors.setdefault("invalid_credentials", []).append("Username and password do not match.")

    return render(request, "login.html", {"generic_errors": generic_errors, "next": next_url})

def logout_form(request):
    logout(request)
    return redirect(f"/profile/login/")

@login_required
def profile(request):
    assignments = models.Assignment.objects.all().order_by('id')    
    studentAssignmentGrade = 0

    #0-Student, 1-TA, 2-Anonymous, 3-Supervisor. 
    whichUser = [False, False, False, False]

    user = request.user

    #Determine if the user is a Student or TA.
    if (is_student(user)):
        whichUser[0] = True
    elif (is_ta(user)):
        whichUser[1] = True
    elif (is_anonynous(user)):
        whichUser[2] = True
    elif (is_supervisor(user)):
        whichUser[3] = True

    #Case 0: Student.
    if (whichUser[0]):
        try:
            student = User.objects.get(username=user)
        except:
            raise Http404("Page not found.")

        assignmentCollection = []
        totalEarnedPoints = 0
        totalMissingPoints = 0
        totalAvailablePoints = 0
        earnedPercentage = 0
        status = ""
        for assignment in assignments:
            assignmentTitle = assignment.title
            assignmentId = assignment.id
            assignmentWeight = assignment.weight
            
            assignmentDueDate = assignment.deadline
            currentDate = date.today()

            appendingScore = ""
            
            studentAssignmentGrade = models.Submission.objects.filter(assignment=assignment, author=student).first()

            #Check if the assignment is graded.
            if studentAssignmentGrade and studentAssignmentGrade.score is not None:
                totalEarnedPoints = totalEarnedPoints + Decimal(studentAssignmentGrade.score) * Decimal(assignment.weight)/100
                totalAvailablePoints = totalAvailablePoints + assignment.points

                filename = models.Submission.objects.get(assignment=assignment, author=user).file.name

                displayScore = round(studentAssignmentGrade.score, 0)
                displayPercentage = round(100/Decimal(assignment.points)*Decimal(studentAssignmentGrade.score))

                status = ("Your submission, " + filename + " received " + str(displayScore) + "/" 
                + str(assignment.points) + " (" + str(displayPercentage) + "%).")

                appendingScore=str(studentAssignmentGrade.score)
            #Check if the assignment is submitted but not graded.
            elif studentAssignmentGrade:
                appendingScore = "Ungraded"
                filename = models.Submission.objects.get(assignment=assignment, author=user).file.name
                status = "Your submission, " + filename + ", is being graded."
            #Check if the assignment is submitted but not due yet.
            elif studentAssignmentGrade and (currentDate <= assignmentDueDate):
                appendingScore = "Not Due"
                filename = models.Submission.objects.get(assignment=assignment, author=user).file.name
                status = "Your current submission is " + filename
            #Check if the assignment is not submitted but not due yet.
            elif currentDate <= assignmentDueDate:
                appendingScore = "Not Due"
                status = "No current submission."
            #Check if the assignment is not submitted and already due.
            elif not studentAssignmentGrade and currentDate > assignmentDueDate:
                totalMissingPoints = totalMissingPoints + assignment.points * assignment.weight/100
                totalAvailablePoints = totalAvailablePoints + assignment.points
                appendingScore = "Missing"
                status = "You did not submit this assignment and received 0 points."

            assignmentCollection.append({
                'assignmentId' : assignmentId,
                'assignmentTitles': assignmentTitle,
                'appendingScore' : appendingScore,
                'assignmentWeight' : assignmentWeight
            })

        earnedPercentage = round((totalEarnedPoints/totalAvailablePoints)*100, 2)

        context = {
            'graderName' : student.username,
            'assignments' : assignments,
            'assignmentCollection' : assignmentCollection,
            'user' : user,
            'whichUser' : whichUser,
            'earnedPercentage' : earnedPercentage,
            'status' : status
        }

    #Case 1: TA or Supervisor. 
    elif (whichUser[1] or whichUser[3]):
    #Get the original Assignment and count how many Submissions there are.
        try:
            grader = User.objects.get(username=user)
        except:
            raise Http404("Page not found.")
   
        assignmentCollection = []
        for assignment in assignments:
            assignmentTitle = assignment.title
            assignmentId = assignment.id
            assignedSubmissions = models.Submission.objects.filter(assignment=assignment, grader=grader).count()
            gradedSubmissions = models.Submission.objects.filter(assignment=assignment, grader=grader, score__isnull=False).count()
            submissionCount = models.Submission.objects.filter(assignment=assignment).count()
            gradedCount = models.Submission.objects.filter(assignment=assignment, score__isnull = False).count()

            assignmentCollection.append({
                'assignmentId' : assignmentId,
                'assignmentTitles': assignmentTitle,
                'assignedSubmissions':assignedSubmissions,
                'gradedSubmissions':gradedSubmissions,
                'submissionCount':submissionCount,
                'gradedCount':gradedCount
            })

        context = {
            'graderName' : grader.username,
            'assignments' : assignments,
            'assignmentCollection' : assignmentCollection,
            'user' : user,
            'whichUser' : whichUser
        }
    
    #Case 2: Anon
    elif (whichUser[2]):        
        assignmentCollection = []
        for assignment in assignments:
            assignmentTitle = assignment.title
            assignmentId = assignment.id
        
            assignmentCollection.append({
                    'assignmentId' : assignmentId,
                    'assignmentTitles': assignmentTitle
                })

        context = {
            'graderName' : 'AnonoymousUser',
            'assignments' : assignments,
            'assignmentCollection' : assignmentCollection,
            'user' : user,
            'whichUser' : whichUser
        }
        print(context)
    
    return render(request, "profile.html", context)
        
@login_required
def show_upload(request, filename):
    try:
        submission = models.Submission.objects.get(file__contains=filename)
        file = submission.view_submission(request.user)
        
    except models.Submission.DoesNotExist:
        raise Http404("File not found!")
    except PermissionDenied:
        raise Http404("Permission Denied.")
    
    file_path = submission.file.path
    file_name = os.path.basename(file_path)

    with open(file_path, 'rb') as file:
        # Construct the HttpResponse and set headers
        response = HttpResponse(file.read(), content_type="application/pdf")
        response['Content-Disposition'] = f'attachment; filename="{file_name}"' 

    return response


def extract_grades(post_data):
    grades = {}
    for key, value in post_data.items():
        if key.startswith("grade-"):
            submissions_id = int(key.removeprefix("grade-"))
            grades[submissions_id] = value

    return grades

