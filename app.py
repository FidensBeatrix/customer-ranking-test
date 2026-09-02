#region IMPORTS

from io import BytesIO
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

import streamlit as st
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from PIL import Image, ImageDraw, ImageFont

#endregion IMPORTS


#region APP CONFIGURATION

APP_TITLE = "Customer Scoring - Web V15"

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "Customer_Scoring.xlsx"
ASSETS_DIR = BASE_DIR / "assets"

SPINMASTER_LOGO_PATH = ASSETS_DIR / "SpinMaster-Logo-CMYK.png"
PRIMAL_HATCH_IMAGE_PATH = ASSETS_DIR / "PrimalHatch_Jurassic_DinoFreedom-2025.png"
PAW_HEADER_IMAGE_PATH = ASSETS_DIR / "PAW_CSG25_Grp_005_CGI.jpg"

MAX_TOTAL = 15

MONTH_WEEK_MAPPING = {
    1:  [1, 2, 3, 4],
    2:  [5, 6, 7, 8],
    3:  [9, 10, 11, 12, 13],
    4:  [14, 15, 16, 17],
    5:  [18, 19, 20, 21],
    6:  [22, 23, 24, 25, 26],
    7:  [27, 28, 29, 30],
    8:  [31, 32, 33, 34],
    9:  [35, 36, 37, 38, 39],
    10: [40, 41, 42, 43],
    11: [44, 45, 46, 47],
    12: [48, 49, 50, 51, 52],
}

MONTH_LABELS = [
    "1 - January",
    "2 - February",
    "3 - March",
    "4 - April",
    "5 - May",
    "6 - June",
    "7 - July",
    "8 - August",
    "9 - September",
    "10 - October",
    "11 - November",
    "12 - December",
]

CATEGORIES = [
    (
        "Timeliness",
        "How reliably the customer sends the data on time.\n\n"
        "0 = Missing / seriously late\n"
        "1 = Often late\n"
        "2 = Mostly on time, minor delays\n"
        "3 = On time",
    ),
    (
        "Layout Consistency",
        "How stable and reusable the incoming file layout is.\n\n"
        "0 = Major layout changes / difficult to process\n"
        "1 = Frequent layout changes\n"
        "2 = Mostly consistent, small changes\n"
        "3 = Fully consistent",
    ),
    (
        "Data Completeness",
        "Whether the required POS / inventory / product information is present.\n\n"
        "0 = Major information missing\n"
        "1 = Several missing elements\n"
        "2 = Mostly complete, minor gaps\n"
        "3 = Complete",
    ),
    (
        "Material Mapping",
        "How cleanly customer materials can be matched to the correct #600.\n\n"
        "0 = Major mapping problems\n"
        "1 = Frequent manual mapping required\n"
        "2 = Minor mapping issues\n"
        "3 = Clean / accurate mapping",
    ),
    (
        "Manual Effort",
        "How much analyst work is needed before the data can be used.\n\n"
        "0 = Very high manual effort\n"
        "1 = High manual effort\n"
        "2 = Some manual work needed\n"
        "3 = Minimal manual effort",
    ),
]


DEFAULT_CUSTOMERS = {
    "UK": [
        "Amazon UK",
        "Argos",
        "ASDA",
        "B&M",
        "ENTERTAINER",
        "Sainsburys",
        "Smyths UK",
    ],

    "FR": [
        "Amazon FR",
        "Auchan FR",
        "Carrefour FR",
        "Cultura",
        "Distritoys",
        "Fnac FR",
        "Joueclub & Ludendo",
        "Leclerc",
        "Maxitoys",
        "Smyths FR",
    ],

    "GAS": [
        "Amazon DE",
        "Wave",
        "Karstad",
        "Kaufland",
        "Mueller",
        "Otto",
        "Rofu",
        "Rossmann",
        "Smyths DE",
        "Thalia",
        "Interspar",
        "Migros",
    ],

    "IBER": [
        "Amazon ES",
        "Alcampo",
        "Carrefour ES",
        "El Corte Ingles",
        "Fnac ES",
        "Toy Planet",
        "Toys r us",
        "El Corte Ingles Portugal",
        "Pingo Doce",
        "Sonae",
    ],

    "IT": [
        "Amazon IT",
        "Prenatal IT",
    ],

    "BNL": [
        "Amazon NL",
        "Amazon BE",
        "Bol.com",
        "LOBBES",
        "Intertoys",
        "Colruyt",
        "Dreamland",
        "Wehkamp",
    ],

    "GR": [
        "Enarxis",
        "Jumbo",
        "Max Stores",
        "Moustakas",
        "Perfect Toys",
        "Retail World",
    ],

    "CEE": [
        "Auchan HU",
        "Modell & Hobby",
        "Regio",
        "Spar",
        "Carrefour PL",
        "Amazon PL",
        "Smyk",
        "Auchan RO",
        "Carrefour RO",
        "Noriel/Intertoy",
        "Peaktoys",
        "Allegro",
        "Alza",
        "Sparkys",
        "Alltoys",
        "Framee",
        "TESCO CEE",
    ],

    "NORDICS": [
        "Lekia",
        "SG",
    ],
}


