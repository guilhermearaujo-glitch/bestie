#!/usr/bin/env python3
"""
Bestie — Gerador de Relatório Mensal
Para o nutri Matheus Coelho
Uso: python3 gerar_relatorio_bestie.py <logs_json> <mes> <ano>

O arquivo logs_json deve conter os registros do Notion exportados.
Este script também pode ser chamado diretamente com dados hardcoded para teste.
"""

import json
import sys
import os
from datetime import datetime, date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, PageBreak
)
from reportlab.pdfgen import canvas as pdfcanvas

# ── CORES ──────────────────────────────────────────────────────────────────────
AZUL_ESCURO  = colors.HexColor('#1a3a5c')
AZUL_MEDIO   = colors.HexColor('#1b4f72')
AZUL_CLARO   = colors.HexColor('#d6e4f0')
VERDE        = colors.HexColor('#1a7a40')
VERDE_CLARO  = colors.HexColor('#eaf7ef')
LARANJA      = colors.HexColor('#e67e22')
LARANJA_CLAR = colors.HexColor('#fff4e6')
CINZA        = colors.HexColor('#888888')
CINZA_CLARO  = colors.HexColor('#f5f5f5')
CINZA_BORDA  = colors.HexColor('#e0e0e0')
BRANCO       = colors.white
PRETO        = colors.HexColor('#1a1a1a')

MESES_PT = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho',
            'Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']

# ── CANVAS COM CABEÇALHO/RODAPÉ ───────────────────────────────────────────────
class BestieCanvas(pdfcanvas.Canvas):
    def __init__(self, *args, mes_ano='', **kwargs):
        super().__init__(*args, **kwargs)
        self.mes_ano = mes_ano
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for i, state in enumerate(self._saved_page_states):
            self.__dict__.update(state)
            self.draw_page(i + 1, num_pages)
            super().showPage()
        super().save()

    def draw_page(self, page_num, total):
        w, h = A4
        # Faixa de topo
        self.setFillColor(AZUL_ESCURO)
        self.rect(0, h - 1.5*cm, w, 1.5*cm, fill=1, stroke=0)
        self.setFillColor(BRANCO)
        self.setFont('Helvetica-Bold', 10)
        self.drawString(1.5*cm, h - 1.0*cm, 'BESTIE')
        self.setFont('Helvetica', 9)
        self.drawString(1.5*cm + 50, h - 1.0*cm, f'| Relatório {self.mes_ano} — Guilherme Araujo')
        self.setFont('Helvetica', 8)
        self.drawRightString(w - 1.5*cm, h - 1.0*cm, f'Página {page_num}/{total}')
        # Rodapé
        self.setFillColor(CINZA_CLARO)
        self.rect(0, 0, w, 1.2*cm, fill=1, stroke=0)
        self.setFillColor(CINZA)
        self.setFont('Helvetica', 7.5)
        self.drawString(1.5*cm, 0.45*cm, 'Gerado automaticamente pelo Bestie • Uso exclusivo para acompanhamento com o nutri Matheus Coelho')
        self.drawRightString(w - 1.5*cm, 0.45*cm, f'guilherme.araujo@previnamed.io')

