from prices import Tax

from .utils import get_tax_for_country


class EuropeanVAT(Tax):
    def __init__(self, country_code, rate_name):
        self.country_code = country_code
        self.rate_name = rate_name

    def calculate_tax(self, price_obj):
        vat_rate = get_tax_for_country(self.country_code, self.rate_name)
        if vat_rate is None:
            return 0
        return (vat_rate * price_obj.gross) / 100

    def apply(self, price_obj):
        return super(EuropeanVAT, self).apply(price_obj)

    def __repr__(self):
        return 'EuropeanVat(%s, %s)' % (self.country_code, self.rate_name)
