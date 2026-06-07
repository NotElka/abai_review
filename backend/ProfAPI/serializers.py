from rest_framework import serializers
from .models import Professor, User, Review, Subject, WishlistItem

class WishlistSerializer(serializers.ModelSerializer):
    professor_name = serializers.CharField(source='professor.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    professor_rating = serializers.SerializerMethodField()

    class Meta:
        model = WishlistItem
        fields = ['id', 'professor', 'subject', 'professor_name', 'subject_name', 'professor_rating', 'added_at']
        read_only_fields = ['id', 'added_at']

    def get_professor_rating(self, obj):
        reviews = obj.professor.reviews.all()
        if reviews.exists():
            avg = sum(r.rating for r in reviews) / reviews.count()
            return round(avg, 1)
        return None


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email',
            'first_name', 'last_name', 'full_name',
            'role', 'role_display',
            'course',
            'date_joined',
        ]

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class ProfessorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professor
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['rev_id', 'user', 'professor', 'subject', 'rating', 'difficulty', 'text', 'created_at', 'is_anounimous']

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['subj_id', 'name', 'description']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data['username']
        password = data['password']
        user = User.objects.filter(username=username).first()
        if not user:
            raise serializers.ValidationError("User not found")
        if not user.check_password(password):
            raise serializers.ValidationError("Wrong password")
        
        data['user'] = user
        return data

class CreateReviewSerializer(serializers.Serializer):
    prof_id = serializers.IntegerField(write_only=True)
    subj_id = serializers.IntegerField(write_only=True)
    rating = serializers.FloatField()
    difficulty = serializers.FloatField(required=False, default=3.0)
    text = serializers.CharField()
    is_anounimous = serializers.BooleanField(required=False, default=False)

    def validate(self, data):
        user = self.context['request'].user

        if not user or not user.is_authenticated:
            raise serializers.ValidationError("You must be logged in")

        prof = Professor.objects.filter(prof_id=data['prof_id']).first()
        subj = Subject.objects.filter(subj_id=data['subj_id']).first()

        if not prof or not subj:
            raise serializers.ValidationError("Invalid professor or subject")

        if Review.objects.filter(user=user, professor=prof, subject=subj).exists():
            raise serializers.ValidationError("You already left a review")

        return data

    def create(self, validated_data):
        prof = Professor.objects.get(prof_id=validated_data['prof_id'])
        subj = Subject.objects.get(subj_id=validated_data['subj_id'])
        
        review = Review.objects.create(
            user=validated_data['user'],
            professor=prof,
            subject=subj,
            rating=validated_data['rating'],
            difficulty=validated_data.get('difficulty', 3.0),
            text=validated_data['text'],
            is_anounimous=validated_data.get('is_anounimous', False)
        )
        return review

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField(required=False, allow_blank=True)
    course = serializers.FloatField(required=False, default=1.0, min_value=1.0, max_value=4.0)

    def validate(self, data):
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("Username already exists")
        return data

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data.get('email', ''),
            course=validated_data.get('course', 1.0),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user