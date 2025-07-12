from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, TabbedInterface, ObjectList
from wagtail.images.models import Image
from django.db import models

@register_setting(icon='site')
class SiteDataSettings(BaseSiteSetting):
    site_name = models.CharField(max_length=255, help_text="Название сайта")
    tg_chat_id = models.CharField(max_length=32, help_text="ID отправки формы в TG", blank=True, null=True,)
    contact_email = models.EmailField(blank=True, null=True, help_text="Контактный email")
    phone_number = models.CharField(max_length=20, blank=True, null=True, help_text="Телефон")
    address = models.TextField(blank=True, null=True, help_text="Адрес")

    logo_header = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Логотип в шапке',
        help_text='Рекомендуемый размер: 180×50 пикселей'
    )
    logo_footer = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Логотип в подвале',
        help_text='Рекомендуемый размер: 180×50 пикселей'
    )

    panels = [
        TabbedInterface([
            ObjectList([
                FieldPanel('site_name'),
                FieldPanel('contact_email'),
                FieldPanel('phone_number'),
                FieldPanel('address'),
            ], heading="Общие данные"),
            ObjectList([
                FieldPanel('logo_header'),
                FieldPanel('logo_footer'),
            ], heading="Логотипы"),
        ])
    ]

    class Meta:
        verbose_name = "Данные сайта"