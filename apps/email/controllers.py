from apps.admin.register import quickstart_admin_model
from .models import OutboundEmail

quickstart_admin_model(OutboundEmail, 'emails', 'emails', 'Emails', enable_edit=False, enable_delete=False, enable_new=False)
