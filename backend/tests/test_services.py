"""
Testes unitários dos services.
Execute com: DJANGO_SETTINGS_MODULE=condominios.settings_test python manage.py test tests
"""
from decimal import Decimal
from datetime import date
from django.test import TestCase
from api.cobranca.services import calcular_multa_juros


class TestCalculoMultaJuros(TestCase):

    def test_sem_atraso_nao_aplica_multa(self):
        resultado = calcular_multa_juros(
            valor=Decimal('1000.00'),
            data_vencimento=date(2026, 1, 10),
            data_pagamento=date(2026, 1, 10),
        )
        self.assertEqual(resultado['multa'], Decimal('0'))
        self.assertEqual(resultado['juros'], Decimal('0'))
        self.assertEqual(resultado['dias_atraso'], 0)

    def test_pagamento_antes_vencimento_sem_multa(self):
        resultado = calcular_multa_juros(
            valor=Decimal('500.00'),
            data_vencimento=date(2026, 1, 15),
            data_pagamento=date(2026, 1, 10),
        )
        self.assertEqual(resultado['multa'], Decimal('0'))
        self.assertEqual(resultado['juros'], Decimal('0'))

    def test_multa_dois_porcento_apos_vencimento(self):
        resultado = calcular_multa_juros(
            valor=Decimal('1000.00'),
            data_vencimento=date(2026, 1, 1),
            data_pagamento=date(2026, 1, 2),  # 1 dia de atraso
        )
        self.assertEqual(resultado['multa'], Decimal('20.00'))   # 2% de 1000

    def test_juros_por_dia(self):
        resultado = calcular_multa_juros(
            valor=Decimal('1000.00'),
            data_vencimento=date(2026, 1, 1),
            data_pagamento=date(2026, 1, 11),  # 10 dias de atraso
        )
        # juros = 1000 * 0.00033 * 10 = 3.30
        self.assertEqual(resultado['juros'], Decimal('3.30'))
        self.assertEqual(resultado['dias_atraso'], 10)

    def test_valor_total_com_multa_e_juros(self):
        resultado = calcular_multa_juros(
            valor=Decimal('1000.00'),
            data_vencimento=date(2026, 1, 1),
            data_pagamento=date(2026, 1, 11),  # 10 dias
        )
        # multa = 20.00, juros = 3.30, total = 1023.30
        self.assertEqual(resultado['valor_total'], Decimal('1023.30'))

    def test_sem_data_pagamento_retorna_zeros(self):
        resultado = calcular_multa_juros(
            valor=Decimal('1000.00'),
            data_vencimento=date(2026, 1, 1),
            data_pagamento=None,
        )
        self.assertEqual(resultado['multa'], Decimal('0'))
        self.assertEqual(resultado['juros'], Decimal('0'))