DEFAULT_FREQUENCY = "Weekly"

MONTHLY_CUSTOMERS = {
    "Cultura",
    "Carrefour FR",
    "Leclerc",
    "Interspar",
    "Kaufland",
    "Modell & Hobby",
    "Carrefour PL",
    "Auchan RO",
    "Carrefour RO",
    "Noriel/Intertoy",
    "Peaktoys",
}


CATEGORY_COLORS = {
    "Timeliness": "#20a8f0",
    "Layout Consistency": "#f04a34",
    "Data Completeness": "#9a5de8",
    "Material Mapping": "#79c934",
    "Manual Effort": "#f39a22",
}

#endregion APP CONFIGURATION


#region REPORTING HELPERS


def parse_month_value(value):
    text = str(value or "").strip()

    if not text:
        raise ValueError("Month is empty.")

    month = int(text.split("-", 1)[0].strip())

    if month not in MONTH_WEEK_MAPPING:
        raise ValueError("Month must be between 1 and 12.")

    return month


def weeks_for_month(month):
    return list(MONTH_WEEK_MAPPING[month])


def month_for_week(week):

    for month, weeks in MONTH_WEEK_MAPPING.items():

        if week in weeks:
            return month

    return 12


def get_customer_frequency(region, customer):

    if region == "GR":
        return "Monthly"

    if customer in MONTHLY_CUSTOMERS:
        return "Monthly"

    return "Weekly"


def parse_custom_weeks(year, text):

    text = (text or "").strip()

    if not text:
        return []

    weeks = []

    for part in text.split(","):

        part = part.strip()

        if not part:
            continue

        if "-" in part:

            a, b = part.split("-", 1)

            start_week = int(a.strip())
            end_week = int(b.strip())

            if start_week > end_week:
                start_week, end_week = end_week, start_week

            for week in range(start_week, end_week + 1):

                datetime.fromisocalendar(
                    year,
                    week,
                    1,
                )

                weeks.append(week)

        else:

            week = int(part)

            datetime.fromisocalendar(
                year,
                week,
                1,
            )

            weeks.append(week)

    return [
        (year, week)
        for week in sorted(set(weeks))
    ]


#endregion REPORTING HELPERS


#region EXCEL DATABASE


def format_workbook(wb):

    header_fill = PatternFill(
        "solid",
        fgColor="243447",
    )

    header_font = Font(
        color="FFFFFF",
        bold=True,
    )

    for ws in wb.worksheets:

        for cell in ws[1]:

            cell.fill = header_fill
            cell.font = header_font

            cell.alignment = Alignment(
                horizontal="center",
            )

        ws.freeze_panes = "A2"

        for column in range(
            1,
            ws.max_column + 1,
        ):

            max_length = 0

            for row in range(
                1,
                ws.max_row + 1,
            ):

                value = ws.cell(
                    row,
                    column,
                ).value

                if value is not None:

                    max_length = max(
                        max_length,
                        len(str(value)),
                    )

            ws.column_dimensions[
                get_column_letter(column)
            ].width = min(
                max(max_length + 2, 11),
                30,
            )


