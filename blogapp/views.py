from django.views.generic import TemplateView , DetailView , FormView ,ListView ,UpdateView , CreateView
from django.shortcuts import get_object_or_404, redirect
from .models import Post, Category , Comment , Like
from .forms import CommentForm ,CustomUserCreationForm, CustomAuthenticationForm, PostForm, ProfileUpdateForm
from django.shortcuts import render , redirect
from django.db.models import Q
from .models import Post, Category , Profile
from django.contrib.auth.models import User
from datetime import datetime
from django.contrib.auth import login, authenticate , logout
from django.contrib.auth.decorators import login_required
from django.views import View
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.http import require_POST;
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

class HomeView(TemplateView):

    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['latest_posts'] = Post.objects.order_by('-created_at')[:6]  # Display the 6 most recent posts
        return context

class ContactView(View):
    template_name = 'contact.html'

    def get(self,request):
        return render(request , template_name=self.template_name)

class AboutView(View):
    template_name = 'about.html'

    def get(self,request):
        return render(request , template_name=self.template_name)
    

class PostCreateView(LoginRequiredMixin , CreateView):
    model = Post
    form_class = PostForm
    template_name = 'create_post.html'
    success_url = reverse_lazy('filter_posts')   

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
     
      
class PostDetailView(DetailView, FormView):
    model = Post
    template_name = 'post_detail.html'
    context_object_name = 'post'
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.filter(parent__isnull=True)   
        context['related_posts'] = Post.objects.all()[:6]
        context['categories'] = Category.objects.all()
        context['form'] = self.get_form()
        return context

    @require_POST
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'errors': 'Please log in to comment'}, status=403)
            
        self.object = self.get_object()
        form = self.get_form()
        
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = self.object
            
            parent_id = request.POST.get('parent_id')
            if parent_id:
                try:
                    comment.parent = Comment.objects.get(id=parent_id)
                except Comment.DoesNotExist:
                    return JsonResponse({'success': False, 'errors': 'Parent comment not found'}, status=404)
            
            comment.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest': 
                comment_data = {
                    'id': comment.id,
                    'content': comment.content,
                    'author': comment.author.username,
                    'created_at': comment.created_at.strftime('%B %d, %Y'),
                    'likes_count': 0,
                }
                return JsonResponse({'success': True, 'comment': comment_data})

            messages.success(request, 'Comment added successfully!')
            return redirect('post_detail', slug=self.object.slug)
            
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
            
        messages.error(request, 'Please correct the errors below.')
        return self.form_invalid(form)
class LikeToggleView(LoginRequiredMixin,View):
    def post(self, request, *args, **kwargs):
        # Fetch the post using the slug from URL
        post = get_object_or_404(Post, slug=kwargs.get('slug'))
        comment_id = request.POST.get('comment_id')
        
        if comment_id: 
            comment = get_object_or_404(Comment, id=comment_id)
            like, created = Like.objects.get_or_create(user=request.user, comment=comment)
        else: 
            like, created = Like.objects.get_or_create(user=request.user, post=post)
         
        if not created:
            like.delete()
 
        if comment_id:
            like_count = comment.likes.count()  
        else:
            like_count = post.likes.count()  

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'liked': created,
                'like_count': like_count
            })
        return redirect('post_detail', slug=post.slug)
    

class CommentFormView(LoginRequiredMixin, FormView):
    form_class = CommentForm

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'errors': 'Please log in to comment'}, status=403)

        post = get_object_or_404(Post, slug=kwargs.get('slug'))
        form = self.get_form()
        
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            
            parent_id = request.POST.get('parent_id')
            if parent_id:
                try:
                    comment.parent = Comment.objects.get(id=parent_id)
                except Comment.DoesNotExist:
                    return JsonResponse({'success': False, 'errors': 'Parent comment not found'}, status=404)
            
            comment.save()

            response_data = {
                'id': comment.id,
                'author': comment.author.username,
                'content': comment.content,
                'created_at': comment.created_at.strftime('%B %d, %Y'),
                'likes_count': 0,
                'is_liked': False
            }
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'comment': response_data})

            messages.success(request, 'Comment added successfully!')
            return redirect('post_detail', slug=post.slug)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
            
        messages.error(request, 'Please correct the errors below.')
        return self.form_invalid(form)
    
class FilterPostsView(ListView):
    model = Post
    template_name = 'filter_posts.html'
    context_object_name = 'posts'
    
    def get_queryset(self): 
        category_id = self.request.GET.get('category')
        author_id = self.request.GET.get('author')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        query = self.request.GET.get('query', '')
 
        filters = Q()
        if category_id:
            filters &= Q(category_id=category_id)
        if author_id:
            filters &= Q(author_id=author_id)
        if start_date:
            filters &= Q(created_at__gte=datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            filters &= Q(created_at__lte=datetime.strptime(end_date, '%Y-%m-%d'))
        if query:
            filters &= Q(title__icontains=query) | Q(content__icontains=query)

        return Post.objects.filter(filters).distinct()
    
    def get_context_data(self, **kwargs):
        """
        Override the get_context_data method to include categories and authors in the context.
        """
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['authors'] = User.objects.all()
        return context
    
    
class RegisterView(View):
    template_name = 'auth.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, self.template_name)

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already taken.")
            return render(request, self.template_name)

        user = User.objects.create_user(
            username=email,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password1
        )
        Profile.objects.create(user=user)
        login(request, user)
        return redirect('home')


class LoginView(View):
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to a page after successful login
        else:
            messages.error(request, "Invalid email or password.")
            return redirect('home')

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'profile_update.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return Profile.objects.get(user=self.request.user)

    def form_valid(self, form): 
        response = super().form_valid(form)
        user = self.request.user
        if 'first_name' in form.changed_data:
            user.first_name = form.cleaned_data['first_name']
        if 'last_name' in form.changed_data:
            user.last_name = form.cleaned_data['last_name']
        if 'image' in form.changed_data:
            user.profile.image = form.cleaned_data['image']
        user.save()
        return response
class ProfileView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'profile.html'
    context_object_name = 'profile'

    def get_object(self): 
        return Profile.objects.get(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        context['blogs'] = Post.objects.filter(author=self.request.user)
        return context
    
class CustomLogoutView(View):
    def get(self, request, *args, **kwargs): 
        logout(request) 
        return HttpResponseRedirect(reverse('home'))
    
    