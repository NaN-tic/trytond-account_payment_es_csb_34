## coding: utf-8
# This file is part of account_payment_es_csb_34 module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.pyson import Eval

__all__ = [
    'Journal',
    'Group',
    ]
__metaclass__ = PoolMeta


class Journal:
    __name__ = 'account.payment.journal'
    csb34_type = fields.Selection([
            ('transfer', 'Transfers'),
            ('check', 'Checks'),
            ], 'Type of CSB 34 payment')
    csb_34_cost_key = fields.Selection([
            ('payer', 'Expense of the Payer'),
            ('recipient', 'Expense of the Recipient'),
            ], 'Cost Key')
    csb_34_concept = fields.Selection([
            ('payroll', 'Payroll'),
            ('pension', 'Pension'),
            ('other', 'Other'),
            ], 'Concept of the Order', help="Concept of the Order.")
    csb_34_direct_pay_order = fields.Boolean('Direct Pay Order',
        help="By default 'Not'.")
    csb_34_send_type = fields.Selection([
            ('mail', 'Ordinary Mail'),
            ('certified_mail', 'Certified Mail'),
            ('other', 'Other'),
            ], 'Send Type', states={
            'required': Eval('csb34_11_lc_type') != 'transfer',
            }, help="The sending type of the payment file.")
    csb_34_payroll_check = fields.Boolean('Payroll Check', help=('Check it if '
            'you want to add the 018 data type in the file (the vat of the '
            'recipient is added in the 018 data type).'))
    csb34_not_to_the_order = fields.Boolean('Not to the Order')
    csb34_barred = fields.Boolean('Barred')

    @staticmethod
    def default_csb34_type():
        return 'transfer'

    @staticmethod
    def default_csb_34_cost_key():
        return 'payer'

    @staticmethod
    def default_csb_34_concept():
        return 'other'

    @staticmethod
    def default_csb_34_send_type():
        return 'other'

    @staticmethod
    def default_csb_34_direct_pay_order():
        return False


class Group:
    __name__ = 'account.payment.group'

    def set_default_csb34_payment_values(self):
        values = self.set_default_payment_values()
        values['send_type'] = values['payment_journal'].csb_34_send_type

        if not values['address'] or not values['street'] or \
                not values['zip'] or not values['city']:
            self.raise_user_error('company_without_complete_address', (
                values['party'].name,))
        # Set csb 34 payment values
        values['not_to_the_order'] = values['payment_journal'].\
            csb34_not_to_the_order
        values['barred'] = values['payment_journal'].csb34_barred
        values['csb34_type'] = values['payment_journal'].csb34_type
        values['payroll_check'] = values['payment_journal'].\
            csb_34_payroll_check
        values['record_count'] = 0
        values['detail_record_count'] = 0
        values['payment_count'] = 0
        for receipt in values['receipts']:
            if not receipt['address']:
                self.raise_user_error('configuration_error',
                    error_description='party_without_address',
                    error_description_args=(receipt['party'].name,))
            if not receipt['zip'] or not receipt['city'] or not \
                    receipt['country']:
                self.raise_user_error('configuration_error',
                        error_description='party_without_complete_address',
                        error_description_args=(receipt['party'].name,))
            if not receipt['vat_number']:
                self.raise_user_error('configuration_error',
                    error_description='party_without_vat_number',
                    error_description_args=(receipt['party'].name,))
            receipt['cost'] = values['payment_journal'].csb_34_cost_key
            receipt['concept'] = values['payment_journal'].csb_34_concept
            receipt['direct_payment'] = 'true' if values[
                'payment_journal'].csb_34_direct_pay_order else 'false'
            receipt['name'] = receipt['party'].name
            receipt['country_code'] = receipt['country'].code
        return values
