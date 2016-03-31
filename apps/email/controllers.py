from apps.admin.register import quickstart_admin_model
from .models import OutboundEmail

quickstart_admin_model(OutboundEmail, 'emails', 'emails', 'Emails',
                       name_singular='email', name_plural='emails',
                       enable_edit=False, enable_delete=False, enable_new=False, list_fields=['sent', 'date_created'])
