# Create your models here.
from django.db import models
from PyPDF2 import PdfFileReader
from django.core.files.storage import default_storage as storage
import boto3
from decouple import config
from django.conf import settings
from django.urls import reverse

BUCKET_NAME = config('BUCKET_NAME', cast=str)  # replace with your bucket name
ACCESS_ID = config('ACCESS_ID')
ACCESS_KEY = config('ACCESS_KEY')



class Ip(models.Model):
    address=models.CharField(max_length=20)

    def __str__(self):
        return self.address


class University(models.Model):
    name = models.CharField(max_length=50)


    def __str__(self):
        return self.name


class Faculty(models.Model):
    name = models.CharField(max_length=50)
    university = models.ForeignKey(
        'University',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=50)
    university = models.ForeignKey(
        'University',
        on_delete=models.CASCADE
    )
    faculty = models.ForeignKey(
        'Faculty',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class File(models.Model):
    img_list = []

    categories_choices = [("أسئلة سنوات", "أسئلة سنوات"), ("ملخصات", 'ملخصات')]
    # university = models.OneToOneField(University, on_delete=models.CASCADE)
    university = models.ForeignKey(
        'University',
        on_delete=models.CASCADE
    )
    faculty = models.ForeignKey(
        'Faculty',
        on_delete=models.CASCADE
    )
    course = models.ForeignKey(
        'Course',
        on_delete=models.CASCADE,
    )
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='file_likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return "/file/%i/" % self.id

    def get_like_url(self):
        return reverse("documents:like", kwargs={"pk": self.pk})

    def get_api_like_url(self):
        return reverse("documents:like-api", kwargs={"pk": self.pk})

    created_at_date = models.DateTimeField(auto_now_add=True)

    category = models.CharField(max_length=20, choices=categories_choices)
    pdf = models.FileField()
    thumbnail = models.CharField(max_length=1000)
    images_number = models.PositiveIntegerField(default=1)

    def get_numofpages(self):
        ff = storage.open(self.pdf.name, 'rb')
        file = PdfFileReader(ff)
        number_of_pages = file.getNumPages()
        ff.close()

        return number_of_pages

    def text_extractor(self):
        text = ""
        ff = storage.open(self.pdf.name, 'rb')
        file = PdfFileReader(ff)
        # get the first page
        for x in range(0, self.get_numofpages()):
            page = file.getPage(x)
            text = text + "page:" + str(x + 1) + '\n' + page.extractText()
        ff.close()

        return text

    def imgs(self):

        directory = "media/" + self.university.name + "/" + self.faculty.name + "/" + self.course.name + "/" + self.pdf.name
        imgs = []
        s3 = boto3.resource('s3',
                            aws_access_key_id=ACCESS_ID,
                            aws_secret_access_key=ACCESS_KEY)
        my_bucket = s3.Bucket(BUCKET_NAME)
        for object in my_bucket.objects.filter(Prefix=directory):
            imgs.append('https://wara8-static.s3.amazonaws.com' + '/' + object.key)

        return imgs

    def size_cal(self):
        return str(self.pdf.size / 1024 / 1024)[0:3]


class Comment(models.Model):
    file = models.ForeignKey(File,
                             on_delete=models.CASCADE,
                             related_name='comments')

    body = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return 'Comment by {} on {}'.format(self.user, self.file.pdf)
