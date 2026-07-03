import csv
import os
from datetime import datetime

from reportlab.lib import colors

from reportlab.lib.pagesizes import letter

from reportlab.platypus import (

    SimpleDocTemplate,

    Paragraph,

    Spacer,

    Table,

    TableStyle

)

from reportlab.lib.styles import getSampleStyleSheet


BASE_DIR = os.path.dirname(

    os.path.dirname(

        os.path.dirname(

            os.path.abspath(__file__)

        )

    )

)

REPORT_DIR = os.path.join(

    BASE_DIR,

    "reports"

)

os.makedirs(

    REPORT_DIR,

    exist_ok=True

)


styles = getSampleStyleSheet()


def timestamp():

    return datetime.now().strftime(

        "%Y-%m-%d_%H-%M-%S"

    )


def report_paths():

    name = f"pixelops_report_{timestamp()}"

    pdf = os.path.join(

        REPORT_DIR,

        name + ".pdf"

    )

    csv_file = os.path.join(

        REPORT_DIR,

        name + ".csv"

    )

    return pdf, csv_file
# ============================================================
# PDF REPORT
# ============================================================

def generate_pdf(metrics, chaos_config, logs):

    pdf_path, csv_path = report_paths()

    doc = SimpleDocTemplate(

        pdf_path,

        pagesize=letter

    )

    story = []

    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------

    story.append(

        Paragraph(

            "<b><font size=22>PixelOps Report</font></b>",

            styles["Title"]

        )

    )

    story.append(

        Paragraph(

            datetime.now().strftime(

                "%d %B %Y  %H:%M:%S"

            ),

            styles["Normal"]

        )

    )

    story.append(

        Spacer(1, 20)

    )

    # --------------------------------------------------------
    # Metrics Summary
    # --------------------------------------------------------

    story.append(

        Paragraph(

            "<b>Simulation Summary</b>",

            styles["Heading2"]

        )

    )

    summary = [

        ["Metric", "Value"],

        [

            "System Status",

            metrics["system_status"]

        ],

        [

            "Boss Health",

            f'{metrics["health"]}%'

        ],

        [

            "Total Requests",

            metrics["total_requests"]

        ],

        [

            "Success Rate",

            f'{metrics["success_rate"]}%'

        ],

        [

            "Failures",

            metrics["failures"]

        ],

        [

            "Average Latency",

            f'{round(metrics["average_latency_ms"],2)} ms'

        ],

        [

            "Requests/sec",

            round(

                metrics["requests_per_second"],

                2

            )

        ]

    ]

    table = Table(summary)

    table.setStyle(

        TableStyle([

            ("BACKGROUND",

             (0,0),

             (-1,0),

             colors.darkblue),

            ("TEXTCOLOR",

             (0,0),

             (-1,0),

             colors.white),

            ("GRID",

             (0,0),

             (-1,-1),

             1,

             colors.grey),

            ("BACKGROUND",

             (0,1),

             (-1,-1),

             colors.beige),

            ("BOTTOMPADDING",

             (0,0),

             (-1,0),

             10),

            ("ALIGN",

             (0,0),

             (-1,-1),

             "CENTER")

        ])

    )

    story.append(table)

    story.append(

        Spacer(1,20)

    )

    # --------------------------------------------------------
    # Chaos Settings
    # --------------------------------------------------------

    story.append(

        Paragraph(

            "<b>Chaos Configuration</b>",

            styles["Heading2"]

        )

    )

    chaos_table = [

        ["Setting", "Value"],

        [

            "Failure Rate",

            chaos_config["failure_rate"]

        ],

        [

            "Minimum Latency",

            chaos_config["min_latency"]

        ],

        [

            "Maximum Latency",

            chaos_config["max_latency"]

        ],

        [

            "Retry Attempts",

            chaos_config["retry_attempts"]

        ],

        [

            "Rate Limit",

            chaos_config["rate_limit"]

        ]

    ]

    table = Table(

        chaos_table

    )

    table.setStyle(

        TableStyle([

            ("BACKGROUND",

             (0,0),

             (-1,0),

             colors.darkgreen),

            ("TEXTCOLOR",

             (0,0),

             (-1,0),

             colors.white),

            ("GRID",

             (0,0),

             (-1,-1),

             1,

             colors.grey),

            ("BACKGROUND",

             (0,1),

             (-1,-1),

             colors.whitesmoke),

            ("ALIGN",

             (0,0),

             (-1,-1),

             "CENTER")

        ])

    )

    story.append(table)

    story.append(

        Spacer(1,20)

    )
    # --------------------------------------------------------
    # Status Codes
    # --------------------------------------------------------

    story.append(

        Paragraph(

            "<b>Status Codes</b>",

            styles["Heading2"]

        )

    )

    codes = metrics.get(

        "status_codes",

        {}

    )

    code_table = [

        ["Code", "Count"],

        ["200", codes.get("200", 0)],

        ["429", codes.get("429", 0)],

        ["500", codes.get("500", 0)]

    ]

    table = Table(code_table)

    table.setStyle(

        TableStyle([

            ("BACKGROUND",(0,0),(-1,0),colors.darkred),

            ("TEXTCOLOR",(0,0),(-1,0),colors.white),

            ("GRID",(0,0),(-1,-1),1,colors.grey),

            ("BACKGROUND",(0,1),(-1,-1),colors.beige),

            ("ALIGN",(0,0),(-1,-1),"CENTER")

        ])

    )

    story.append(table)

    story.append(

        Spacer(1,20)

    )

    # --------------------------------------------------------
    # Recent Requests
    # --------------------------------------------------------

    story.append(

        Paragraph(

            "<b>Recent Requests</b>",

            styles["Heading2"]

        )

    )

    request_rows = [[

        "Time",

        "Endpoint",

        "Status",

        "Latency",

        "Attempts"

    ]]

    for log in logs[-20:]:

        request_rows.append([

            log.get("timestamp","")[11:19],

            log.get("endpoint",""),

            log.get("status",""),

            f'{log.get("latency_ms",0)} ms',

            log.get("attempts",1)

        ])

    table = Table(request_rows)

    table.setStyle(

        TableStyle([

            ("BACKGROUND",(0,0),(-1,0),colors.black),

            ("TEXTCOLOR",(0,0),(-1,0),colors.white),

            ("GRID",(0,0),(-1,-1),0.5,colors.grey),

            ("FONTSIZE",(0,0),(-1,-1),8),

            ("ALIGN",(0,0),(-1,-1),"CENTER")

        ])

    )

    story.append(table)

    # --------------------------------------------------------
    # Build PDF
    # --------------------------------------------------------

    doc.build(story)

    # --------------------------------------------------------
    # CSV Export
    # --------------------------------------------------------

    with open(

        csv_path,

        "w",

        newline="",

        encoding="utf-8"

    ) as csvfile:

        writer = csv.writer(csvfile)

        writer.writerow([

            "Timestamp",

            "Endpoint",

            "Status",

            "Latency(ms)",

            "Attempts"

        ])

        for log in logs:

            writer.writerow([

                log.get("timestamp",""),

                log.get("endpoint",""),

                log.get("status",""),

                log.get("latency_ms",0),

                log.get("attempts",1)

            ])

    return pdf_path, csv_path