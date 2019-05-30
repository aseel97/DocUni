from rest_framework import serializers, status
from .models import File, University,Ip


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ('id', 'name')


class IpSerializer(serializers.ModelSerializer):
    class Meta:
        model=Ip
        fields="__all__"


class FileSerializer(serializers.ModelSerializer):
    """
    A student serializer to return the student details
    """
    university = UniversitySerializer(required=True)

    class Meta:
        model = File
        fields = ('university', 'id', 'imgs')

    def create(self, validated_data):
        """
        Overriding the default create method of the Model serializer.
        :param validated_data: data containing all the details of student
        :return: returns a successfully created student record
        """
        uni_data = validated_data.pop('user')
        university = UniversitySerializer.create(UniversitySerializer(), validated_data=uni_data)
        file, created = File.objects.update_or_create(university=university,
                                                      id=validated_data.pop('id'))
        return file
