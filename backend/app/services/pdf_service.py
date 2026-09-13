import io
import base64
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing, Circle, Line, String, Rect, Group
from app.models.case import Case
from app.services.risk_score_service import RiskScoreService

class PDFService:
    @staticmethod
    def generate_case_pdf(
        case: Case,
        risk_score_service: RiskScoreService | None = None,
        graph_image_base64: str | None = None
    ) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Custom Styles
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#0F172A"),
            fontName="Helvetica-Bold",
            spaceAfter=6
        )

        subtitle_style = ParagraphStyle(
            'SubTitleStyle',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#64748B"),
            spaceAfter=12
        )

        h2_style = ParagraphStyle(
            'H2Style',
            parent=styles['Heading2'],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#1E293B"),
            fontName="Helvetica-Bold",
            spaceBefore=14,
            spaceAfter=8
        )

        body_style = ParagraphStyle(
            'BodyStyle',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#334155")
        )

        caption_style = ParagraphStyle(
            'CaptionStyle',
            parent=styles['Normal'],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#64748B"),
            alignment=1, # Center
            spaceBefore=4
        )

        elements = []

        # Document Header
        elements.append(Paragraph("FRAUD INVESTIGATION CASE REPORT", title_style))
        elements.append(Paragraph(f"Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')} | Confidential Security Intelligence", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#3B82F6"), spaceAfter=15))

        # Overview Table
        overview_data = [
            [Paragraph("<b>Case ID:</b>", body_style), Paragraph(f"#{case.id}", body_style), Paragraph("<b>Severity:</b>", body_style), Paragraph(f"<font color='{'#EF4444' if case.severity in ['high', 'critical'] else '#F59E0B'}'><b>{case.severity.upper()}</b></font>", body_style)],
            [Paragraph("<b>Case Title:</b>", body_style), Paragraph(case.title, body_style), Paragraph("<b>Status:</b>", body_style), Paragraph(case.status.upper(), body_style)],
            [Paragraph("<b>Assigned User ID:</b>", body_style), Paragraph(str(case.assigned_to or "Unassigned"), body_style), Paragraph("<b>Created At:</b>", body_style), Paragraph(case.created_at.strftime('%Y-%m-%d %H:%M') if case.created_at else "N/A", body_style)]
        ]

        t_overview = Table(overview_data, colWidths=[90, 180, 70, 180])
        t_overview.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
            ('PADDING', (0,0), (-1,-1), 8),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0"))
        ]))
        elements.append(t_overview)
        elements.append(Spacer(1, 12))

        # Case Description
        elements.append(Paragraph("Case Summary & Details", h2_style))
        elements.append(Paragraph(case.description or "No description provided.", body_style))
        elements.append(Spacer(1, 12))

        # --- GRAPH VISUALIZATION SECTION ---
        elements.append(Paragraph("Transaction Graph Network Topology", h2_style))
        
        graph_embedded = False
        if graph_image_base64:
            try:
                # Strip base64 header if present
                clean_b64 = graph_image_base64
                if "," in clean_b64:
                    clean_b64 = clean_b64.split(",", 1)[1]
                
                image_data = base64.b64decode(clean_b64)
                image_stream = io.BytesIO(image_data)
                
                img = Image(image_stream, width=520, height=260)
                elements.append(img)
                elements.append(Paragraph("Figure 1.0: Cytoscape transaction network topology graph snapshot captured during investigation.", caption_style))
                elements.append(Spacer(1, 12))
                graph_embedded = True
            except Exception as e:
                print(f"Error embedding graph image: {e}")
                graph_embedded = False

        if not graph_embedded:
            # Fallback vector drawing of target network nodes & edges
            d = Drawing(520, 160)
            # Background
            d.add(Rect(0, 0, 520, 160, fillColor=colors.HexColor("#0F172A"), strokeColor=colors.HexColor("#334155"), strokeWidth=1, rx=8, ry=8))
            
            related_ids = case.related_account_ids or []
            target_id = related_ids[0] if related_ids else f"TARGET-{case.id}"
            
            # Central target node
            d.add(Circle(260, 80, 26, fillColor=colors.HexColor("#EC4899"), strokeColor=colors.white, strokeWidth=2))
            d.add(String(260, 76, target_id, fontSize=8, fontName="Helvetica-Bold", textAnchor="middle", fillColor=colors.white))
            
            # Counterparty nodes dynamically assigned from case related accounts
            other_ids = related_ids[1:] if len(related_ids) > 1 else []
            cp_positions = [
                (120, 120, "#3B82F6", True),
                (120, 40, "#3B82F6", False),
                (400, 120, "#10B981", False),
                (400, 40, "#10B981", True),
            ]
            
            for idx, (cx, cy, col, is_fraud) in enumerate(cp_positions):
                cp_id = other_ids[idx] if idx < len(other_ids) else f"CP-{idx+1}"
                # Edge line to center
                edge_col = colors.HexColor("#EF4444") if is_fraud else colors.HexColor("#475569")
                d.add(Line(cx, cy, 260, 80, strokeColor=edge_col, strokeWidth=2 if is_fraud else 1))
                # Node
                d.add(Circle(cx, cy, 18, fillColor=colors.HexColor(col), strokeColor=colors.white, strokeWidth=1))
                d.add(String(cx, cy - 3, cp_id, fontSize=7, fontName="Helvetica-Bold", textAnchor="middle", fillColor=colors.white))
            
            elements.append(d)
            elements.append(Paragraph("Figure 1.0: Vector topology schematic of linked target account network and transaction flows.", caption_style))
            elements.append(Spacer(1, 12))

        # Related Accounts Table & Risk Profiles
        elements.append(Paragraph("Linked Target Accounts & Risk Profiles", h2_style))
        accounts_data = [["Account ID", "Risk Score", "Risk Level", "Primary Factor"]]
        
        related_ids = case.related_account_ids or []
        if related_ids:
            for acc_id in related_ids:
                r_score = "N/A"
                r_level = "N/A"
                factor = "N/A"
                if risk_score_service:
                    try:
                        res = risk_score_service.calculate_risk_score(acc_id)
                        r_score = f"{res.risk_score}/100"
                        r_level = res.risk_level
                        factor = res.explainable_factors.get("known_fraud", "")
                    except Exception:
                        pass
                accounts_data.append([acc_id, r_score, r_level, factor])
        else:
            accounts_data.append(["No accounts linked", "-", "-", "-"])

        t_accounts = Table(accounts_data, colWidths=[130, 80, 80, 230])
        t_accounts.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E293B")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('PADDING', (0,0), (-1,-1), 6),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")])
        ]))
        elements.append(t_accounts)
        elements.append(Spacer(1, 12))

        elements.append(Paragraph("Attached Evidence", h2_style))
        evidence = case.evidence or []
        if evidence:
            evidence_data = [["Account", "Transaction", "Added By", "Evidence Note"]]
            for item in evidence:
                evidence_data.append([
                    item.get("account_id") or "-",
                    str(item.get("transaction_id") or "-"),
                    f"User #{item.get('added_by', '-')}",
                    Paragraph(item.get("note") or "No note", body_style)
                ])
            evidence_table = Table(evidence_data, colWidths=[110, 90, 90, 210])
            evidence_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F766E")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('PADDING', (0,0), (-1,-1), 6),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
                ('VALIGN', (0,0), (-1,-1), 'TOP')
            ]))
            elements.append(evidence_table)
        else:
            elements.append(Paragraph("No evidence attached to this case.", body_style))
        elements.append(Spacer(1, 12))

        # Investigation Notes / Audit Trail
        elements.append(Paragraph("Investigation Notes & Log", h2_style))
        notes = case.notes or []
        if notes:
            notes_data = [["User", "Timestamp", "Note Content"]]
            for n in notes:
                user_label = n.get("user_email") or f"User #{n.get('user_id')}"
                ts = n.get("timestamp", "")[:19].replace("T", " ")
                notes_data.append([user_label, ts, Paragraph(n.get("note", ""), body_style)])
            
            t_notes = Table(notes_data, colWidths=[120, 110, 290])
            t_notes.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#475569")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('PADDING', (0,0), (-1,-1), 6),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1"))
            ]))
            elements.append(t_notes)
        else:
            elements.append(Paragraph("No investigation notes added yet.", body_style))

        # Build Document
        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
