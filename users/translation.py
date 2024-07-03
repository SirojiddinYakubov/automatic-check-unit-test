from modeltranslation.translator import TranslationOptions, register
from .models import CustomUser


@register(CustomUser)
class CustomUserTranslationOptions(TranslationOptions):
    fields = ('username', 'first_name', 'last_name', 'middle_name', 'email',)


# translator.register(CustomUser, CustomUserTranslationOptions)
