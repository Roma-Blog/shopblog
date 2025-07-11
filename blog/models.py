from django.db import models
from wagtail.models import Page
from home.models import BasePage
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, ObjectList, TabbedInterface
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from modelcluster.fields import ParentalManyToManyField


class PaginationMixin:
    def paginate_queryset(self, request, queryset, per_page=None):
        per_page = per_page or self.posts_per_page
        paginator = Paginator(queryset, per_page)
        page_number = request.GET.get('page')
        
        try:
            page = paginator.page(page_number)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)
        
        return page

    def get_pagination_context(self, request, context):
        posts = BlogPost.objects.live().descendant_of(self).order_by('-first_published_at')
        context['posts'] = self.paginate_queryset(request, posts)

        return context
    
class CategoriesMixin:
    def get_categories(self):
        """Возвращает все дочерние категории"""
        return self.get_children().live().type(BlogCategoryPage).specific()
    
class PostMixin:
    """Миксин для работы с постами"""
    def get_posts(self, order='-first_published_at', limit=3, exclude_current=None, **filters):
        """
        Возвращает посты с возможностью фильтрации
        :param order: сортировка
        :param limit: лимит постов
        :param exclude_current: исключить текущий пост
        :param filters: дополнительные фильтры (например, authors__id=author_id)
        """
        queryset = BlogPost.objects.live().order_by(order)
        
        if exclude_current:
            queryset = queryset.exclude(id=exclude_current.id)
            
        if filters:
            queryset = queryset.filter(**filters)
            
        return queryset[:limit]
    

class BlogCatalog(BasePage, PaginationMixin, CategoriesMixin):

    seo_text = RichTextField("SEO текст", blank=True)
    posts_per_page = models.PositiveIntegerField(
        default=6,
        verbose_name="Количество постов на странице"
    )

    parent_page_types = ['home.HomePage']
    subpage_types = ['blog.BlogCategoryPage']

    content_panels = BasePage.content_panels + [
        FieldPanel('seo_text'),
        FieldPanel('posts_per_page'),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Содержимое'),
        ObjectList(BasePage.seo_panels, heading='SEO'),
        ObjectList(Page.settings_panels, heading='Настройки'),
    ])

    def get_context(self, request, *args, **kwargs):

        context = super().get_context(request, *args, **kwargs)
        context = self.get_pagination_context(request, context)
        context['authors'] = AuthorPage.objects.all()

        return context


class BlogCategoryPage(BasePage, PaginationMixin, CategoriesMixin):

    posts_per_page = models.PositiveIntegerField(
        default=6,
        verbose_name="Количество постов на странице"
    )

    subpage_types = ['blog.BlogPost', 'blog.BlogCategoryPage']

    def get_context(self, request, *args, **kwargs):

        context = super().get_context(request, *args, **kwargs)
        context = self.get_pagination_context(request, context)

        return context


class BlogPost(BasePage, PostMixin):
    intro = models.CharField(max_length=255, blank=True)
    authors = ParentalManyToManyField('blog.AuthorPage', blank=True, verbose_name="Авторы")
    body = RichTextField(blank=True)
    main_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    views = models.PositiveIntegerField(default=0, editable=False)

    parent_page_types = ['blog.BlogCategoryPage']

    content_panels = BasePage.content_panels + [
        FieldPanel('main_image'),
        FieldPanel('authors'),
        FieldPanel('intro'),
        FieldPanel('body'),
    ]

    seo_panels = BasePage.seo_panels


    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Содержимое'),
        ObjectList(seo_panels, heading='SEO'),
        ObjectList(Page.settings_panels, heading='Настройки'),
    ])

    def get_previous_post(self):
        """Возвращает предыдущий пост в той же категории"""
        return BlogPost.objects.live().filter(
            first_published_at__lt=self.first_published_at,
            path__startswith=self.get_parent().path
        ).order_by('-first_published_at').first()

    def get_next_post(self):
        """Возвращает следующий пост в той же категории"""
        return BlogPost.objects.live().filter(
            first_published_at__gt=self.first_published_at,
            path__startswith=self.get_parent().path
        ).order_by('first_published_at').first()
    
    def get_authors(self):
        """Возвращает список авторов с их URL"""
        authors = []
        for author in self.authors.all():
            authors.append({
                'name': author.title,
                'url': author.url, 
            })
        return authors
    
    def serve(self, request):
        BlogPost.objects.filter(id=self.id).update(views=models.F('views') + 1)
        self.views = models.F('views') + 1
        self.refresh_from_db()

        response = super().serve(request)

        response.context_data['previous_post'] = self.get_previous_post()
        response.context_data['next_post'] = self.get_next_post()

        response.context_data['popular_posts'] = self.get_posts(order='-views' ,limit=3, exclude_current=self)
        response.context_data['recent_posts'] = self.get_posts(limit=5, exclude_current=self)

        response.context_data['authors'] = self.get_authors()
        
        return response
    
class AuthorContainer(Page):
    parent_page_types = ['home.HomePage']
    subpage_types = ['AuthorPage']
    
    def serve(self, request):
        from django.http import HttpResponseNotFound
        return HttpResponseNotFound()
    
class AuthorPage(BasePage, PostMixin):
    education = models.CharField(max_length=128, blank=True)
    bio = RichTextField(blank=True)
    photo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = BasePage.content_panels + [
        FieldPanel('education'),
        FieldPanel('photo'),
        FieldPanel('bio'),
    ]

    seo_panels = BasePage.seo_panels


    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Содержимое'),
        ObjectList(seo_panels, heading='SEO'),
        ObjectList(Page.settings_panels, heading='Настройки'),
    ])
    
    def serve(self, request):
        response = super().serve(request)
        response.context_data['latest_posts'] = self.get_posts(limit=6, authors__id=self.id )
        return response