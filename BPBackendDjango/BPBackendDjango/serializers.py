from rest_framework import serializers
from .models import *

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'username', 'password', 'email_address', 'trainer'
        )


class CreateTrainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trainer
        fields = (
            'first_name', 'last_name', 'username', 'password', 'email_address'
        )


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'password'
        )


class CreateExercise(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = (
            'description', 'path', 'title'
        )


class CreateExerciseWithoutVideo(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = (
            'description', 'title'
        )

