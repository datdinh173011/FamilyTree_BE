from rest_framework import serializers
from .models.users import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with basic fields
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'avatar', 'is_staff', 'is_active', 'date_joined']
        read_only_fields = ['is_staff', 'is_active', 'date_joined']

    def create(self, validated_data):
        """Override create method to properly handle password"""
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for User model with all fields
    """
    age = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'avatar', 'phone_number', 'date_of_birth', 'gender', 'bio',
                 'address', 'city', 'state', 'country', 'postal_code',
                 'family_role', 'family_branch', 'facebook', 'twitter',
                 'instagram', 'linkedin', 'is_verified', 'is_staff', 
                 'is_active', 'date_joined', 'last_activity', 'age']
        read_only_fields = ['is_staff', 'is_active', 'date_joined', 'last_activity']
        extra_kwargs = {
            'password': {'write_only': True}
        }
