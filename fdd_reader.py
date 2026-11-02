from pathlib import Path

from docx import Document
from openpyxl import load_workbook
from PyPDF2 import PdfReader


class FDDReader:

    def read_file(
        self,
        file_path
    ):

        file_path = Path(file_path)

        if not file_path.exists():

            raise FileNotFoundError(
                f"File not found: {file_path}"
            )

        suffix = file_path.suffix.lower()

        if suffix == ".docx":

            return self.read_docx(
                file_path
            )

        elif suffix == ".pdf":

            return self.read_pdf(
                file_path
            )

        elif suffix == ".xlsx":

            return self.read_excel(
                file_path
            )

        elif suffix == ".txt":

            return self.read_text(
                file_path
            )

        else:

            raise ValueError(
                f"Unsupported file type: {suffix}"
            )

    def read_docx(
        self,
        file_path
    ):

        document = Document(
            file_path
        )

        content = []

        for paragraph in document.paragraphs:

            text = paragraph.text.strip()

            if text:

                content.append(
                    text
                )

        return "\n".join(content)

    def read_pdf(
        self,
        file_path
    ):

        reader = PdfReader(
            str(file_path)
        )

        content = []

        for page in reader.pages:

            text = page.extract_text()

            if text:

                content.append(
                    text
                )

        return "\n".join(content)

    def read_excel(
        self,
        file_path
    ):

        workbook = load_workbook(
            file_path,
            data_only=True
        )

        content = []

        for sheet in workbook.worksheets:

            content.append(
                f"\n===== SHEET: {sheet.title} =====\n"
            )

            for row in sheet.iter_rows(
                values_only=True
            ):

                row_data = []

                for cell in row:

                    if cell is not None:

                        row_data.append(
                            str(cell)
                        )

                if row_data:

                    content.append(
                        " | ".join(
                            row_data
                        )
                    )

        return "\n".join(content)

    def read_text(
        self,
        file_path
    ):

        return file_path.read_text(
            encoding="utf-8"
        )