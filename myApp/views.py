from django.shortcuts import render, redirect
import base64
import pyrebase
import time

config={
    "apiKey": "",
  "authDomain": "",
  "databaseURL": "",
  "projectId": "",
  "storageBucket": "",
  "messagingSenderId": "",
  "appId": ""
}

firebase = pyrebase.initialize_app(config)
authe = firebase.auth()
database = firebase.database()

def home(request):
    template = "home.html"
    return render(request,template)

def register(request):
    template = "register.html"
    context = {}
    if request.method == 'POST':
        if request.POST['password'] == request.POST['password_confirm']:
            try:
                user = authe.create_user_with_email_and_password(request.POST['username'], request.POST['password'])
                return redirect('/login')
            except:
                context['message'] = "Something went wrong."
        else:
            context['message'] = "The passwords do not match."
    return render(request,template,context)

def login(request):
    template = "login.html"
    context = {}
    if request.method == 'POST':
        try:
            user = authe.sign_in_with_email_and_password(request.POST['username'],request.POST['password'])
            request.session['uid'] = str(user['idToken'])
            request.session['user'] = request.POST['username']
            return redirect('/')
        except:
            context['message'] = "Something went wrong"
    return render(request,template,context)

def logout(request):
    try:
        del request.session['uid']
        del request.session['user']
    except:
        pass
    return redirect("/")

def insert_creds(request):
    try:
        if not request.session['uid']:
            return redirect('/')
    except:
        return redirect('/')
    template = "insert.html"
    context = {}
    if request.method == 'POST':
        creds_ref = database.child("creds")
        new_creds = creds_ref.push({
            "owner" : request.session['user'],
            "website" : request.POST['website'],
            "username_or_email" : request.POST['username'],
            "password" : encode_string(request.POST['password']),
            "timestamp" : time.time()
        })
        return redirect('/show-creds')
    return render(request,template,context)

def encode_string(temp):
    temp = temp.encode('ascii')
    temp = base64.b64encode(temp)
    return temp.decode('ascii')

def decode_string(temp):
    temp = temp.encode('ascii')
    temp = base64.b64decode(temp)
    return temp.decode('ascii')

def show_creds(request):
    try:
        if not request.session['uid']:
            return redirect('/')
    except:
        return redirect('/')
    template = "show.html"
    context = {}
    templist = []
    creds_ref = database.child("creds").order_by_child("owner").equal_to(request.session['user']).get()
    for i in creds_ref.each():
        temp = {'iden':i.key()}
        for key, value in i.val().items():
            if key == "website":
                temp['site'] = value
            if key == "username_or_email":
                temp['user'] = value
            if key == "password":
                temp['pass'] = decode_string(value)
        templist.append(temp)
    context['objs'] = templist
    return render(request,template,context)

def delete_creds(request,iden):
    try:
        if not request.session['uid']:
            return redirect('/')
    except:
        return redirect('/')
    creds_ref = database.child("creds").child(iden).remove()
    return redirect("/show-creds")
    

def edit_creds(request,iden):
    try:
        if not request.session['uid']:
            return redirect('/')
    except:
        return redirect('/')
    if request.method == 'POST':
        cred_ref_edit = database.child("creds").child(iden).set({
            "owner" : request.session['user'],
            "website" : request.POST['website'],
            "username_or_email" : request.POST['username'],
            "password" : encode_string(request.POST['password']),
            "timestamp" : time.time()
        })
        return redirect("/show-creds")
    template = "edit.html"
    context = {}
    temp = {}
    creds_ref = database.child("creds").child(iden).get()
    for key, value in creds_ref.val().items():
        if key == "website":
            temp['site'] = value
        if key == "username_or_email":
            temp['user'] = value
        if key == "password":
            temp['pass'] = decode_string(value)
    context['obj'] = temp
    return render(request,template,context)