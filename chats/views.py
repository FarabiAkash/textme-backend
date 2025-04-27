from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import Conversation, Message
from .serializers import (
    ConversationSerializer, MessageSerializer,
    ConversationCreateSerializer
)

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(participants=user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ConversationCreateSerializer
        return ConversationSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        conversation = self.get_object()
        messages = conversation.messages.all()
        
        # Mark messages as read
        unread_messages = messages.filter(is_read=False).exclude(sender=request.user)
        unread_messages.update(is_read=True)
        
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        conversation = self.get_object()
        
        # Check if user is a participant
        if request.user not in conversation.participants.all():
            return Response(
                {"detail": "You are not part of this conversation."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Create the message
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=request.data.get('content', '')
        )
        
        # Update conversation timestamp
        conversation.save()  # This will update the updated_at field
        
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def with_user(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {"detail": "user_id query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create conversation with user
        user = request.user
        try:
            conversation = Conversation.objects.filter(
                participants=user
            ).filter(
                participants__id=user_id
            ).first()
            
            if not conversation:
                # Create new conversation
                conversation = Conversation.objects.create()
                conversation.participants.add(user.id, user_id)
            
            serializer = ConversationSerializer(conversation, context={"request": request})
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(
            conversation__participants=user
        )
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        message = self.get_object()
        
        # Check if user is a participant
        if request.user not in message.conversation.participants.all():
            return Response(
                {"detail": "You are not part of this conversation."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        message.is_read = True
        message.save()
        
        serializer = MessageSerializer(message)
        return Response(serializer.data)