# blog/forms.py
from django import forms
from django.core.mail import send_mail
from django.contrib.auth import get_user_model

from .models import Post, Comment, Category, Location


User = get_user_model()

BEATLES = {'Джон Леннон', 'Пол Маккартни', 'Джордж Харрисон', 'Ринго Старр'}

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'pub_date', 'image', 'location', 'category', 'is_published']
        
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'}),
        } 
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['author'] = forms.ModelChoiceField(
            queryset=User.objects.all(),
            required=False,
            widget=forms.HiddenInput()
        )
        
    def clean(self):
        cleaned_data = super().clean()
        
        title = cleaned_data.get('title', '')
        for beatle in BEATLES:
            if beatle.lower() in title.lower():
                send_mail(
                    subject='Another Beatles member',
                    message=f'{beatle} {title} пытался опубликовать запись!',
                    from_email='birthday_form@acme.not',
                    recipient_list=['admin@acme.not'],
                    fail_silently=True,
                )
        if 'author' in cleaned_data and cleaned_data['author'] is None:
            del cleaned_data['author']
        return cleaned_data
            
class CommentForm(forms.ModelForm):
    
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
        labels = {
            'text': 'Коментарий',
        }
        
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'bio']