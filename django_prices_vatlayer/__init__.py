from prices import Tax

from .utils import get_tax_for_country


class EuropeanVAT(Tax):
    def __init__(self, country_code, rate_name):
        self.country_code = country_code
        self.rate_name = rate_name

    def calculate_tax(self, price_obj):
        vat_rate = get_tax_for_country(self.country_code, self.rate_name)
        return (vat_rate * price_obj.net) / 100
