from django.views.generic import ListView, CreateView, UpdateView, DetailView, RedirectView
from django.shortcuts import render, get_object_or_404
from .serializers import FileSerializer, UniversitySerializer,IpSerializer

from django.urls import reverse_lazy
from .models import Course, Faculty, File, University, Comment,Ip
from .forms import CourseForm, FileForm, FacultyForm, CommentForm,UniversityForm
from hitcount.views import HitCountDetailView

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, viewsets

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth.models import User





class CheckIp(generics.ListAPIView):
    serializer_class = IpSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = Ip.objects.all()
        address = self.request.query_params.get('address', None)
        print(address)
        if address is not None:
            queryset = queryset.filter(address=address)
        return queryset


class IpList(viewsets.ModelViewSet):
    queryset = Ip.objects.all()
    serializer_class = IpSerializer




class FileRecordView(APIView):
    """
    A class based view for creating and fetching student records
    """

    def get(self, format=None):
        """
        Get all the student records
        :param format: Format of the student records to return to
        :return: Returns a list of student records
        """
        files = File.objects.all()
        serializer = FileSerializer(files, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Create a student record
        :param format: Format of the student records to return to
        :param request: Request object for creating student
        :return: Returns a student record
        """
        serializer = UniversitySerializer(data=request.data)
        if serializer.is_valid(raise_exception=ValueError):
            serializer.create(validated_data=request.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.error_messages,
                        status=status.HTTP_400_BAD_REQUEST)


def home(request):
    universities = University.objects.all()
    faculties = Faculty.objects.all()
    courses = Course.objects.all()
    files = File.objects.all()
    return render(request, 'home.html',
                  {'university_list': universities, 'faculty_list': faculties, "course_list": courses,
                   "file_list": files})


def footerLinks(request):
    universities = University.objects.all()
    return render(request, 'base.html',
                  {'university_list': universities})


class CourseListView(ListView):
    model = Course
    context_object_name = 'courses'


class UniversitySingleView(DetailView):
    model = University
    template_name = 'documents/single_university.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(UniversitySingleView, self).get_context_data(**kwargs)
        # Add extra context from another model
        context['faculties'] = Faculty.objects.filter(university_id=self.kwargs['pk'])
        return context


class FacultySingleView(DetailView):
    model = Faculty
    template_name = 'documents/single_faculty.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(FacultySingleView, self).get_context_data(**kwargs)
        # Add extra context from another model
        context['courses'] = Course.objects.filter(faculty_id=self.kwargs['pk'])
        page_alt = University.objects.get(id=self.kwargs.get('pk_alt', ''))
        context['page_alt'] = page_alt

        return context


class CourseSingleView(DetailView):
    model = Course
    template_name = 'documents/single_course.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CourseSingleView, self).get_context_data(**kwargs)
        # Add extra context from another model
        context['files'] = File.objects.filter(course_id=self.kwargs['pk'])
        return context


# class FileSingleView(HitCountDetailView):
#     model = File
#     template_name = 'documents/single_file.html'
#     count_hit = True  # set to True if you want it to try and count the hit


def file_detail(request, pk):
    file = get_object_or_404(File, pk=pk)
    # List of active comments for this post
    comments = file.comments.filter(active=True)

    new_comment = None

    if request.method == 'POST':
        # A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.file = file
            new_comment.user=request.user
            # Save the comment to the database
            new_comment.save()
    else:
        comment_form = CommentForm()

    return render(request,
                  'documents/single_file.html',
                  {'file': file,
                   'comments': comments,
                   'new_comment': new_comment,
                   'comment_form': comment_form})


class FileLikeApi(APIView):
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk, format=None):
        pk = self.kwargs.get("pk")
        obj = get_object_or_404(File, pk=pk)
        url_ = obj.get_absolute_url()
        user_ = self.request.user
        updated = False
        liked = False
        counts = obj.likes.count()

        # print(user_)
        if user_.is_authenticated:
            if user_ in obj.likes.all():
                liked = False
                obj.likes.remove(user_)
            else:
                liked = True
                obj.likes.add(user_)
                updated = True

        data = {
            "updated": updated,
            "liked": liked,
            "likescount": counts
        }
        return Response(data)


class FileLikeRedirect(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        pk = self.kwargs.get("pk")
        print(pk)
        obj = get_object_or_404(File, pk=pk)
        url_ = obj.get_absolute_url()
        user_ = self.request.user
        # print(user_)
        if user_.is_authenticated:
            if user_ in obj.likes.all():
                obj.likes.remove(user_)
            else:
                obj.likes.add(user_)
        return url_


class UniversityListView(ListView):
    model = University
    template_name = 'documents/universities.html'
    context_object_name = 'universities'


class UniversityCreateView(CreateView):
    model = University
    success_url = reverse_lazy('home')
    form_class = UniversityForm


class FileCreateView(CreateView):
    model = File
    # fields = ('name', 'universigty', 'country', 'city')
    success_url = reverse_lazy('home')
    form_class = FileForm


class FacultyCreateView(CreateView):
    model = Faculty
    success_url = reverse_lazy('universities')
    form_class = FacultyForm


class CourseCreateView(CreateView):
    model = Course
    # fields = ('name', 'university', 'faculty')
    success_url = reverse_lazy('home')
    form_class = CourseForm


class CourseUpdateView(UpdateView):
    model = Course
    # fields = ('name', 'university', 'faculty')
    success_url = reverse_lazy('home')
    form_class = CourseForm


def load_faculties(request):
    university_id = request.GET.get('university')
    faculties = Faculty.objects.filter(university_id=university_id).order_by('name')
    return render(request, 'documents/faculty_dropdown_list_options.html', {'faculties': faculties})


def load_universities(request):
    course_id = request.GET.get('course')
    universities = University.objects.filter(course_id=course_id).order_by('name')
    return render(request, 'documents/university_dropdown_list_options.html', {'universities': universities})


def load_courses(request):
    faculty_id = request.GET.get('faculty')
    courses = Course.objects.filter(faculty_id=faculty_id).order_by('name')
    return render(request, 'documents/course_dropdown_list_options.html', {'courses': courses})
