"""
Forms for customer registration and authentication.
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from inventory.models import Customer
from .models import CustomerProfile


class CustomerRegistrationForm(UserCreationForm):
    """
    Form for new customer registration.
    Creates both User (for authentication) and Customer (for orders) records.
    """
    # Customer fields from inventory.Customer
    cedula = forms.CharField(
        max_length=100,
        required=True,
        label="ID Number (Cédula)",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your ID number'
        })
    )
    nombre = forms.CharField(
        max_length=200,
        required=True,
        label="Full Name",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name'
        })
    )
    correo = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )
    
    # Extended fields from CustomerProfile
    phone = forms.CharField(
        max_length=20,
        required=False,
        label="Phone Number",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number (optional)'
        })
    )
    address = forms.CharField(
        required=False,
        label="Address",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter your address (optional)'
        })
    )
    
    # User fields
    username = forms.CharField(
        max_length=150,
        required=True,
        label="Username",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
    
    def clean_cedula(self):
        """Validate that cedula is unique"""
        cedula = self.cleaned_data.get('cedula')
        if Customer.objects.filter(cedula=cedula).exists():
            raise forms.ValidationError("A customer with this ID number already exists.")
        return cedula
    
    def clean_correo(self):
        """Validate that email is unique"""
        correo = self.cleaned_data.get('correo')
        if Customer.objects.filter(correo=correo).exists():
            raise forms.ValidationError("A customer with this email already exists.")
        return correo
    
    def clean_username(self):
        """Validate that username is unique"""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username
    
    def save(self, commit=True):
        """
        Save the form and create related objects.
        Creates: User -> Customer -> CustomerProfile
        """
        # Create User
        user = super().save(commit=False)
        user.email = self.cleaned_data['correo']
        
        if commit:
            user.save()
            
            # Create Customer (from inventory app)
            customer = Customer.objects.create(
                cedula=self.cleaned_data['cedula'],
                nombre=self.cleaned_data['nombre'],
                correo=self.cleaned_data['correo']
            )
            
            # Create CustomerProfile (link User and Customer)
            CustomerProfile.objects.create(
                user=user,
                customer=customer,
                phone=self.cleaned_data.get('phone', ''),
                address=self.cleaned_data.get('address', '')
            )
        
        return user


class CustomerLoginForm(forms.Form):
    """
    Simple login form for registered customers.
    """
    username = forms.CharField(
        max_length=150,
        required=True,
        label="Username",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username'
        })
    )
    password = forms.CharField(
        required=True,
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )
