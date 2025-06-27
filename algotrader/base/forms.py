from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User




class Register_form(UserCreationForm):
    starting_capital = forms.DecimalField(max_digits=12, decimal_places=2,label='Starting Capital', min_value=0,max_value=10_000_000,required=True,help_text='Please enter a number up to 10,000,000')
    class Meta:
        model = User
        fields = ('username','email','password1','password2','starting_capital')
    def save(self,commit=True):
        user = super().save(commit=False)
        starting_cash = self.cleaned_data['starting_capital']

        if commit:
            user.save()
            from .models import Portfolio
            Portfolio.objects.update_or_create(user=user, defaults={'cash':starting_cash})

        return user
