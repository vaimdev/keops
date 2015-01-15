from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from keops.db import models
from keops.modules.base.models.locale import Language


class Translation(models.Model):
    """
    Translates database field value.
    """
    content_type = models.ForeignKey(ContentType)
    name = models.CharField(_('name'), max_length=64)
    language = models.ForeignKey(Language, verbose_name=_('language'))
    source = models.CharField(_('source'), max_length=1024, db_index=True)
    value = models.TextField(_('value'))

    class Meta:
        unique_together = (('content_type', 'name'))
        verbose_name = _('translation')
        verbose_name_plural = _('translations')