# ── ESTILOS ───────────────────────────────────────────────────────────────────
def make_styles():
    base = getSampleStyleSheet()
    s = {}
    s['titulo_secao'] = ParagraphStyle(
        'titulo_secao', fontName='Helvetica-Bold', fontSize=11,
        textColor=AZUL_ESCURO, spaceBefore=14, spaceAfter=6,
        borderPad=(0,0,4,0)
    )
    s['subtitulo'] = ParagraphStyle(
        'subtitulo', fontName='Helvetica-Bold', fontSize=9.5,
        textColor=AZUL_MEDIO, spaceBefore=8, spaceAfter=3
    )
    s['corpo'] = ParagraphStyle(
        'corpo', fontName='Helvetica', fontSize=9,
        textColor=PRETO, leading=14, spaceAfter=4, alignment=TA_JUSTIFY
    )
    s['corpo_small'] = ParagraphStyle(
        'corpo_small', fontName='Helvetica', fontSize=8,
        textColor=CINZA, leading=12, spaceAfter=2
    )
    s['label_card'] = ParagraphStyle(
        'label_card', fontName='Helvetica-Bold', fontSize=8,
        textColor=CINZA, spaceAfter=1, leading=11
    )
    s['valor_card'] = ParagraphStyle(
        'valor_card', fontName='Helvetica-Bold', fontSize=22,
        textColor=AZUL_ESCURO, spaceAfter=0, leading=26
    )
    s['centro'] = ParagraphStyle(
        'centro', fontName='Helvetica', fontSize=9,
        textColor=PRETO, alignment=TA_CENTER, leading=13
    )
    s['negrito'] = ParagraphStyle(
        'negrito', fontName='Helvetica-Bold', fontSize=9,
        textColor=PRETO, leading=13, spaceAfter=2
    )
    return s


# ── HELPERS ───────────────────────────────────────────────────────────────────
def secao(titulo, styles):
    return [
        HRFlowable(width='100%', thickness=1.5, color=AZUL_ESCURO, spaceAfter=4),
        Paragraph(titulo.upper(), styles['titulo_secao']),
    ]

def card_numero(label, valor, cor_fundo, cor_texto, styles):
    """Retorna uma Table de 1 célula estilo card de KPI."""
    p_label = Paragraph(label, ParagraphStyle('cl', fontName='Helvetica', fontSize=7.5,
                         textColor=cor_texto, leading=10))
    p_valor = Paragraph(str(valor), ParagraphStyle('cv', fontName='Helvetica-Bold', fontSize=20,
                         textColor=cor_texto, leading=24))
    t = Table([[p_label], [p_valor]], colWidths=[3.8*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), cor_fundo),
        ('BOX',        (0,0), (-1,-1), 0.5, CINZA_BORDA),
        ('ROUNDEDCORNERS', [6]),
        ('TOPPADDING',    (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING',   (0,0), (-1,-1), 10),
        ('RIGHTPADDING',  (0,0), (-1,-1), 10),
    ]))
    return t

def humor_cor(humor):
    mapa = {
        '😄 Ótimo':  ('#eaf7ef', '#1a7a40'),
        '🙂 Bom':    ('#e8f0fe', '#1a3a5c'),
        '😐 Ok':     ('#fffde6', '#7d6608'),
        '😔 Cansado':('#fff4e6', '#a04000'),
        '😫 Péssimo':('#fde8e8', '#a00000'),
    }
    return mapa.get(humor, ('#f5f5f5', '#444444'))


