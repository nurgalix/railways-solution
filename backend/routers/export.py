"""
Export endpoints: CSV and PDF report generation.
"""

import csv
import io
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import get_db
from models.telemetry import TelemetryReading, AlertEvent

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/csv")
async def export_csv(
    minutes: int = Query(15, ge=1, le=1440),
    locomotive_id: str = Query("LOC-001"),
    db: AsyncSession = Depends(get_db),
):
    """Export telemetry data as CSV."""
    end = datetime.now(timezone.utc)
    start = end - timedelta(minutes=minutes)

    q = (
        select(TelemetryReading)
        .where(
            TelemetryReading.locomotive_id == locomotive_id,
            TelemetryReading.timestamp >= start,
            TelemetryReading.timestamp <= end,
        )
        .order_by(TelemetryReading.timestamp)
    )
    result = await db.execute(q)
    readings = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "timestamp", "locomotive_id",
        "speed", "fuel_level", "pressure", "temperature",
        "latitude", "longitude", "km_marker",
        "health_index", "health_category",
    ])

    # Data rows
    for r in readings:
        writer.writerow([
            r.timestamp.isoformat() if r.timestamp else "",
            r.locomotive_id,
            r.speed, r.fuel_level, r.pressure, r.temperature,
            r.latitude, r.longitude, r.km_marker,
            r.health_index, r.health_category,
        ])

    output.seek(0)
    filename = f"telemetry_{locomotive_id}_{start.strftime('%Y%m%d_%H%M')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/pdf")
async def export_pdf(
    minutes: int = Query(15, ge=1, le=1440),
    locomotive_id: str = Query("LOC-001"),
    db: AsyncSession = Depends(get_db),
):
    """Generate a PDF diagnostic report."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    )
    from reportlab.lib.styles import getSampleStyleSheet

    end = datetime.now(timezone.utc)
    start = end - timedelta(minutes=minutes)

    # Fetch telemetry
    q = (
        select(TelemetryReading)
        .where(
            TelemetryReading.locomotive_id == locomotive_id,
            TelemetryReading.timestamp >= start,
            TelemetryReading.timestamp <= end,
        )
        .order_by(TelemetryReading.timestamp)
    )
    result = await db.execute(q)
    readings = result.scalars().all()

    # Fetch alerts
    aq = (
        select(AlertEvent)
        .where(
            AlertEvent.locomotive_id == locomotive_id,
            AlertEvent.timestamp >= start,
            AlertEvent.timestamp <= end,
        )
        .order_by(AlertEvent.timestamp)
    )
    alert_result = await db.execute(aq)
    alerts = alert_result.scalars().all()

    # Build PDF
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph(
        f"Locomotive Diagnostic Report — {locomotive_id}",
        styles["Title"],
    ))
    elements.append(Spacer(1, 5 * mm))
    elements.append(Paragraph(
        f"Period: {start.strftime('%Y-%m-%d %H:%M')} — {end.strftime('%Y-%m-%d %H:%M')} UTC",
        styles["Normal"],
    ))
    elements.append(Paragraph(
        f"Total readings: {len(readings)} | Total alerts: {len(alerts)}",
        styles["Normal"],
    ))
    elements.append(Spacer(1, 10 * mm))

    # Summary statistics
    if readings:
        avg_health = sum(r.health_index or 0 for r in readings) / len(readings)
        min_health = min(r.health_index or 0 for r in readings)
        max_speed = max(r.speed for r in readings)
        avg_speed = sum(r.speed for r in readings) / len(readings)

        summary_data = [
            ["Metric", "Value"],
            ["Avg Health Index", f"{avg_health:.1f}"],
            ["Min Health Index", f"{min_health:.1f}"],
            ["Max Speed", f"{max_speed:.1f} km/h"],
            ["Avg Speed", f"{avg_speed:.1f} km/h"],
            ["Fuel Level (start)", f"{readings[0].fuel_level:.1f}%"],
            ["Fuel Level (end)", f"{readings[-1].fuel_level:.1f}%"],
        ]

        summary_table = Table(summary_data, colWidths=[60 * mm, 60 * mm])
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ]))
        elements.append(Paragraph("Summary", styles["Heading2"]))
        elements.append(summary_table)
        elements.append(Spacer(1, 10 * mm))

    # Alerts table
    if alerts:
        elements.append(Paragraph("Alerts", styles["Heading2"]))
        alert_data = [["Time", "Severity", "Code", "Message"]]
        for a in alerts[:30]:  # limit to 30 for PDF
            alert_data.append([
                a.timestamp.strftime("%H:%M:%S") if a.timestamp else "",
                a.severity,
                a.code,
                (a.message[:60] + "...") if len(a.message) > 60 else a.message,
            ])

        alert_table = Table(alert_data, colWidths=[25 * mm, 20 * mm, 40 * mm, 75 * mm])
        alert_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e94560")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("WORDWRAP", (0, 0), (-1, -1), True),
        ]))
        elements.append(alert_table)

    doc.build(elements)
    pdf_buffer.seek(0)

    filename = f"diagnostic_{locomotive_id}_{start.strftime('%Y%m%d_%H%M')}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
