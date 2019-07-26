from django.contrib.auth.models import User
from rest_framework import serializers

from blog.models import Post, LikeDislike


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        read_only_fields = ['id']
        fields = ['username', 'email', 'password'] + read_only_fields
        extra_kwargs = {
            'username': {"required": True},
            'email': {"required": True},
            'password': {"required": True, 'write_only': True}}

    def validate(self, data):
        data = super().validate(data)

        # todo: make cheking email by https://hunter.io/api/v2/docs
        return data

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'])
        user.set_password(validated_data['password'])
        user.save()
        return user


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        read_only_fields = ['id', 'updated_on', 'created_on', 'my_vote', 'count_likes', 'count_dislikes']
        fields = ['author', 'title', 'content'] + read_only_fields

    author = serializers.PrimaryKeyRelatedField(required=False, queryset=User.objects.all(),
                                                default=serializers.CurrentUserDefault())

    # my vote
    my_vote = serializers.SerializerMethodField(read_only=True)

    def get_my_vote(self, obj):
        try:
            return obj.votes.filter(user=self.context['request'].user).get().vote
        except LikeDislike.DoesNotExist:
            return None

    # count likes
    count_likes = serializers.SerializerMethodField(read_only=True)

    def get_count_likes(self, obj):
        return obj.votes.filter(vote='+').count()

    # count dislikes
    count_dislikes = serializers.SerializerMethodField(read_only=True)

    def get_count_dislikes(self, obj):
        return obj.votes.filter(vote='-').count()


class LikeDislikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikeDislike
        read_only_fields = ['id', 'user']
        fields = read_only_fields + ['post', 'vote']

    user = serializers.PrimaryKeyRelatedField(read_only=True)
    post = serializers.PrimaryKeyRelatedField(required=True, queryset=Post.objects.all())

    def create(self, validated_data):
        return self.Meta.model.objects.create(
            user=self.context["request"].user,
            post=validated_data["post"],
            vote=validated_data["vote"]
        )