# ── GERADOR PRINCIPAL ─────────────────────────────────────────────────────────
def gerar_relatorio(logs, mes, ano, output_path):
    """
    logs: lista de dicts com os campos do Notion
    mes: int (1-12)
    ano: int
    """
    mes_nome = MESES_PT[mes - 1]
    mes_ano  = f'{mes_nome} {ano}'
    styles   = make_styles()

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        topMargin=2.2*cm, bottomMargin=1.8*cm,
        leftMargin=1.6*cm, rightMargin=1.6*cm,
        title=f'Relatório Bestie — {mes_ano} — Guilherme Araujo',
        author='Bestie',
    )

    story = []
    W = A4[0] - 3.2*cm  # largura útil

    # ── CAPA / CABEÇALHO DO RELATÓRIO ─────────────────────────────────────────
    story.append(Spacer(1, 0.4*cm))
    # Bloco título
    titulo_data = [
        [Paragraph('<b>RELATÓRIO MENSAL DE SAÚDE</b>', ParagraphStyle(
            't1', fontName='Helvetica-Bold', fontSize=18, textColor=AZUL_ESCURO,
            alignment=TA_LEFT, leading=22)),
         Paragraph(f'<b>{mes_ano.upper()}</b>', ParagraphStyle(
            't2', fontName='Helvetica-Bold', fontSize=14, textColor=BRANCO,
            alignment=TA_CENTER, leading=18))]
    ]
    t_titulo = Table(titulo_data, colWidths=[W*0.6, W*0.4])
    t_titulo.setStyle(TableStyle([
        ('BACKGROUND', (1,0), (1,0), AZUL_ESCURO),
        ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (0,0), 0),
        ('LEFTPADDING', (1,0), (1,0), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('ROUNDEDCORNERS', [6]),
    ]))
    story.append(t_titulo)
    story.append(Spacer(1, 0.3*cm))

    # Linha de info
    info_data = [[
        Paragraph('<b>Paciente:</b> Guilherme da Conceicao Araujo', styles['corpo_small']),
        Paragraph('<b>Nutricionista:</b> Matheus Coelho (CRN 75166)', styles['corpo_small']),
        Paragraph(f'<b>Gerado em:</b> {date.today().strftime("%d/%m/%Y")}', styles['corpo_small']),
    ]]
    t_info = Table(info_data, colWidths=[W/3, W/3, W/3])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CINZA_CLARO),
        ('BOX',        (0,0), (-1,-1), 0.5, CINZA_BORDA),
        ('TOPPADDING',    (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING',   (0,0), (-1,-1), 10),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 0.5*cm))

    # ── RESUMO EXECUTIVO (KPIs) ────────────────────────────────────────────────
    story += secao('Resumo do Mes', styles)
    story.append(Spacer(1, 0.2*cm))

    total_dias = len(logs)
    dias_registrados = sum(1 for l in logs if l.get('REF 1 — Café') or l.get('REF 2 — Almoço') or l.get('REF 3 — Pós-treino/Jantar'))
    dias_treino = sum(1 for l in logs if l.get('Treino do Dia', '').strip())
    vitc_ok = sum(1 for l in logs if l.get('Vitamina C') == '__YES__')
    omega_ok = sum(1 for l in logs if l.get('Ômega 3 (almoço)') == '__YES__')
    dias_ref1 = sum(1 for l in logs if l.get('REF 1 — Café', '').strip())
    dias_ref2 = sum(1 for l in logs if l.get('REF 2 — Almoço', '').strip())
    dias_ref3 = sum(1 for l in logs if l.get('REF 3 — Pós-treino/Jantar', '').strip())
    aderencia = round((dias_registrados / total_dias * 100) if total_dias else 0)

    humores = [l.get('Humor & Energia','') for l in logs if l.get('Humor & Energia','')]
    humor_map = {'😄 Ótimo':5,'🙂 Bom':4,'😐 Ok':3,'😔 Cansado':2,'😫 Péssimo':1}
    humor_med = round(sum(humor_map.get(h,3) for h in humores)/len(humores),1) if humores else 0
    humor_labels = {5:'Otimo',4:'Bom',3:'Ok',2:'Cansado',1:'Pessimo'}
    humor_label = humor_labels.get(round(humor_med), 'Ok')

    cards = [
        card_numero('DIAS\nREGISTRADOS', f'{dias_registrados}/{total_dias}', AZUL_CLARO, AZUL_ESCURO, styles),
        card_numero('ADERENCIA\nAO PLANO', f'{aderencia}%', VERDE_CLARO if aderencia>=80 else LARANJA_CLAR,
                    VERDE if aderencia>=80 else LARANJA, styles),
        card_numero('DIAS\nDE TREINO', str(dias_treino), CINZA_CLARO, AZUL_MEDIO, styles),
        card_numero('HUMOR\nMEDIO', humor_label, CINZA_CLARO, AZUL_ESCURO, styles),
    ]
    ncols = len(cards)
    col_w = W / ncols
    t_cards = Table([cards], colWidths=[col_w]*ncols, hAlign='LEFT')
    t_cards.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING',  (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING',   (0,0), (-1,-1), 0),
        ('BOTTOMPADDING',(0,0), (-1,-1), 0),
        ('LEFTPADDING',  (0,0), (0,0), 0),
    ]))
    story.append(t_cards)
    story.append(Spacer(1, 0.5*cm))

    # ── ADERÊNCIA AOS REMÉDIOS ─────────────────────────────────────────────────
    story += secao('Adherencia aos Remedios e Suplementos', styles)
    story.append(Spacer(1, 0.15*cm))

    def pct(n): return f'{round(n/total_dias*100) if total_dias else 0}%'
    def barra(n, total, cor):
        pct_val = n/total if total else 0
        bar_w = W - 6*cm
        preenchido = bar_w * pct_val
        data = [['', '']]
        t = Table(data, colWidths=[preenchido, bar_w - preenchido])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,0), cor),
            ('BACKGROUND', (1,0), (1,0), CINZA_CLARO),
            ('TOPPADDING',    (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        return t

    rem_rows = [
        [Paragraph('<b>Remedio / Suplemento</b>', styles['label_card']),
         Paragraph('<b>Tomou</b>', styles['label_card']),
         Paragraph('<b>% Aderencia</b>', styles['label_card'])],
        ['Vitamina C 1g (diario)',        f'{vitc_ok}/{total_dias}',  pct(vitc_ok)],
        ['Omega 3 (diario, apos almoco)', f'{omega_ok}/{total_dias}', pct(omega_ok)],
    ]
    col_ws = [W*0.55, W*0.2, W*0.25]
    t_rem = Table(rem_rows, colWidths=col_ws)
    t_rem.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0),   AZUL_CLARO),
        ('BACKGROUND',    (0,1), (-1,1),   CINZA_CLARO),
        ('BACKGROUND',    (0,2), (-1,2),   BRANCO),
        ('BOX',           (0,0), (-1,-1),  0.5, CINZA_BORDA),
        ('INNERGRID',     (0,0), (-1,-1),  0.3, CINZA_BORDA),
        ('FONTNAME',      (0,1), (-1,-1),  'Helvetica'),
        ('FONTSIZE',      (0,1), (-1,-1),  9),
        ('TOPPADDING',    (0,0), (-1,-1),  7),
        ('BOTTOMPADDING', (0,0), (-1,-1),  7),
        ('LEFTPADDING',   (0,0), (-1,-1),  9),
        ('TEXTCOLOR',     (2,1), (2,-1),   VERDE if vitc_ok/max(total_dias,1)>=0.8 else LARANJA),
        ('FONTNAME',      (2,1), (2,-1),   'Helvetica-Bold'),
    ]))
    story.append(t_rem)
    story.append(Spacer(1, 0.5*cm))

    # ── REFEIÇÕES POR DIA ──────────────────────────────────────────────────────
    story += secao('Log de Refeicoes — Dia a Dia', styles)
    story.append(Paragraph(
        f'Total de dias com REF.1: <b>{dias_ref1}</b> | REF.2: <b>{dias_ref2}</b> | REF.3: <b>{dias_ref3}</b>',
        styles['corpo']
    ))
    story.append(Spacer(1, 0.2*cm))

    header_ref = [
        Paragraph('<b>Data</b>', styles['label_card']),
        Paragraph('<b>REF. 1 — Cafe</b>', styles['label_card']),
        Paragraph('<b>REF. 2 — Almoco</b>', styles['label_card']),
        Paragraph('<b>REF. 3 — Pos-treino/Jantar</b>', styles['label_card']),
        Paragraph('<b>Humor</b>', styles['label_card']),
    ]
    ref_rows = [header_ref]

    for i, log in enumerate(sorted(logs, key=lambda x: x.get('Data',''))):
        data_str = log.get('Data','—').split('—')[0].strip()
        ref1_t = log.get('Horário REF 1','')
        ref2_t = log.get('Horário REF 2','')
        ref3_t = log.get('Horário REF 3','')

        def fmt_ref(texto, hora):
            if not texto: return Paragraph('—', styles['corpo_small'])
            linha = texto.strip().replace('\n',' ')
            if hora: linha = f'[{hora}] {linha}'
            return Paragraph(linha[:120] + ('...' if len(linha)>120 else ''), styles['corpo_small'])

        humor = log.get('Humor & Energia','')
        bg_humor, cor_humor = humor_cor(humor)
        emoji_humor = humor.split(' ')[0] if humor else '—'

        row_bg = CINZA_CLARO if i%2==0 else BRANCO
        ref_rows.append([
            Paragraph(f'<b>{data_str}</b>', styles['corpo_small']),
            fmt_ref(log.get('REF 1 — Café',''), ref1_t),
            fmt_ref(log.get('REF 2 — Almoço',''), ref2_t),
            fmt_ref(log.get('REF 3 — Pós-treino/Jantar',''), ref3_t),
            Paragraph(emoji_humor, ParagraphStyle('eh', fontName='Helvetica', fontSize=14,
                       alignment=TA_CENTER, leading=18)),
        ])

    cw_ref = [2.2*cm, (W-2.2*cm)*0.28, (W-2.2*cm)*0.28, (W-2.2*cm)*0.28, (W-2.2*cm)*0.16]
    t_ref = Table(ref_rows, colWidths=cw_ref, repeatRows=1)
    row_styles = [
        ('BACKGROUND',    (0,0), (-1,0),  AZUL_ESCURO),
        ('TEXTCOLOR',     (0,0), (-1,0),  BRANCO),
        ('FONTNAME',      (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,0),  8),
        ('BOX',           (0,0), (-1,-1), 0.5, CINZA_BORDA),
        ('INNERGRID',     (0,0), (-1,-1), 0.3, CINZA_BORDA),
        ('VALIGN',        (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING',    (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING',   (0,0), (-1,-1), 7),
        ('ALIGN',         (4,0), (4,-1),  'CENTER'),
    ]
    for i in range(1, len(ref_rows)):
        if i % 2 == 1:
            row_styles.append(('BACKGROUND', (0,i), (-1,i), CINZA_CLARO))
    t_ref.setStyle(TableStyle(row_styles))
    story.append(t_ref)
    story.append(Spacer(1, 0.5*cm))

    # ── TREINOS ───────────────────────────────────────────────────────────────
    story += secao('Treinos Realizados', styles)
    treinos_log = [(l.get('Data','').split('—')[0].strip(), l.get('Treino do Dia','').strip())
                   for l in logs if l.get('Treino do Dia','').strip()]

    if treinos_log:
        story.append(Paragraph(f'Total de sessoes de treino no mes: <b>{len(treinos_log)}</b>', styles['corpo']))
        story.append(Spacer(1, 0.2*cm))
        t_rows = [[Paragraph('<b>Data</b>', styles['label_card']),
                   Paragraph('<b>Treino</b>', styles['label_card'])]]
        for i, (dt, tr) in enumerate(sorted(treinos_log)):
            t_rows.append([
                Paragraph(dt, styles['corpo_small']),
                Paragraph(tr[:200] + ('...' if len(tr)>200 else ''), styles['corpo_small']),
            ])
        t_tr = Table(t_rows, colWidths=[2.8*cm, W-2.8*cm], repeatRows=1)
        tr_style = [
            ('BACKGROUND',    (0,0), (-1,0),  AZUL_ESCURO),
            ('TEXTCOLOR',     (0,0), (-1,0),  BRANCO),
            ('FONTNAME',      (0,0), (-1,0),  'Helvetica-Bold'),
            ('FONTSIZE',      (0,0), (-1,0),  8),
            ('BOX',           (0,0), (-1,-1), 0.5, CINZA_BORDA),
            ('INNERGRID',     (0,0), (-1,-1), 0.3, CINZA_BORDA),
            ('VALIGN',        (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING',    (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING',   (0,0), (-1,-1), 7),
        ]
        for i in range(1, len(t_rows)):
            if i % 2 == 1:
                tr_style.append(('BACKGROUND', (0,i), (-1,i), CINZA_CLARO))
        t_tr.setStyle(TableStyle(tr_style))
        story.append(t_tr)
    else:
        story.append(Paragraph('Nenhum treino registrado neste mes.', styles['corpo']))

    story.append(Spacer(1, 0.5*cm))

    # ── OBSERVAÇÕES / NOTAS ───────────────────────────────────────────────────
    obs_logs = [(l.get('Data','').split('—')[0].strip(), l.get('Observações do Dia','').strip())
                for l in logs if l.get('Observações do Dia','').strip()]
    if obs_logs:
        story += secao('Observacoes do Paciente', styles)
        for dt, obs in sorted(obs_logs):
            story.append(KeepTogether([
                Paragraph(f'<b>{dt}</b>', styles['subtitulo']),
                Paragraph(obs, styles['corpo']),
                Spacer(1, 0.1*cm),
            ]))
        story.append(Spacer(1, 0.3*cm))

    # ── HUMOR AO LONGO DO MES ─────────────────────────────────────────────────
    if humores:
        story += secao('Bem-estar e Energia', styles)
        humor_count = {}
        for h in humores:
            humor_count[h] = humor_count.get(h, 0) + 1

        humor_rows = [[
            Paragraph('<b>Humor</b>', styles['label_card']),
            Paragraph('<b>Dias</b>', styles['label_card']),
            Paragraph('<b>% do Mes</b>', styles['label_card']),
        ]]
        for h in ['😄 Ótimo','🙂 Bom','😐 Ok','😔 Cansado','😫 Péssimo']:
            n = humor_count.get(h, 0)
            if n > 0:
                bg, fg = humor_cor(h)
                humor_rows.append([
                    Paragraph(h, styles['corpo']),
                    Paragraph(str(n), styles['corpo']),
                    Paragraph(f'{round(n/len(humores)*100)}%', styles['corpo']),
                ])
        t_hum = Table(humor_rows, colWidths=[W*0.5, W*0.25, W*0.25])
        t_hum.setStyle(TableStyle([
            ('BACKGROUND',    (0,0), (-1,0),  AZUL_ESCURO),
            ('TEXTCOLOR',     (0,0), (-1,0),  BRANCO),
            ('FONTNAME',      (0,0), (-1,0),  'Helvetica-Bold'),
            ('FONTSIZE',      (0,0), (-1,0),  8),
            ('BOX',           (0,0), (-1,-1), 0.5, CINZA_BORDA),
            ('INNERGRID',     (0,0), (-1,-1), 0.3, CINZA_BORDA),
            ('TOPPADDING',    (0,0), (-1,-1), 7),
            ('BOTTOMPADDING', (0,0), (-1,-1), 7),
            ('LEFTPADDING',   (0,0), (-1,-1), 9),
        ]))
        story.append(t_hum)
        story.append(Spacer(1, 0.3*cm))

    # ── RODAPÉ FINAL ──────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.4*cm))
    story.append(HRFlowable(width='100%', thickness=0.5, color=CINZA_BORDA))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        f'Relatorio gerado automaticamente pelo sistema Bestie em {date.today().strftime("%d/%m/%Y")}. '
        f'Dados provenientes dos registros diarios de {mes_nome}/{ano}.',
        styles['corpo_small']
    ))

    # ── BUILD ─────────────────────────────────────────────────────────────────
    class CanvasMaker(BestieCanvas):
        def __init__(self, filename, **kwargs):
            super().__init__(filename, mes_ano=mes_ano, **kwargs)

    doc.build(story, canvasmaker=CanvasMaker)
    print(f'✅ Relatorio gerado: {output_path}')
    return output_path


