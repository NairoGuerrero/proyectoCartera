from .models import *


def saldo_pagos(numero_contrato):
    pagos = Pagos.objects.filter(numero_contrato__numero_contrato=numero_contrato)
    valor_contrato = Contratos.objects.get(numero_contrato=numero_contrato).valor
    valores_pago = sum(list(pagos.values_list('valor_pago', flat=True)))
    saldo = valor_contrato - valores_pago
    return [valor_contrato, valores_pago, saldo, pagos]
