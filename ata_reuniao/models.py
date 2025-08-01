# ata_reuniao/models.py (CORRIGIDO E REATORADO)

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone 
from django.conf import settings


class AtaReuniao(models.Model):
    """
    Modelo para gerenciar as Atas de Reunião, com foco em ações e responsabilidades.
    """
    class Natureza(models.TextChoices):
        ADMINISTRATIVA = 'Administrativa', _('Administrativa')
        COMERCIAL = 'Comercial', _('Comercial')
        TECNICA = 'Técnica', _('Técnica')
        OUTRO = 'Outro', _('Outro')

    class Status(models.TextChoices):
        CONCLUIDO = 'Concluído', _('Concluído')
        ANDAMENTO = 'Andamento', _('Em Andamento')
        PENDENTE = 'Pendente', _('Pendente')
        CANCELADO = 'Cancelado', _('Cancelado')

    # --- TODOS OS CAMPOS DECLARADOS PRIMEIRO ---
    
    contrato = models.ForeignKey(
        'cliente.Cliente', 
        on_delete=models.PROTECT,
        related_name='atas',
        verbose_name=_("Contrato")
    )
    coordenador = models.ForeignKey(
        'departamento_pessoal.Funcionario',
        on_delete=models.PROTECT,
        related_name='atas_coordenadas',
        verbose_name=_("Coordenador")
    )
    responsavel = models.ForeignKey(
        'departamento_pessoal.Funcionario',
        on_delete=models.PROTECT,
        related_name='atas_responsaveis',
        verbose_name=_("Responsável")
    )
    natureza = models.CharField(
        max_length=20,
        choices=Natureza.choices,
        default=Natureza.TECNICA,
        verbose_name=_("Natureza")
    )
    acao = models.TextField(
        verbose_name=_("Ação/Proposta"),
        help_text=_("Descreva a ação a ser tomada ou a proposta discutida.")
    )
    entrada = models.DateField(
        verbose_name=_("Data de Entrada")
    )
    prazo = models.DateField(
        verbose_name=_("Prazo Final"),
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDENTE,
        verbose_name=_("Status")
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name=_("Criado em"))
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name=_("Atualizado em"))

    # --- META CLASS DEPOIS DOS CAMPOS ---
    
    class Meta:
        db_table = 'ata_reuniao'
        verbose_name = _("Ata de Reunião")
        verbose_name_plural = _("Atas de Reunião")
        ordering = ['-entrada', '-id']
        get_latest_by = 'entrada'

    # --- MÉTODOS DEPOIS DA META CLASS ---
    
    def __str__(self):
        # Acessa o nome do contrato relacionado. O Django carrega o objeto automaticamente.
        return f"Ata #{self.id} - {self.contrato.nome}"

    @property
    def is_overdue(self):
        """Retorna True se a ata estiver com o prazo vencido e não finalizada."""
        if self.status in [self.Status.CONCLUIDO, self.Status.CANCELADO]:
            return False
        if self.prazo and self.prazo < timezone.now().date():
            return True
        return False

class HistoricoAta(models.Model):
    """
    Armazena um registro de cada comentário ou atualização feita em uma Ata de Reunião.
    """
    ata = models.ForeignKey(
        AtaReuniao, 
        on_delete=models.CASCADE, 
        related_name='historico',
        verbose_name=_("Ata de Reunião")
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_("Usuário")
    )
    timestamp = models.DateTimeField(
        auto_now_add=True, 
        verbose_name=_("Data e Hora")
    )
    comentario = models.TextField(
        verbose_name=_("Comentário")
    )

    class Meta:
        db_table = 'historico_ata'
        verbose_name = _("Histórico da Ata")
        verbose_name_plural = _("Históricos da Ata")
        ordering = ['-timestamp'] # Ordena do mais recente para o mais antigo

    def __str__(self):
        return f"Comentário em {self.ata} por {self.usuario} em {self.timestamp.strftime('%d/%m/%Y %H:%M')}"
    
    