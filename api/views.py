from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Student, Course, Graph, Task
import json
from pypdf import PdfReader
from docx import Document as DocxDocument
import io
import datetime

@csrf_exempt
def upload_course_view(request):
    if request.method == 'POST':
        try:
            if 'file' not in request.FILES:
                return JsonResponse({'status': 'error', 'message': 'No file uploaded'})
            
            file = request.FILES['file']
            file_name = file.name
            file_content = file.read()
            
            # Simple parsing logic
            text_content = ""
            if file_name.endswith('.pdf'):
                try:
                    reader = PdfReader(io.BytesIO(file_content))
                    for page in reader.pages:
                        text_content += page.extract_text()
                except:
                    text_content = "PDF Parsing Failed"
            elif file_name.endswith('.docx'):
                try:
                    doc = DocxDocument(io.BytesIO(file_content))
                    for para in doc.paragraphs:
                        text_content += para.text + "\n"
                except:
                    text_content = "Docx Parsing Failed"
            else:
                text_content = file_content.decode('utf-8', errors='ignore')

            if not request.user.is_authenticated:
                 return JsonResponse({'status': 'error', 'message': 'Not authenticated'})
            
            student = Student.objects.get(username=request.user.username)
            
            course = Course(
                name=file_name.split('.')[0],
                outline_text=text_content[:5000],
                owner=student,
                icon="dumpling"
            )
            course.save()
            
            return JsonResponse({'status': 'success', 'course_id': str(course.id)})
        except Exception as e:
             return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def set_thinking_type_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            thinking_type = data.get('thinking_type')
            
            if not request.user.is_authenticated:
                 return JsonResponse({'status': 'error', 'message': 'Not authenticated'})
                 
            student = Student.objects.get(username=request.user.username)
            student.thinking_type = thinking_type
            student.save()
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def generate_tasks_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            count = int(data.get('count', 3))
            
            if not request.user.is_authenticated:
                 return JsonResponse({'status': 'error', 'message': 'Not authenticated'})
            
            student = Student.objects.get(username=request.user.username)
            
            course = Course.objects.filter(owner=student).order_by('-created_at').first()
            if not course:
                return JsonResponse({'status': 'error', 'message': 'No course found'})
            
            # Generate Tasks
            tasks_data = []
            for i in range(count):
                task = Task(
                    content=f"Analyze {course.name} - Step {i+1}",
                    course=course,
                    owner=student,
                    status="pending"
                )
                task.save()
                tasks_data.append(str(task.id))
                
            # Generate Graph (Mock)
            nodes = [
                {'id': 1, 'label': course.name, 'shape': 'box', 'color': '#FFD54F'},
                {'id': 2, 'label': 'Concept A', 'shape': 'dot', 'color': '#FFAB91'},
                {'id': 3, 'label': 'Concept B', 'shape': 'dot', 'color': '#FFAB91'},
            ]
            edges = [
                {'from': 1, 'to': 2},
                {'from': 1, 'to': 3},
            ]
            
            graph = Graph(
                course=course,
                nodes=nodes,
                edges=edges,
                owner=student
            )
            graph.save()
            
            return JsonResponse({'status': 'success', 'graph_id': str(graph.id), 'task_ids': tasks_data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)


@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            major = data.get('major')
            
            if not username or not password:
                return JsonResponse({'status': 'error', 'message': 'Username and password required'})

            if User.objects.filter(username=username).exists():
                return JsonResponse({'status': 'error', 'message': 'Username exists'})
            
            user = User.objects.create_user(username=username, password=password)
            
            # Create Mongo Student
            student = Student(username=username)
            student.save()
            
            # Piggy complaint logic (Simple stub)
            complaint = f"Wow, {major}? Sounds tasty but tough!"
            
            login(request, user)
            return JsonResponse({'status': 'success', 'complaint': complaint})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                try:
                    student = Student.objects.get(username=username)
                    return JsonResponse({
                        'status': 'success', 
                        'username': username,
                        'thinking_type': student.thinking_type
                    })
                except Student.DoesNotExist:
                    # Auto-create if missing (legacy/error recovery)
                    student = Student(username=username)
                    student.save()
                    return JsonResponse({
                        'status': 'success', 
                        'username': username,
                        'thinking_type': student.thinking_type
                    })
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid credentials'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

def check_auth_view(request):
    if request.user.is_authenticated:
        try:
            student = Student.objects.get(username=request.user.username)
            return JsonResponse({
                'is_authenticated': True,
                'username': request.user.username,
                'thinking_type': student.thinking_type
            })
        except Student.DoesNotExist:
            return JsonResponse({'is_authenticated': True, 'username': request.user.username, 'thinking_type': None})
    return JsonResponse({'is_authenticated': False})

def logout_view(request):
    logout(request)
    return JsonResponse({'status': 'success'})

@csrf_exempt
def get_task_details_view(request):
    task_id = request.GET.get('id')
    try:
        task = Task.objects.get(id=task_id)
        return JsonResponse({
            'status': 'success',
            'task': {'id': str(task.id), 'content': task.content, 'status': task.status, 'course_name': task.course.name, 'course_icon': task.course.icon}
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@csrf_exempt
def get_dashboard_data_view(request):
    if not request.user.is_authenticated:
         return JsonResponse({'status': 'error', 'message': 'Not authenticated'})
    
    student = Student.objects.get(username=request.user.username)
    course = Course.objects.filter(owner=student).order_by('-created_at').first()
    if not course:
         return JsonResponse({'status': 'error', 'message': 'No course'})
         
    graph = Graph.objects.filter(course=course).order_by('-id').first()
    # Flexible date filter or just take latest batch
    tasks = Task.objects.filter(course=course).order_by('-date')[:5] # Simple fetch latest 5 for demo
    
    tasks_data = [{'id': str(t.id), 'content': t.content, 'status': t.status, 'is_completed': t.is_completed} for t in tasks]
    
    return JsonResponse({
        'status': 'success',
        'graph': {
            'nodes': graph.nodes if graph else [],
            'edges': graph.edges if graph else []
        },
        'tasks': tasks_data
    })

@csrf_exempt
def complete_task_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        task_id = data.get('task_id')
        status = data.get('status', 'completed')
        
        try:
            task = Task.objects.get(id=task_id)
            task.status = status
            task.is_completed = (status == 'completed')
            task.save()
            
            # Check if all relevant tasks are done
            # For demo, check the tasks returned in dashboard (latest batch)
            all_tasks = Task.objects.filter(course=task.course).order_by('-date')[:5]
            all_done = all([t.is_completed or t.status == 'skipped' for t in all_tasks])
            
            return JsonResponse({'status': 'success', 'all_done': all_done})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error'})

@csrf_exempt
def get_results_view(request):
    if not request.user.is_authenticated:
         return JsonResponse({'status': 'error', 'message': 'Not authenticated'})
    student = Student.objects.get(username=request.user.username)
    
    # Simple calculation
    tasks = Task.objects.filter(owner=student, is_completed=True).order_by('-date')[:5]
    earned = len(tasks)
    
    return JsonResponse({'status': 'success', 'carrots': earned, 'total_carrots': student.carrots + earned})
