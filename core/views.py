from itertools import chain
import random
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, auth
from .models import Follower, Like, Profile, Post

# Create your views here.
@login_required(login_url='signin')
def index(request):
  user_profile = Profile.objects.get(user=request.user)

  feed = []
  feed.append(Post.objects.filter(user= request.user))

  my_followings = Follower.objects.filter(follower= request.user.username)
  user_following_list = []

  for users in my_followings:
    user_following = User.objects.get(username= users.user)
    user_following_list.append(user_following)
    feed.append(Post.objects.filter(user= user_following))
  
  users_list = [x for x in User.objects.all() if x not in user_following_list and x not in [request.user]]
  profile_list = [x for x in Profile.objects.all() if x.user in users_list] 
  random.shuffle(profile_list)

  feed_list = list(chain(*feed))
  print(feed_list.sort(key=lambda x: x.created_at))
  return render(request, 'index.html', {
    "user_profile": user_profile,
    "posts": feed_list,
    "suggestions_username_profile_list": profile_list[:4]
  })

def signup(request):

  if request.method == "POST":
    is_valid_signup = True
    username = request.POST['username']
    email = request.POST['email']
    password = request.POST['password']
    password_confirmation = request.POST['password2']

    if password_confirmation != password:
      messages.info(request, "Passwords not matching!")
      is_valid_signup = False
    
    if User.objects.filter(email=email).exists():
      messages.info(request, 'Email has been taken!')
      is_valid_signup = False

    if User.objects.filter(username=username).exists():
      messages.info(request, 'Username has been taken!')
      is_valid_signup = False
    
    if not is_valid_signup:
      return redirect('signup')
    
    user = User.objects.create_user(
      username = username, 
      email = email, 
      password = password
    )
    user.save()

    user_login = auth.authenticate(username=username, password=password)
    auth.login(request, user_login)

    new_profile = Profile.objects.create(
      user = user,
      id_user = user.id
    )
    new_profile.save()

    return redirect('settings')
  
  return render(request, 'signup.html')

def signin(request):

  if request.method == "POST":
    name = request.POST['name']
    passwrd = request.POST['pass']

    user = auth.authenticate(username=name, password=passwrd)

    if user is not None:
      auth.login(request, user)
      return redirect('/')
    
    messages.info(request, 'Invalid Login!')
    return redirect('signin')
  
  return render(request, 'signin.html')

@login_required(login_url='signin')
def logout(request):
  auth.logout(request)
  return redirect('signin')

@login_required(login_url='signin')
def settings(request):
  user_profile = Profile.objects.get(user=request.user)
  if request.method == "POST":
    bio = request.POST['bio']
    location = request.POST['location']
    image = request.FILES.get('image')

    user_profile.bio = bio
    user_profile.location = location

    if image:
      user_profile.profile_img = image

    user_profile.save()

  return render(request, 'setting.html', {
    "user_profile": user_profile
  })

@login_required(login_url='signin')
def upload(request):
  if request.method == "POST":
    image = request.FILES.get('image_upload')
    caption = request.POST['caption']
    
    new_post = Post.objects.create(
      user= request.user,
      image= image,
      caption= caption
    )
    new_post.save()

  return redirect('/')

@login_required(login_url='signin')
def like_post(request, post_id):
  post = Post.objects.get(id=post_id)
  like_exists = Like.objects.filter(post=post, user=request.user).first()

  if like_exists:
    like_exists.delete()
    post.number_of_likes = post.number_of_likes - 1
    post.save()
    return redirect('/')

  new_like = Like.objects.create(user=request.user, post=post)
  new_like.save()
  post.number_of_likes = post.number_of_likes + 1
  post.save()
  return redirect('/')

@login_required(login_url='signin')
def profile(request, username):

  if not User.objects.filter(username= username).exists():
    return redirect('/')
  
  user_object = User.objects.get(username= username)
  user_profile = Profile.objects.get(user= user_object)
  user_posts = Post.objects.filter(user= user_object)
  user_post_length = len(user_posts)

  return render(request, 'profile.html', {
    "username": username,
    "user_object": user_object,
    "user_profile": user_profile,
    "user_posts": user_posts,
    "user_post_length": user_post_length,
    "user_followers": Follower.objects.filter(user=username).count,
    "user_following": Follower.objects.filter(follower=username).count,
    "button_text": "Unfollow" if Follower.objects.filter(user=username, follower=request.user.username).exists() else "Follow"
  })

@login_required(login_url='signin')
def follow(request):
  if request.method == "POST":
    user = request.POST['user']
    follow_exists = Follower.objects.filter(user=user, follower=request.user.username).first()

    if follow_exists:
      follow_exists.delete()
    else:
      new_follower = Follower.objects.create(user=user, follower= request.user.username)
      new_follower.save()
    
    return redirect('/profile/'+user)

@login_required(login_url='signin')
def search(request):
  user_profile = Profile.objects.get(user= request.user)
  user_search = request.GET['username']

  if user_search:
    username_profile_list = []
    search_result = User.objects.filter(username__icontains= user_search)

    for users in search_result:
      profile_result = Profile.objects.filter(user= users).first()
      username_profile_list.append(profile_result)

  else:
    username_profile_list = Profile.objects.all

  return render(request, 'search.html', {
    "user_profile": user_profile,
    "username_profile_list": username_profile_list,
    "username": user_search
  })