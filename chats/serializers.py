from rest_framework import serializers
from .models import Conversation, Message
from accounts.serializers import UserSerializer

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ('id', 'sender', 'content', 'timestamp', 'is_read')
        read_only_fields = ('id', 'timestamp', 'is_read')


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ('id', 'participants', 'created_at', 'updated_at', 'last_message', 'unread_count')
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-timestamp').first()
        if last_message:
            return MessageSerializer(last_message).data
        return None
    
    def get_unread_count(self, obj):
        user = self.context.get('request').user
        return obj.messages.filter(is_read=False).exclude(sender=user).count()


class ConversationCreateSerializer(serializers.ModelSerializer):
    participants = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True
    )
    
    class Meta:
        model = Conversation
        fields = ('id', 'participants')
        read_only_fields = ('id',)
    
    def create(self, validated_data):
        participants_ids = validated_data.pop('participants')
        
        # Add the current user to the participants
        user = self.context['request'].user
        if user.id not in participants_ids:
            participants_ids.append(user.id)
        
        conversation = Conversation.objects.create(**validated_data)
        conversation.participants.set(participants_ids)
        return conversation