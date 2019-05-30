from django.urls import path, include
from django.conf.urls import url
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

app_name = 'documents'

router = routers.DefaultRouter()
router.register(r'ips', views.IpList)

urlpatterns = [
    path('', include(router.urls)),

    # fomrs for adding objects #
    path('add/university/', views.UniversityCreateView.as_view(), name='university_add'),
    path('add/faculty/', views.FacultyCreateView.as_view(), name='faculty_add'),
    path('add/course/', views.CourseCreateView.as_view(), name='course_add'),
    path('add/file/', views.FileCreateView.as_view(), name='file_add'),
    # end of forms #


    # start of ajax calls #
    path('<int:pk>/', views.CourseUpdateView.as_view(), name='course_change'),
    path('ajax/load-faculties/', views.load_faculties, name='ajax_load_faculties'),  # <-- this one here
    path('ajax/load-universities/', views.load_universities, name='ajax_load_universities'),  # <-- this one here
    path('ajax/load-courses/', views.load_courses, name='ajax_load_courses'),  # <-- this one here
    # end of ajax calls #

    # start of like #
    path('file/<int:pk>/like', views.FileLikeRedirect.as_view(), name="like"),
    path('api/file/<int:pk>/like', views.FileLikeApi.as_view(), name="like-api"),
    # end of likes #

    # start of objects views #
    path('course/<int:pk>/', views.CourseSingleView.as_view(), name="course-detail"),
    path('file/<int:pk>/', views.file_detail, name="file-detail"),
    path('university/<int:pk>/', views.UniversitySingleView.as_view(), name="university-detail"),
    path('universities/', views.UniversityListView.as_view(), name="universities"),
    path('university/<int:pk_alt>/faculty/<int:pk>/', views.FacultySingleView.as_view(), name="faculty-detail"),
    # end of objects views #
    path('check/', views.CheckIp.as_view()),

    # url(r'api/list', views.get_file_list, name='get_file_list'),
]
# ,views.CourseSingleView.as_view()
urlpatterns += format_suffix_patterns([
    # API to map the student record
    url(r'^api/list/$',
        views.FileRecordView.as_view(),
        name='files_list'),
])
