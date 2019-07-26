import django_filters
from django.contrib.auth.models import User

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from blog.models import Post, LikeDislike
from blog.serializers import UserSerializer, PostSerializer, LikeDislikeSerializer


class BaseModelViewSet(viewsets.ModelViewSet):
    permission_classes_by_action = {"default": [IsAdminUser]}

    def get_permissions(self):
        return [permission() for permission in
                self.permission_classes_by_action.get(self.action, self.permission_classes_by_action['default'])]


class UserViewSet(BaseModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    permission_classes_by_action = {'create': [AllowAny],
                                    'default': [IsAdminUser]}

    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class PostViewSet(BaseModelViewSet):
    """
    API endpoint that allows posts to be viewed or edited.
    """

    permission_classes_by_action = {'create': [IsAuthenticated],
                                    'list': [AllowAny],
                                    'default': [IsAdminUser]}

    filter_fields = ['author', 'title']

    queryset = Post.objects.all().order_by('-created_on')
    serializer_class = PostSerializer


class LikeDislikeViewSet(BaseModelViewSet):
    """
    API endpoint that allows likes and dislikes to be viewed or edited.
    """

    permission_classes_by_action = {'create': [IsAuthenticated],
                                    'list': [AllowAny],
                                    'update': [],
                                    'default': [IsAdminUser]}

    filter_fields = ['user', 'post', 'vote']

    queryset = LikeDislike.objects.all().order_by('user')
    serializer_class = LikeDislikeSerializer

    def perform_create(self, serializer):
        self.request.user.votes.filter(post=serializer.validated_data["post"]).delete()
        super().perform_create(serializer)


@api_view(['POST'])
def user_signup(request):
    serialized = UserSerializer(data=request.data)
    if serialized.is_valid() and serialized.save():
        return Response(serialized.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
