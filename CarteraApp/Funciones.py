from .models import *
def saldo_pagos(Numero_Contrato):
    pagos = Pagos.objects.filter(numero_contrato__Numero_Contrato=Numero_Contrato)
    valor_contrato = Contratos.objects.get(Numero_Contrato=Numero_Contrato).valor
    valores_pago = sum(list(pagos.values_list('valor_pago', flat=True)))
    saldo = valor_contrato - valores_pago
    return [valor_contrato, valores_pago, saldo, pagos]