def ensure_workbook():

    if DATA_FILE.exists():

        sync_customer_master()
        return

    wb = Workbook()

    ws = wb.active
    ws.title = "Scores"

    ws.append([
        "Year",
        "Week",
        "Region",
        "Customer",
        "Frequency",
        "Timeliness",
        "Layout Consistency",
        "Data Completeness",
        "Material Mapping",
        "Manual Effort",
        "Total",
        "Life %",
        "Saved At",
    ])

    customers_ws = wb.create_sheet(
        "Customers"
    )

    customers_ws.append([
        "Region",
        "Customer",
        "Frequency",
    ])

    for region, customers in DEFAULT_CUSTOMERS.items():

        for customer in customers:

            customers_ws.append([
                region,
                customer,
                get_customer_frequency(
                    region,
                    customer,
                ),
            ])

    format_workbook(wb)

    wb.save(DATA_FILE)
    wb.close()


def sync_customer_master():

    if not DATA_FILE.exists():
        return

    wb = load_workbook(DATA_FILE)

    if "Customers" not in wb.sheetnames:

        ws = wb.create_sheet(
            "Customers"
        )

        ws.append([
            "Region",
            "Customer",
            "Frequency",
        ])

    else:

        ws = wb["Customers"]

    if ws.cell(1, 3).value != "Frequency":

        ws.cell(
            1,
            3,
        ).value = "Frequency"

    existing = {}

    for row_index in range(
        2,
        ws.max_row + 1,
    ):

        region = ws.cell(
            row_index,
            1,
        ).value

        customer = ws.cell(
            row_index,
            2,
        ).value

        if region and customer:

            region = str(region)
            customer = str(customer)

            existing[
                (region, customer)
            ] = row_index

            ws.cell(
                row_index,
                3,
            ).value = get_customer_frequency(
                region,
                customer,
            )

    for region, customers in DEFAULT_CUSTOMERS.items():

        for customer in customers:

            if (
                region,
                customer,
            ) not in existing:

                ws.append([
                    region,
                    customer,
                    get_customer_frequency(
                        region,
                        customer,
                    ),
                ])

    format_workbook(wb)

    wb.save(DATA_FILE)
    wb.close()


def replace_data_file(uploaded_file):

    DATA_FILE.write_bytes(
        uploaded_file.getvalue()
    )

    ensure_workbook()


def load_customer_master():

    ensure_workbook()

    wb = load_workbook(
        DATA_FILE,
        data_only=True,
    )

    ws = wb["Customers"]

    data = defaultdict(list)

    for row in ws.iter_rows(
        min_row=2,
        values_only=True,
    ):

        region = row[0]
        customer = row[1]

        if not region or not customer:
            continue

        region = str(region)
        customer = str(customer)

        data[region].append({
            "customer": customer,

            "frequency":
                get_customer_frequency(
                    region,
                    customer,
                ),
        })

    wb.close()

    return dict(data)


def get_saved_customers_for_period(
    year,
    weeks,
):

    ensure_workbook()

    if isinstance(weeks, int):
        weeks = [weeks]

    weeks = set(weeks)

    wb = load_workbook(
        DATA_FILE,
        data_only=True,
    )

    ws = wb["Scores"]

    saved_by_customer = defaultdict(set)

    for row in ws.iter_rows(
        min_row=2,
        values_only=True,
    ):

        if not row:
            continue

        if row[0] is None:
            continue

        row_year = row[0]
        row_week = row[1]
        customer = row[3]

        if (
            row_year == year
            and row_week in weeks
            and customer
        ):

            saved_by_customer[
                str(customer)
            ].add(
                int(row_week)
            )

    wb.close()

    return {
        customer

        for customer, saved_weeks
        in saved_by_customer.items()

        if weeks.issubset(
            saved_weeks
        )
    }


def get_last_saved_period():

    ensure_workbook()

    wb = load_workbook(
        DATA_FILE,
        data_only=True,
    )

    ws = wb["Scores"]

    periods = []

    for row in ws.iter_rows(
        min_row=2,
        values_only=True,
    ):

        if (
            isinstance(row[0], int)
            and isinstance(row[1], int)
        ):

            periods.append(
                (
                    row[0],
                    row[1],
                )
            )

    wb.close()

    if periods:

        return max(
            periods,

            key=lambda period:
                datetime.fromisocalendar(
                    period[0],
                    period[1],
                    1,
                ),
        )

    reporting_date = (
        datetime.now()
        - timedelta(weeks=1)
    )

    iso = reporting_date.isocalendar()

    return (
        iso.year,
        iso.week,
    )


