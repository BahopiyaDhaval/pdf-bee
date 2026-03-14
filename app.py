from flask import Flask, render_template, request, send_file
from pdf2image import convert_from_bytes
from PIL import Image
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from pdf2docx import Converter
from docx import Document
from reportlab.pdfgen import canvas
import os
import pikepdf

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


# PDF → IMAGE (DIRECT IMAGE DOWNLOAD)
@app.route("/pdf_to_image", methods=["POST"])
def pdf_to_image():

    file = request.files["pdf"]

    images = convert_from_bytes(file.read(), dpi=300)

    img_path = "page1.jpg"

    images[0].save(img_path, "JPEG", quality=95)

    return send_file(img_path, as_attachment=True)


# IMAGE → PDF
@app.route("/image_to_pdf", methods=["POST"])
def image_to_pdf():

    files = request.files.getlist("images")

    image_list = []

    for file in files:

        img = Image.open(file).convert("RGB")

        width, height = img.size
        a4_width = 2480
        new_height = int(a4_width * height / width)

        img = img.resize((a4_width, new_height))

        image_list.append(img)

    pdf_path = "output.pdf"

    image_list[0].save(
        pdf_path,
        save_all=True,
        append_images=image_list[1:]
    )

    return send_file(pdf_path, as_attachment=True)


# PDF MERGE
@app.route("/merge_pdf", methods=["POST"])
def merge_pdf():

    files = request.files.getlist("pdfs")

    merger = PdfMerger()

    for file in files:
        merger.append(file)

    output = "merged.pdf"

    merger.write(output)
    merger.close()

    return send_file(output, as_attachment=True)


# PDF SPLIT
@app.route("/split_pdf", methods=["POST"])
def split_pdf():

    file = request.files["pdf"]

    reader = PdfReader(file)
    writer = PdfWriter()

    writer.add_page(reader.pages[0])

    output = "split.pdf"

    with open(output, "wb") as f:
        writer.write(f)

    return send_file(output, as_attachment=True)


# PDF ROTATE
@app.route("/rotate_pdf", methods=["POST"])
def rotate_pdf():

    file = request.files["pdf"]

    reader = PdfReader(file)
    writer = PdfWriter()

    for page in reader.pages:
        page.rotate(90)
        writer.add_page(page)

    output = "rotated.pdf"

    with open(output, "wb") as f:
        writer.write(f)

    return send_file(output, as_attachment=True)


# PDF WATERMARK
@app.route("/watermark_pdf", methods=["POST"])
def watermark_pdf():

    file = request.files["pdf"]

    watermark_file = "watermark.pdf"

    c = canvas.Canvas(watermark_file)
    c.drawString(250, 500, "pdf.bee")
    c.save()

    reader = PdfReader(file)
    watermark = PdfReader(watermark_file)

    writer = PdfWriter()

    for page in reader.pages:
        page.merge_page(watermark.pages[0])
        writer.add_page(page)

    output = "watermarked.pdf"

    with open(output, "wb") as f:
        writer.write(f)

    return send_file(output, as_attachment=True)


# PDF COMPRESS
@app.route("/compress_pdf", methods=["POST"])
def compress_pdf():

    file = request.files["pdf"]

    input_pdf = "input.pdf"
    output_pdf = "compressed.pdf"

    file.save(input_pdf)

    with pikepdf.open(input_pdf) as pdf:
        pdf.save(output_pdf)

    return send_file(output_pdf, as_attachment=True)


# PDF UNLOCK
@app.route("/unlock_pdf", methods=["POST"])
def unlock_pdf():

    file = request.files["pdf"]

    input_pdf = "locked.pdf"
    output_pdf = "unlocked.pdf"

    file.save(input_pdf)

    with pikepdf.open(input_pdf) as pdf:
        pdf.save(output_pdf)

    return send_file(output_pdf, as_attachment=True)


# PDF → DOCX
@app.route("/pdf_to_doc", methods=["POST"])
def pdf_to_doc():

    file = request.files["pdfdoc"]

    pdf_path = "input.pdf"
    docx_path = "output.docx"

    file.save(pdf_path)

    cv = Converter(pdf_path)
    cv.convert(docx_path)
    cv.close()

    return send_file(docx_path, as_attachment=True)


# DOCX → PDF
@app.route("/doc_to_pdf", methods=["POST"])
def doc_to_pdf():

    file = request.files["docfile"]

    docx_path = "input.docx"
    pdf_path = "doc_output.pdf"

    file.save(docx_path)

    doc = Document(docx_path)

    c = canvas.Canvas(pdf_path)

    y = 800

    for para in doc.paragraphs:
        c.drawString(50, y, para.text)
        y -= 20

    c.save()

    return send_file(pdf_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)