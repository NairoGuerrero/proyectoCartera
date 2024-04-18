from .models import *


def saldo_pagos(numero_contrato):
    pagos = Pagos.objects.filter(contrato__numero_contrato=numero_contrato)
    contrato = Contratos.objects.get(numero_contrato=numero_contrato)
    valores_pago = sum(list(pagos.values_list('valor_pago', flat=True)))
    total = contrato.valor + contrato.valor_subcontratos
    saldo = total - valores_pago
    num_saldo = saldo
    return [contrato.valor, valores_pago, saldo, pagos, total, num_saldo]
