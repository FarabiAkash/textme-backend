from django.contrib import admin
from .models import Conversation, Message

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('sender', 'content', 'timestamp', 'is_read')
    can_delete = False

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'updated_at', 'get_participants')
    inlines = [MessageInline]
    
    def get_participants(self, obj):
        return ", ".join([user.email for user in obj.participants.all()])
    get_participants.short_description = 'Participants'

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender', 'content', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('content', 'sender__email')
    readonly_fields = ('timestamp',)