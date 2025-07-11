from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import TabbedInterface, ObjectList, FieldPanel


class BasePage(Page):
    h1 = models.CharField("H1 заголовок", max_length=255, blank=True)
    keywords = models.CharField("Ключевые слова", max_length=512, blank=True)

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

class BasePageEditHandlerMixin:

    content_panels = BasePage.content_panels
    seo_panels = BasePage.seo_panels
    
    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Содержимое'),
        ObjectList(seo_panels, heading='SEO'),
        ObjectList(Page.settings_panels, heading='Настройки'),
    ])

class HomePage(BasePage):

    hero_text = RichTextField("Текст на главной", blank=True)

    subpage_types = ['blog.BlogCatalog', 'blog.AuthorContainer', 'About', 'Contacts']

    content_panels = BasePage.content_panels + [
        FieldPanel('hero_text'),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Содержимое'),
        ObjectList(BasePage.seo_panels, heading='SEO'),
        ObjectList(Page.settings_panels, heading='Настройки'),
    ])

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
