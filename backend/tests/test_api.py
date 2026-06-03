"""
Testes de integração dos endpoints.
"""
from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.usuarios.models import Usuario
from api.condominio.models import Condominio
from api.unidade.models import Unidade
from api.cobranca.models import Cobranca
from api.acordo.models import Acordo, AcordoParcela


def criar_usuario(tipo='administrador'):
    return Usuario.objects.create_user(username=f'user_{tipo}', password='senha123', tipo=tipo)


def get_token(client, username, password='senha123'):
    resp = client.post('/api/token/', {'username': username, 'password': password}, format='json')
    return resp.data.get('access')


class AutenticacaoTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = criar_usuario('administrador')

    def test_obter_token_valido(self):
        resp = self.client.post('/api/token/', {'username': 'user_administrador', 'password': 'senha123'}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('access', resp.data)
        self.assertIn('refresh', resp.data)

    def test_token_invalido_retorna_401(self):
        resp = self.client.post('/api/token/', {'username': 'inexistente', 'password': 'errada'}, format='json')
        self.assertEqual(resp.status_code, 401)

    def test_endpoint_protegido_sem_token(self):
        resp = self.client.get('/api/condominios/')
        self.assertEqual(resp.status_code, 401)


class CondominioTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = criar_usuario('administrador')
        self.user = criar_usuario('usuario')
        token = get_token(self.client, 'user_administrador')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_criar_condominio(self):
        resp = self.client.post('/api/condominios/', {
            'nome': 'Residencial Teste',
            'endereco': 'Rua A, 100',
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data['nome'], 'Residencial Teste')

    def test_listar_condominios(self):
        Condominio.objects.create(nome='Cond A', endereco='End A')
        resp = self.client.get('/api/condominios/')
        self.assertEqual(resp.status_code, 200)

    def test_usuario_comum_nao_pode_criar(self):
        token_user = get_token(self.client, 'user_usuario')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_user}')
        resp = self.client.post('/api/condominios/', {'nome': 'Teste', 'endereco': 'End'}, format='json')
        self.assertEqual(resp.status_code, 403)

    def test_nome_curto_retorna_400(self):
        resp = self.client.post('/api/condominios/', {'nome': 'AB', 'endereco': 'End'}, format='json')
        self.assertEqual(resp.status_code, 400)


class CobrancaTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = criar_usuario('administrador')
        token = get_token(self.client, 'user_administrador')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        self.cond = Condominio.objects.create(nome='Cond Teste', endereco='End Teste')
        self.unidade = Unidade.objects.create(numero='101', condominio=self.cond, status='OCUPADO')

    def test_criar_cobranca(self):
        resp = self.client.post('/api/cobrancas/', {
            'unidade': self.unidade.id,
            'competencia': '2026-01-01',
            'data_vencimento': '2026-01-10',
            'valor': '500.00',
            'status': 'PENDENTE',
        }, format='json')
        self.assertEqual(resp.status_code, 201)

    def test_cobranca_paga_sem_data_pagamento_retorna_400(self):
        resp = self.client.post('/api/cobrancas/', {
            'unidade': self.unidade.id,
            'competencia': '2026-01-01',
            'data_vencimento': '2026-01-10',
            'valor': '500.00',
            'status': 'PAGO',
        }, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_filtro_por_status(self):
        Cobranca.objects.create(
            unidade=self.unidade, competencia=date(2026, 1, 1),
            data_vencimento=date(2026, 1, 10), valor=500, status='VENCIDO'
        )
        resp = self.client.get('/api/cobrancas/?status=VENCIDO')
        self.assertEqual(resp.status_code, 200)
        for item in resp.data.get('results', resp.data):
            self.assertEqual(item['status'], 'VENCIDO')

    def test_cobranca_pendente_vencida_aparece_como_vencida_na_consulta(self):
        Cobranca.objects.create(
            unidade=self.unidade,
            competencia=date(2026, 1, 1),
            data_vencimento=date.today() - timedelta(days=1),
            valor=Decimal('500.00'),
            status='PENDENTE',
        )

        resp = self.client.get('/api/cobrancas/?status=VENCIDO')

        self.assertEqual(resp.status_code, 200)
        resultados = resp.data.get('results', resp.data)
        self.assertEqual(len(resultados), 1)
        self.assertEqual(resultados[0]['status'], 'VENCIDO')

    def test_filtro_por_unidade(self):
        Cobranca.objects.create(
            unidade=self.unidade, competencia=date(2026, 1, 1),
            data_vencimento=date(2026, 1, 10), valor=300, status='PENDENTE'
        )
        resp = self.client.get(f'/api/cobrancas/?unidade={self.unidade.id}')
        self.assertEqual(resp.status_code, 200)

    def test_endpoint_pagar_calcula_multa_juros(self):
        ontem = date.today() - timedelta(days=5)
        cobranca = Cobranca.objects.create(
            unidade=self.unidade, competencia=date(2026, 1, 1),
            data_vencimento=ontem, valor=Decimal('1000.00'), status='VENCIDO'
        )
        resp = self.client.post(f'/api/cobrancas/{cobranca.id}/pagar/', {
            'data_pagamento': str(date.today()),
            'forma_pagamento': 'PIX',
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['status'], 'PAGO')
        self.assertGreater(float(resp.data['multa']), 0)
        self.assertGreater(float(resp.data['juros']), 0)


class AcordoTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = criar_usuario('administrador')
        token = get_token(self.client, 'user_administrador')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        self.cond = Condominio.objects.create(nome='Cond Acordo', endereco='End')
        self.unidade = Unidade.objects.create(numero='202', condominio=self.cond, status='OCUPADO')

        ontem = date.today() - timedelta(days=10)
        self.c1 = Cobranca.objects.create(
            unidade=self.unidade, competencia=date(2026, 1, 1),
            data_vencimento=ontem, valor=Decimal('500.00'), status='VENCIDO'
        )
        self.c2 = Cobranca.objects.create(
            unidade=self.unidade, competencia=date(2026, 2, 1),
            data_vencimento=ontem, valor=Decimal('500.00'), status='VENCIDO'
        )

    def test_criar_acordo_gera_parcelas(self):
        resp = self.client.post('/api/acordos/', {
            'unidade': self.unidade.id,
            'numero_parcelas': 3,
            'cobrancas_ids': [self.c1.id, self.c2.id],
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(len(resp.data['parcelas']), 3)

    def test_acordo_rejeita_cobranca_de_outra_unidade(self):
        outra_unidade = Unidade.objects.create(numero='303', condominio=self.cond)
        ontem = date.today() - timedelta(days=5)
        c_outra = Cobranca.objects.create(
            unidade=outra_unidade, competencia=date(2026, 1, 1),
            data_vencimento=ontem, valor=Decimal('300.00'), status='VENCIDO'
        )
        resp = self.client.post('/api/acordos/', {
            'unidade': self.unidade.id,
            'numero_parcelas': 2,
            'cobrancas_ids': [self.c1.id, c_outra.id],
        }, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_acordo_rejeita_cobranca_nao_vencida(self):
        c_pendente = Cobranca.objects.create(
            unidade=self.unidade, competencia=date(2026, 3, 1),
            data_vencimento=date(2027, 3, 10), valor=Decimal('400.00'), status='PENDENTE'
        )
        resp = self.client.post('/api/acordos/', {
            'unidade': self.unidade.id,
            'numero_parcelas': 2,
            'cobrancas_ids': [c_pendente.id],
        }, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_pagar_todas_parcelas_quita_acordo(self):
        resp = self.client.post('/api/acordos/', {
            'unidade': self.unidade.id,
            'numero_parcelas': 2,
            'cobrancas_ids': [self.c1.id, self.c2.id],
        }, format='json')
        self.assertEqual(resp.status_code, 201)

        acordo = Acordo.objects.get(id=resp.data['id'])
        for parcela in acordo.parcelas.all():
            pagamento = self.client.post(f'/api/parcelas-acordo/{parcela.id}/pagar/', {
                'data_pagamento': str(date.today()),
            }, format='json')
            self.assertEqual(pagamento.status_code, 200)

        acordo.refresh_from_db()
        self.assertEqual(acordo.status, Acordo.STATUS_QUITADO)


class DashboardTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = criar_usuario('administrador')
        token = get_token(self.client, 'user_administrador')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_dashboard_retorna_estrutura_correta(self):
        resp = self.client.get('/api/dashboard/')
        self.assertEqual(resp.status_code, 200)
        campos = [
            'total_condominios', 'total_unidades', 'total_cobrancas',
            'total_pagas', 'total_pendentes', 'total_vencidas',
            'valor_total_recebido', 'valor_total_em_aberto', 'total_acordos',
        ]
        for campo in campos:
            self.assertIn(campo, resp.data)

    def test_inadimplencia_resumo(self):
        resp = self.client.get('/api/inadimplencia/resumo/')
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.data, list)
