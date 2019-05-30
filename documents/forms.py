from django import forms
from .models import Course, Faculty, File, Comment, University
from pdf2image import convert_from_bytes
import boto3
import io
from decouple import config
from django.contrib.auth.decorators import login_required

BUCKET_NAME = config('BUCKET_NAME', cast=str)  # replace with your bucket name
ACCESS_ID = config('ACCESS_ID')
ACCESS_KEY = config('ACCESS_KEY')


class UniversityForm(forms.ModelForm):
    class Meta:
        model = University
        fields = '__all__'


class FacultyForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = ('name', 'university')


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ('name', 'university', 'faculty')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['faculty'].queryset = Faculty.objects.none()

        if 'university' in self.data:
            try:
                university_id = int(self.data.get('university'))
                self.fields['faculty'].queryset = Faculty.objects.filter(university_id=university_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['faculty'].queryset = self.instance.university.faculty_set.order_by('name')


class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ('university', 'faculty', 'course', 'pdf', 'category')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['faculty'].queryset = Faculty.objects.none()
        self.fields['course'].queryset = Course.objects.none()

        if 'university' in self.data:
            try:
                university_id = int(self.data.get('university'))
                self.fields['faculty'].queryset = Faculty.objects.filter(university_id=university_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['university'].queryset = self.instance.course.university_set.order_by('name')

        if 'faculty' in self.data:
            try:
                faculty_id = int(self.data.get('faculty'))
                self.fields['course'].queryset = Course.objects.filter(faculty_id=faculty_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset

        print(self.data)

    def save(self, *args, **kwargs):

        file_object = super().save(*args, **kwargs)
        KEY = "media/" + str(file_object.pdf)  # replace with your object key

        s3 = boto3.client("s3", aws_access_key_id=ACCESS_ID, aws_secret_access_key=ACCESS_KEY, region_name='us-east-1')
        s3i = boto3.resource('s3',
                             aws_access_key_id=ACCESS_ID,
                             aws_secret_access_key=ACCESS_KEY)

        obj = s3.get_object(Bucket=BUCKET_NAME, Key=KEY)

        pages = convert_from_bytes(obj['Body'].read(), 100)
        i = 0
        for page in pages:
            i += 1

            out_img = io.BytesIO()
            page.save(out_img, "png")
            out_img.seek(0)
            s3.put_object(Bucket=BUCKET_NAME,
                          Key="media/" + file_object.university.name + "/" + file_object.faculty.name + "/" + file_object.course.name + "/" + file_object.pdf.name + "/" + str(
                              i) + ".png",
                          Body=out_img)
        t = File.objects.get(id=file_object.pk)
        t.images_number = i  # change field
        t.save()  # this will update only

        return file_object


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)
