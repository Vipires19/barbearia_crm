"""
Views para webhooks do WhatsApp
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from barbearia.whatsapp_integration import WhatsAppWebhook, whatsapp_api
from .models import Agendamento
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def whatsapp_webhook(request):
    """
    Webhook para receber e processar mensagens do WhatsApp
    """
    if request.method == 'GET':
        # Verificação do webhook
        return WhatsAppWebhook.verify_webhook(request)
    
    elif request.method == 'POST':
        # Processamento de mensagens
        return WhatsAppWebhook.process_webhook(request)


@csrf_exempt
@require_http_methods(["POST"])
def send_agendamento_confirmation(request, agendamento_id):
    """
    Envia confirmação de agendamento via WhatsApp
    """
    try:
        agendamento = Agendamento.objects.get(id=agendamento_id)
        
        if whatsapp_api.send_agendamento_confirmation(agendamento):
            agendamento.confirmado_whatsapp = True
            agendamento.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Confirmação enviada com sucesso!'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Erro ao enviar confirmação'
            }, status=500)
            
    except Agendamento.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Agendamento não encontrado'
        }, status=404)
    
    except Exception as e:
        logger.error(f"Erro ao enviar confirmação: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Erro interno do servidor'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def send_reminder(request, agendamento_id):
    """
    Envia lembrete de agendamento via WhatsApp
    """
    try:
        agendamento = Agendamento.objects.get(id=agendamento_id)
        
        if whatsapp_api.send_reminder(agendamento):
            return JsonResponse({
                'success': True,
                'message': 'Lembrete enviado com sucesso!'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Erro ao enviar lembrete'
            }, status=500)
            
    except Agendamento.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Agendamento não encontrado'
        }, status=404)
    
    except Exception as e:
        logger.error(f"Erro ao enviar lembrete: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Erro interno do servidor'
        }, status=500)