# ── MODO DEMO (sem dados reais do Notion) ─────────────────────────────────────
def gerar_demo(mes, ano, output_path):
    """Gera um PDF de demonstracao com dados fictícios."""
    import random
    random.seed(42)
    dias = 31 if mes in [1,3,5,7,8,10,12] else 30 if mes in [4,6,9,11] else 28
    proteinas = ['150g frango', '150g tilapia', '150g carne vermelha', '150g hamburguer']
    carbos    = ['200g macarrao', '2 pao frances', '2 Rap10', '1 pao hamburguer']
    frutas    = ['100g banana', '190g uva', '240g morango', '200g melao']
    treinos   = ['Peito + Triceps — supino 4x12, fly 3x12, triceps corda 4x15',
                 'Costas + Biceps — puxada 4x12, remada 3x12, roscas 3x15',
                 'Pernas — agachamento 4x10, leg press 4x12, extensora 3x15',
                 'Ombro + Core — desenvolvimento 4x12, elevacao lateral 3x15, plancha',
                 'Full body — circuito 3x15 cada exercicio']
    humores   = ['😄 Ótimo','🙂 Bom','😐 Ok','😔 Cansado']
    pesos     = ['😄 Ótimo']*6 + ['🙂 Bom']*12 + ['😐 Ok']*6 + ['😔 Cansado']*4 + ['😫 Péssimo']*2

    logs = []
    for d in range(1, dias+1):
        dt = date(ano, mes, d)
        skip = random.random() < 0.12
        if skip: continue
        log = {
            'Data': f'{str(d).zfill(2)}/{str(mes).zfill(2)}/{ano} — {["Domingo","Segunda","Terca","Quarta","Quinta","Sexta","Sabado"][dt.weekday()+1 if dt.weekday()<6 else 0]}',
            'REF 1 — Café': f'2 ovos + {random.choice(carbos[:3])} + {random.choice(frutas)}',
            'REF 2 — Almoço': f'{random.choice(proteinas[:2])} + {random.choice(carbos)} + 30g queijo',
            'REF 3 — Pós-treino/Jantar': f'60g whey + 9g creatina + {random.choice(proteinas[1:])} + {random.choice(carbos[1:])}',
            'Horário REF 1': f'0{random.randint(7,9)}:{random.choice(["00","15","30","45"])}',
            'Horário REF 2': f'{random.randint(12,14)}:{random.choice(["00","15","30"])}',
            'Horário REF 3': f'1{random.randint(6,8)}:{random.choice(["00","15","30"])}',
            'Vitamina C': '__YES__' if random.random()>0.1 else '__NO__',
            'Ômega 3 (almoço)': '__YES__' if random.random()>0.15 else '__NO__',
            'Nevrix IM (semana)': '__YES__' if dt.weekday()==0 else '__NO__',
            'Mounjaro (quinzenal)': '__YES__' if d in [19, 2] else '__NO__',
            'Humor & Energia': random.choice(pesos),
            'Treino do Dia': random.choice(treinos) if random.random()>0.35 else '',
            'Observações do Dia': random.choice([
                'Treino bem produtivo hoje. Aumentei carga no supino.',
                'Senti um pouco de nausea apos o Mounjaro, passou rapido.',
                'Fome controlada o dia todo, plano 100%.',
                '', '', '', '',  # maioria sem obs
            ])
        }
        logs.append(log)
    gerar_relatorio(logs, mes, ano, output_path)


if __name__ == '__main__':
    if len(sys.argv) >= 4 and sys.argv[1] != 'demo':
        with open(sys.argv[1]) as f:
            logs = json.load(f)
        mes = int(sys.argv[2])
        ano = int(sys.argv[3])
        out = sys.argv[4] if len(sys.argv) > 4 else f'relatorio_bestie_{mes:02d}_{ano}.pdf'
        gerar_relatorio(logs, mes, ano, out)
    else:
        # Demo com dados fictícios
        mes = int(sys.argv[2]) if len(sys.argv) > 2 else datetime.now().month
        ano = int(sys.argv[3]) if len(sys.argv) > 3 else datetime.now().year
        out = f'/sessions/youthful-stoic-mendel/mnt/outputs/relatorio_bestie_DEMO_{mes:02d}_{ano}.pdf'
        gerar_demo(mes, ano, out)