def migrate_old_scores_if_needed(wb):

    ws = wb["Scores"]

    headers = [
        ws.cell(
            1,
            column,
        ).value

        for column in range(
            1,
            ws.max_column + 1,
        )
    ]

    if "Frequency" in headers:
        return

    old_rows = list(
        ws.iter_rows(
            min_row=2,
            values_only=True,
        )
    )

    old_index = wb.sheetnames.index(
        "Scores"
    )

    wb.remove(ws)

    new_ws = wb.create_sheet(
        "Scores",
        old_index,
    )

    new_ws.append([
        "Year",
        "Week",
        "Region",
        "Customer",
        "Frequency",
        "Timeliness",
        "Layout Consistency",
        "Data Completeness",
        "Material Mapping",
        "Manual Effort",
        "Total",
        "Life %",
        "Saved At",
    ])

    for row in old_rows:

        if not row:
            continue

        if row[0] is None:
            continue

        region = str(row[2])
        customer = str(row[3])

        frequency = get_customer_frequency(
            region,
            customer,
        )

        new_ws.append([
            row[0],
            row[1],
            row[2],
            row[3],
            frequency,
            row[4],
            row[5],
            row[6],
            row[7],
            row[8],
            row[9],
            row[10],
            row[11],
        ])


def save_batch_to_excel(
    batch,
    year,
    week,
):

    ensure_workbook()

    wb = load_workbook(
        DATA_FILE
    )

    migrate_old_scores_if_needed(
        wb
    )

    ws = wb["Scores"]

    existing = {}

    for row_number in range(
        2,
        ws.max_row + 1,
    ):

        row_year = ws.cell(
            row_number,
            1,
        ).value

        row_week = ws.cell(
            row_number,
            2,
        ).value

        customer = ws.cell(
            row_number,
            4,
        ).value

        if (
            row_year is not None
            and row_week is not None
            and customer
        ):

            existing[
                (
                    int(row_year),
                    int(row_week),
                    str(customer),
                )
            ] = row_number

    saved_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    for customer, item in batch.items():

        scores = item["scores"]

        total = sum(
            scores.values()
        )

        values = [
            year,
            week,
            item["region"],
            customer,
            item["frequency"],
            scores["Timeliness"],
            scores["Layout Consistency"],
            scores["Data Completeness"],
            scores["Material Mapping"],
            scores["Manual Effort"],
            total,
            total / MAX_TOTAL,
            saved_at,
        ]

        key = (
            year,
            week,
            customer,
        )

        if key in existing:

            row_number = existing[key]

            for column, value in enumerate(
                values,
                start=1,
            ):

                ws.cell(
                    row_number,
                    column,
                ).value = value

        else:

            ws.append(values)

    for row_number in range(
        2,
        ws.max_row + 1,
    ):

        ws.cell(
            row_number,
            12,
        ).number_format = "0%"

    format_workbook(wb)

    wb.save(DATA_FILE)
    wb.close()


def load_all_scores():

    ensure_workbook()

    wb = load_workbook(
        DATA_FILE,
        data_only=True,
    )

    ws = wb["Scores"]

    headers = [
        ws.cell(
            1,
            column,
        ).value

        for column in range(
            1,
            ws.max_column + 1,
        )
    ]

    has_frequency = (
        "Frequency" in headers
    )

    records = []

    for row in ws.iter_rows(
        min_row=2,
        values_only=True,
    ):

        if not row:
            continue

        if row[0] is None:
            continue

        if has_frequency:

            frequency = (
                row[4]
                or DEFAULT_FREQUENCY
            )

            offset = 1

        else:

            frequency = (
                get_customer_frequency(
                    str(row[2]),
                    str(row[3]),
                )
            )

            offset = 0

        records.append({
            "year": row[0],
            "week": row[1],
            "region": row[2],
            "customer": row[3],
            "frequency": str(
                frequency
            ).title(),

            "scores": {
                "Timeliness":
                    row[4 + offset],

                "Layout Consistency":
                    row[5 + offset],

                "Data Completeness":
                    row[6 + offset],

                "Material Mapping":
                    row[7 + offset],

                "Manual Effort":
                    row[8 + offset],
            },

            "total":
                row[9 + offset],

            "life":
                row[10 + offset],
        })

    wb.close()

    return records


def workbook_bytes():

    ensure_workbook()

    return DATA_FILE.read_bytes()


#endregion EXCEL DATABASE
