import io
import re
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional

try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import pymupdf
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False

try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


class DocumentProcessor:
    """
    Module 1: Document Processing Pipeline
    Ingests and parses PDF, DOCX, and text documents.
    Performs noise filtering, header/footer removal, and structured chunk extraction
    (units, topics, questions, sub-questions, marks allocations).
    """

    HEADER_FOOTER_PATTERNS = [
        r"page\s+\d+(\s+of\s+\d+)?",
        r"confidential\s*-?\s*for\s+internal\s+use\s+only",
        r"copyright\s+.*",
        r"all\s+rights\s+reserved",
        r"printed\s+on\s+.*",
        r"time:\s*\d+\s*(hours?|hrs?)",
        r"max(\.|imum)?\s*marks?:\s*\d+",
        r"instructions\s+to\s+candidates?:?",
        r"seat\s+no(\.)?:?\s*\[?\s*\]?",
        r"v(ishwakarma)?\s*i(nstitute)?\s*of\s*t(echnology)?.*"
    ]

    QUESTION_HEADER_REGEX = re.compile(
        r"^(?:(?:Q|Question)\s*(\d+)[\.:\)]?|(?:\[?(\d+)\]?[\.:\)]))\s*(.*)",
        re.IGNORECASE
    )

    SUB_QUESTION_REGEX = re.compile(
        r"^(?:\(([a-z]|[ivx]+)\)|([a-z]|[ivx]+)\))\s*(.*)",
        re.IGNORECASE
    )

    MARKS_REGEX = re.compile(
        r"(?:\[|\()?(\d+)\s*(?:marks?|m)(?:\]|\))?",
        re.IGNORECASE
    )
    TABLE_MARKS_REGEX = re.compile(r"\[\s*(\d+)\s*\]|\(\s*(\d+)\s*\)")

    UNIT_REGEX = re.compile(
        r"(?:Unit|Module|Section)\s*[-:]?\s*(\d+)[\s:\.-]+([^\n\r]+)",
        re.IGNORECASE
    )

    MAIN_QUESTION_REGEX = re.compile(
        r"^(?:Q\.?\s*)?(?:QUESTION\s*)?(\d+)\s*[\.:\)]\s*(.*)$",
        re.IGNORECASE,
    )
    OCR_SUB_QUESTION_REGEX = re.compile(
        r"^([a-z]|[ivx]+)\)\s*(.*)$",
        re.IGNORECASE,
    )
    TABLE_ROW_REGEX = re.compile(
        r"^Q\.?\s*(\d+)\s*\|\s*([a-z])\)\s*(.*)$",
        re.IGNORECASE,
    )

    def extract_text_from_pdf(self, file_bytes: bytes) -> str:
        """Extracts searchable text and OCRs scanned or low-text PDF pages."""
        if FITZ_AVAILABLE:
            try:
                doc = pymupdf.open(stream=file_bytes, filetype="pdf")
                extracted_pages = []
                for page in doc:
                    searchable = page.get_text("text").strip()
                    if len(searchable) >= 100:
                        extracted_pages.append(searchable)
                    elif OCR_AVAILABLE:
                        pix = page.get_pixmap(matrix=pymupdf.Matrix(2.5, 2.5), alpha=False)
                        image = Image.open(io.BytesIO(pix.tobytes("png"))).convert("L")
                        ocr_text = pytesseract.image_to_string(
                            image,
                            lang="eng",
                            config="--psm 6 --oem 3",
                        )
                        extracted_pages.append(ocr_text)
                    else:
                        extracted_pages.append(searchable)
                combined = "\n\n".join(extracted_pages).strip()
                if len(combined) >= 100:
                    return combined
            except Exception as e:
                print(f"[DocumentProcessor] PDF page extraction error: {e}")

        if PYPDF_AVAILABLE:
            try:
                reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                text_pages = []
                for p in reader.pages:
                    extracted = p.extract_text()
                    if extracted:
                        text_pages.append(extracted)
                if text_pages:
                    searchable = "\n\n".join(text_pages)
                    if len(searchable.strip()) >= 100:
                        return searchable
            except Exception as e:
                print(f"[DocumentProcessor] PyPDF extraction error: {e}")

        if FITZ_AVAILABLE and OCR_AVAILABLE:
            try:
                doc = pymupdf.open(stream=file_bytes, filetype="pdf")
                ocr_pages = []
                for page in doc:
                    searchable = page.get_text("text")
                    if len(searchable.strip()) >= 100:
                        ocr_pages.append(searchable)
                        continue
                    pix = page.get_pixmap(matrix=pymupdf.Matrix(2.5, 2.5), alpha=False)
                    image = Image.open(io.BytesIO(pix.tobytes("png"))).convert("L")
                    text = pytesseract.image_to_string(
                        image,
                        lang="eng",
                        config="--psm 6 --oem 3",
                    )
                    ocr_pages.append(text)
                if ocr_pages:
                    return "\n\n".join(ocr_pages)
            except Exception as e:
                print(f"[DocumentProcessor] OCR extraction error: {e}")
        
        # Fallback simple stream text extraction
        try:
            raw = file_bytes.decode('utf-8', errors='ignore')
            clean = "".join([c for c in raw if c.isprintable() or c in '\n\r\t'])
            return clean
        except Exception:
            return ""

    def extract_text_from_docx(self, file_bytes: bytes) -> str:
        """Extracts text from DOCX using python-docx or native XML zip unpacker."""
        if DOCX_AVAILABLE:
            try:
                doc = docx.Document(io.BytesIO(file_bytes))
                paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
                return "\n".join(paragraphs)
            except Exception as e:
                print(f"[DocumentProcessor] python-docx read error: {e}")

        # Native zipfile + XML fallback (100% dependency-free)
        try:
            with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
                xml_content = z.read("word/document.xml")
                tree = ET.fromstring(xml_content)
                paragraphs = []
                for p in tree.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"):
                    texts = [
                        node.text for node in p.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t")
                        if node.text
                    ]
                    if texts:
                        paragraphs.append("".join(texts).strip())
                return "\n".join(paragraphs)
        except Exception as e:
            print(f"[DocumentProcessor] Native docx parsing error: {e}")
            return ""

    def clean_text(self, text: str) -> str:
        """Removes headers, footers, consecutive blank lines and administrative notices."""
        lines = text.splitlines()
        cleaned_lines = []
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
            
            # Check against noisy patterns
            is_noise = False
            for pattern in self.HEADER_FOOTER_PATTERNS:
                if re.fullmatch(pattern, line_str, re.IGNORECASE):
                    is_noise = True
                    break
            if not is_noise:
                cleaned_lines.append(line_str)
                
        return "\n".join(cleaned_lines)

    def parse_syllabus(self, text: str) -> List[Dict[str, Any]]:
        """
        Parses structured syllabus modules, units, topics and outcomes.
        Returns list of structured unit dictionaries.
        """
        cleaned = self.clean_text(text)
        units = []
        current_unit = None
        
        lines = cleaned.splitlines()
        for line in lines:
            unit_match = self.UNIT_REGEX.search(line)
            if unit_match:
                if current_unit:
                    units.append(current_unit)
                unit_num = int(unit_match.group(1))
                unit_title = unit_match.group(2).strip()
                current_unit = {
                    "unit_number": unit_num,
                    "title": unit_title,
                    "topics": [],
                    "description": ""
                }
            elif current_unit:
                # Sub-topics or comma-delimited concept lists
                sub_parts = re.split(r'[,;•\t\n]+', line)
                for part in sub_parts:
                    p = part.strip()
                    if len(p) > 3 and not re.match(r'^(unit|module)\s*\d+', p, re.I):
                        current_unit["topics"].append({
                            "name": p,
                            "keywords": p.lower(),
                            "learning_outcome": f"Demonstrate mastery of {p}"
                        })

        if current_unit:
            units.append(current_unit)
            
        # Default fallback if no explicit "Unit X" format found
        if not units and cleaned:
            units.append({
                "unit_number": 1,
                "title": "Core Module Concepts",
                "topics": [{"name": t.strip(), "keywords": t.strip().lower(), "learning_outcome": "Demonstrate understanding"} 
                           for t in cleaned.splitlines()[:10] if len(t.strip()) > 5],
                "description": cleaned[:300]
            })
            
        return units

    def parse_historical_paper(self, text: str) -> List[Dict[str, Any]]:
        """
        Extracts individual questions, sub-questions, and associated marks
        from past exam papers.
        """
        cleaned = self.clean_text(text)
        questions = []
        current_main = None
        current_sub = None
        current_text = []
        current_marks = 5
        current_co = None
        current_bt = None

        def flush_question():
            nonlocal current_text, current_marks
            text_value = " ".join(current_text).strip()
            text_value = re.sub(r"\[\s*\d+\s*\]|\(\s*\d+\s*\)", "", text_value)
            text_value = re.sub(r"\s+", " ", text_value).strip()
            if len(text_value) >= 8:
                questions.append({
                    "text": text_value,
                    "marks": max(1, min(current_marks, 25)),
                    "sub_label": f"Q{current_main}{current_sub or ''}" if current_main else "Q",
                    "co_mapping": current_co,
                    "bt_level": current_bt,
                })

        for raw_line in cleaned.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            if re.match(r"^(?:\(\*\)|\d+\)|[*]\))?\s*(?:Instructions to candidates|Figures to the right|Use of scientific|Use suitable|All questions are compulsory|Max\.? Marks|Time:|Course Name|COURSE NAME|Branch|PAPER CODE|PRN No|Notes:|BT LEVELS)", line, re.I):
                continue
            if re.search(r"\bQuestion Description\b.*\bMarks\b.*\b(?:CO|BT)\b", line, re.I):
                continue

            table_match = self.TABLE_ROW_REGEX.match(line)
            if table_match:
                flush_question()
                current_main = table_match.group(1)
                current_sub = f"({table_match.group(2).lower()})"
                current_text = [table_match.group(3).strip()]
                current_marks = 5
                table_marks = self.TABLE_MARKS_REGEX.search(line)
                if table_marks:
                    current_marks = int(table_marks.group(1) or table_marks.group(2))
                continue

            main_match = self.MAIN_QUESTION_REGEX.match(line)
            sub_match = self.OCR_SUB_QUESTION_REGEX.match(line)

            if main_match:
                flush_question()
                current_main = main_match.group(1)
                current_sub = None
                current_text = [main_match.group(2).strip()] if main_match.group(2).strip() else []
                current_marks = 5
            elif sub_match:
                flush_question()
                current_sub = f"({sub_match.group(1).lower()})"
                current_text = [sub_match.group(2).strip()]
                current_marks = 5
            elif current_main or current_sub:
                current_text.append(line)

            if current_main or current_sub:
                table_marks = self.TABLE_MARKS_REGEX.search(line)
                if table_marks:
                    current_marks = int(table_marks.group(1) or table_marks.group(2))
                plain_marks = self.MARKS_REGEX.search(line)
                if plain_marks:
                    current_marks = int(plain_marks.group(1))
                co_match = re.search(r"\b(?:CO|CO\s*mapped)\s*(?:[:|-]?\s*)\{?(\d+)\}?|\[\s*(\d+)\s*\]", line, re.I)
                bt_match = re.search(r"(?:BT|Bloom(?:'s)?(?:\s*Level)?)[^0-6]*([1-6])", line, re.I)
                if co_match:
                    current_co = co_match.group(1) or co_match.group(2)
                if bt_match:
                    current_bt = f"L{bt_match.group(1)}"

        flush_question()
        return questions

    def parse_exam_template(self, text: str) -> Dict[str, Any]:
        """Extracts an editable template blueprint from ordinary or OCR text."""
        cleaned = self.clean_text(text)
        lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
        title = ""
        duration = 180
        total_marks = 100

        title_match = next(
            (line for line in lines if re.search(r"\b(?:EXAM|SEMESTER|MID|ENDSEM)\b", line, re.I)),
            "",
        )
        if title_match:
            title = title_match.strip()

        duration_match = re.search(r"(?:Time|Duration)[^\d]*(\d+)\s*(?:Hr|Hour|Hrs|Hours)?(?:\s*[:.]?\s*(\d+)\s*(?:Min|Minute|Minutes)?)?", cleaned, re.I)
        if duration_match:
            hours = int(duration_match.group(1))
            minutes = int(duration_match.group(2) or 0)
            duration = hours * 60 + minutes
            if duration == 0:
                duration = 180
        marks_match = re.search(r"(?:Max(?:imum)?\.?\s*Marks?|Total\s*Marks?)\s*[:=]?\s*\[?\s*(\d+)\s*\]?", cleaned, re.I)
        if marks_match:
            total_marks = int(marks_match.group(1))

        sections = []
        section_pattern = re.compile(r"^(?:Section\s+([A-Z]|[1-9]\d*)|Question\s*(?:No\.?|#)\s*([1-9]\d*))", re.I)
        section_marks = re.compile(r"(?:section\s*)?(?:marks?|m)\s*[:=]?\s*(\d+)", re.I)
        for line in lines:
            sec_match = section_pattern.search(line)
            if sec_match:
                section_key = sec_match.group(1) or sec_match.group(2)
                sec_name = f"Section {str(section_key).upper()}"
                marks_in_line = section_marks.search(line)
                sections.append({
                    "section_name": sec_name,
                    "marks": int(marks_in_line.group(1)) if marks_in_line else 0,
                    "instructions": "Answer according to the examination instructions.",
                })
        if not sections:
            sections = [{"section_name": "Section A", "marks": total_marks, "instructions": "Answer all questions as directed."}]

        bloom_targets = {"L1": 10.0, "L2": 20.0, "L3": 30.0, "L4": 25.0, "L5": 10.0, "L6": 5.0}
        bt_levels = re.findall(r"\b([1-6])\b", cleaned)
        if bt_levels:
            counts = {str(level): bt_levels.count(str(level)) for level in range(1, 7)}
            total = sum(counts.values()) or 1
            bloom_targets = {
                f"L{level}": round(counts[str(level)] * 100.0 / total, 2)
                for level in range(1, 7)
            }

        return {
            "name": title or "Extracted Examination Template",
            "description": "Template extracted and awaiting faculty review.",
            "total_marks": total_marks,
            "duration_minutes": duration,
            "instructions": "Figures to the right indicate full marks.",
            "sections_config": sections,
            "bloom_targets": bloom_targets,
            "difficulty_targets": {"Easy": 30.0, "Medium": 50.0, "Hard": 20.0},
        }

    def process_file(self, filename: str, file_bytes: bytes, doc_type: str = "syllabus") -> Dict[str, Any]:
        """
        Orchestrates ingestion, text extraction, cleaning, and structured parsing.
        """
        ext = filename.lower().split(".")[-1]
        raw_text = ""
        if ext == "pdf":
            raw_text = self.extract_text_from_pdf(file_bytes)
        elif ext in ["docx", "doc"]:
            raw_text = self.extract_text_from_docx(file_bytes)
        else:
            raw_text = file_bytes.decode("utf-8", errors="ignore")

        cleaned = self.clean_text(raw_text)

        if doc_type == "syllabus":
            units = self.parse_syllabus(cleaned)
            return {
                "doc_type": "syllabus",
                "raw_length": len(raw_text),
                "cleaned_length": len(cleaned),
                "units_count": len(units),
                "extracted_data": units
            }
        elif doc_type in ["past_paper", "historical_paper"]:
            questions = self.parse_historical_paper(cleaned)
            return {
                "doc_type": "past_paper",
                "raw_length": len(raw_text),
                "cleaned_length": len(cleaned),
                "questions_count": len(questions),
                "extracted_data": questions
            }
        elif doc_type in ["exam_template", "template"]:
            template = self.parse_exam_template(cleaned)
            return {
                "doc_type": "exam_template",
                "raw_length": len(raw_text),
                "cleaned_length": len(cleaned),
                "extracted_data": [template],
                "template": template,
            }
        else:
            return {
                "doc_type": doc_type,
                "raw_length": len(raw_text),
                "cleaned_length": len(cleaned),
                "extracted_text": cleaned
            }

doc_processor = DocumentProcessor()
