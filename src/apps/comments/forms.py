from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('object_id', 'parent', 'file', 'content', )
        widgets = {
            'object_id': forms.HiddenInput(),
            'parent': forms.HiddenInput()
        }
