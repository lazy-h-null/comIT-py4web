from django.shortcuts import render
from django.http import HttpResponse

nav = """
    <nav>
        <a href='/'>Home</a> |
        <a href='contact/'>Contact</a>        
        
    </nav>
"""
name = "Tim"
age = 24
gains = 234.5634224

home_body = f"""
    <ol>
        <li>Name: { name}</li>
        <li>Age: {age}</li>
        <li>Gains: {gains:.2f}</li>
    </ol>
    
"""



def home(request):
    content= """
            <h1>Welcome to my Page</h1>
            <h2>Visit around</h2>
            <p>Enjoy the content</p>
    """
    
    return HttpResponse(nav + content + home_body)

def contact(request):
    return HttpResponse(nav + "Contact Us")
