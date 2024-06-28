from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import serializers
from django.contrib.auth import get_user_model

from users.errors import BIRTH_YEAR_ERROR_MSG

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True, min_length=1)
    last_name = serializers.CharField(required=True, min_length=1)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'middle_name', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User(
            email=validated_data.get('email', ''),
            username=validated_data['username'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            middle_name=validated_data.get('middle_name', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'middle_name', 'email', 'avatar', 'birth_year']

    def validate_birth_year(self, value):
        if not (settings.BIRTH_YEAR_MIN < value < settings.BIRTH_YEAR_MAX):
            raise serializers.ValidationError(BIRTH_YEAR_ERROR_MSG)
        return value

    def validate(self, data):
        birth_year = data.get('birth_year')
        if birth_year is not None:
            if not (settings.BIRTH_YEAR_MIN < birth_year < settings.BIRTH_YEAR_MAX):
                raise serializers.ValidationError({"birth_year": BIRTH_YEAR_ERROR_MSG})
        return data


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise serializers.ValidationError('Invalid login credentials')
        else:
            raise serializers.ValidationError('Both "username" and "password" are required')

        data['user'] = user
        return data


class TokenResponseSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()


class ValidationErrorSerializer(serializers.Serializer):
    detail = serializers.CharField()
    code = serializers.CharField(required=False)

    def to_representation(self, instance):
        if isinstance(instance, dict):
            return instance
        return super().to_representation(instance)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] == data['old_password']:
            raise serializers.ValidationError("New and old passwords should not be the same")
        return data
