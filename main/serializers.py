from django.db.models import Avg
from rest_framework import serializers
from .models import Category, Post, PostImage, Comment, Rating, Favorite, Like


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S',read_only=True)

    class Meta:
        model = Post
        fields = ('id','title','category','created_at','text')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['author'] = instance.author.email
        representation['likes'] = instance.likes.filter(like=True).count()
        representation['ratings'] = instance.ratings.all().aggregate(Avg('rating')).get('rating__avg')
        representation['favorites'] = instance.favorites.filter(favorite=True).count()
        representation['images'] = PostImageSerializer(instance.images.all(),many=True,context=self.context).data
        representation['comments'] = CommentSerializer(instance.comments.all(),many=True).data
        return representation

    def create(self, validated_data):
        request = self.context.get('request')
        user_id = request.user.id
        validated_data['author_id'] = user_id
        post = Post.objects.create(**validated_data)
        return post



class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = '__all__'

    def _get_image_url(self,obj):
        if obj.image:
            url = obj.image.url
            request = self.context.get('request')
            if request is not None:
                url = request.build_absolute_uri(url)
        else:
            url = ''
        return url

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['image'] = self._get_image_url(instance)
        return representation


class CommentSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S',read_only=True)

    class Meta:
        model = Comment
        fields = ['id','post','comment','created_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['author'] = instance.user.email
        return representation

    def create(self, validated_data):
        request = self.context.get('request')
        user_id = request.user.id
        validated_data['user_id'] = user_id
        comment = Comment.objects.create(**validated_data)
        return comment


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ('id', 'post', 'author', 'like')

    def get_fields(self):
        action = self.context.get('action')
        fields = super().get_fields()
        if action == 'create':
            fields.pop('author')
            fields.pop('like')
        return fields

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['author'] = instance.author.email
        return representation

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        post = validated_data.get('post')
        like = Like.objects.get_or_create(author=user, post=post)[0]
        like.like = True if like.like is False else False
        like.save()
        return like


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ('post', 'author', 'rating')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['author'] = instance.author.email
        return representation

    def validate(self, attrs):
        rating = attrs.get('rating')
        if rating > 5:
            raise serializers.ValidationError('Значение не должно быть больше 5')
        return attrs

    def get_fields(self):
        fields = super().get_fields()
        action = self.context.get('action')
        if action == 'create':
            fields.pop('author')
        return fields

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        post = validated_data.get('post')
        rat = validated_data.get('rating')
        rating = Rating.objects.get_or_create(author=user, post=post)[0]
        rating.rating = rat
        rating.save()
        return rating


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('post', 'author', 'favorite')

    def get_fields(self):
        action = self.context.get('action')
        fields = super().get_fields()
        if action == 'create':
            fields.pop('author')
            fields.pop('favorite')
        return fields

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['author'] = instance.author.email
        return representation

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        post = validated_data.get('post')
        favorite = Favorite.objects.get_or_create(author=user, post=post)[0]
        favorite.favorite = True if favorite.favorite == False else False
        favorite.save()
        return favorite