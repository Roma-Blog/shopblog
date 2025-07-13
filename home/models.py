from django.db import models
from django.shortcuts import render
from django.apps import apps

from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import TabbedInterface, ObjectList, FieldPanel
from .forms import ContactForm

from wagtail.contrib.sitemaps import Sitemap




class BasePage(Page):
    h1 = models.CharField("H1 заголовок", max_length=255, blank=True, null=True)
    keywords = models.CharField("Ключевые слова", max_length=512, blank=True, null=True)

    content_panels = Page.content_panels

    seo_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        FieldPanel('keywords'),
        FieldPanel('h1'),
        FieldPanel('show_in_menus'),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Содержимое'),
        ObjectList(seo_panels, heading='SEO'),
        ObjectList(Page.settings_panels, heading='Настройки'),
    ])

    class Meta:
        abstract = True

class HomePage(BasePage):

    hero_text = RichTextField("Текст на главной", blank=True)

    subpage_types = ['blog.BlogCatalog', 'blog.AuthorContainer', 'About', 'Contacts', 'Privacy']

    content_panels = BasePage.content_panels + [
        FieldPanel('hero_text'),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Содержимое'),
        ObjectList(BasePage.seo_panels, heading='SEO'),
        ObjectList(Page.settings_panels, heading='Настройки'),
    ])

    def get_context(self, request, *args, **kwargs):

        context = super().get_context(request, *args, **kwargs)

        model_posts = apps.get_model('blog', 'BlogPost')
        popular_posts = model_posts.objects.order_by('-views')[:6]

        context['posts'] = popular_posts

        return context


class About(BasePage):

    about_text = RichTextField("Текст о компании", blank=True)

    parent_page_types = ['home.HomePage']

    content_panels = BasePage.content_panels + [
        FieldPanel('about_text'),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Содержимое'),
        ObjectList(BasePage.seo_panels, heading='SEO'),
        ObjectList(Page.settings_panels, heading='Настройки'),
    ])

class Contacts(BasePage):

    parent_page_types = ['home.HomePage']

    def serve(self, request):
        if request.method == 'POST':
            form = ContactForm(request.POST)
            if form.is_valid():
                # Отправка в Telegram
                self.send_to_telegram(form.cleaned_data)
                return 
        else:
            form = ContactForm()
        
        return render(request, 'home/contacts.html', {
            'page': self,
            'form': form,
        })

class Privacy(BasePage):

    privacy_text = RichTextField("Текст политики", blank=True)

    parent_page_types = ['HomePage']

    content_panels = BasePage.content_panels + [
        FieldPanel('privacy_text'),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Содержимое'),
        ObjectList(BasePage.seo_panels, heading='SEO'),
        ObjectList(Page.settings_panels, heading='Настройки'),
    ])