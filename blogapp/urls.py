from django.urls import path
from .views import ( HomeView, PostCreateView , PostDetailView , LikeToggleView , FilterPostsView ,ContactView
                     , RegisterView ,LoginView , ProfileUpdateView , 
                     ProfileView , CommentFormView ,CustomLogoutView ,  AboutView)
urlpatterns = [
    path('', HomeView.as_view(), name='home'), 
    path('post/<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
    path('post/<slug:slug>/like/', LikeToggleView.as_view(), name='like_toggle'),
    path('filter/', FilterPostsView.as_view(), name='filter_posts'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile_update'),
    path('post/<slug:slug>/comment/', CommentFormView.as_view(), name='post_comment'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('contact/' , ContactView.as_view()  , name='contact' ),
    path('about/',AboutView.as_view() , name="about"),
    path('create/', PostCreateView.as_view(), name='create_post'),

]
