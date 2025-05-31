from invoices.notifications.new_invoice_mail_notify import NewInvoiceMailNotify
from invoices.notifications.paid_invoice_mail_notify import PaidInvoiceMailNotify
from invoices.notifications.overdue_invoice_notification import OverdueInvoiceMailNotify
from shared.notifications.mail_notify import MailNotify


class InvoiceNotifyFactory:
    def create(self, notify_type: str) -> MailNotify:
        if notify_type == "new":
            return NewInvoiceMailNotify()
        elif notify_type == "paid":
            return PaidInvoiceMailNotify()
        elif notify_type == "overdue":
            return OverdueInvoiceMailNotify()
        else:
            raise ValueError(f"Unknown notify type: {notify_type}")
