from flask import Flask, render_template, request, send_file
from pdf2image import convert_from_bytes
from PIL import Image
from pdf2docx import Converter
from docx import Document
from reportlab.pdfgen import canvas
from PyPDF2 import PdfMerger, PdfReader, PdfWriter

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


# PDF → IMAGE
@app.route("/pdf_to_image", methods=["POST"])
def pdf_to_image():

    file = request.files.get("pdf")

    if not file or not file.filename.lower().endswith(".pdf"):
        return "❌ Upload PDF only"

    images = convert_from_bytes(file.read(), dpi=300)

    img_path = "page1.jpg"
    images[0].save(img_path, "JPEG")

    return send_file(img_path, as_attachment=True)


# IMAGE → PDF
@app.route("/image_to_pdf", methods=["POST"])
def image_to_pdf():

    files = request.files.getlist("images")

    image_list = []

    for file in files:

        if not file.filename.lower().endswith((".png",".jpg",".jpeg")):
            return "❌ Upload images only"

        img = Image.open(file).convert("RGB")
        image_list.append(img)

    pdf_path = "output.pdf"

    image_list[0].save(
        pdf_path,
        save_all=True,
        append_images=image_list[1:]
    )

    return send_file(pdf_path, as_attachment=True)


# PDF → DOCX
@app.route("/pdf_to_doc", methods=["POST"])
def pdf_to_doc():

    file = request.files.get("pdfdoc")

    if not file.filename.lower().endswith(".pdf"):
        return "❌ Upload PDF only"

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

    file = request.files.get("docfile")

    if not file.filename.lower().endswith(".docx"):
        return "❌ Upload DOCX only"

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


# PDF MERGE
@app.route("/merge_pdf", methods=["POST"])
def merge_pdf():

    files = request.files.getlist("pdfs")

    merger = PdfMerger()

    for file in files:

        if not file.filename.lower().endswith(".pdf"):
            return "❌ Upload PDF files only"

        merger.append(file)

    output = "merged.pdf"

    merger.write(output)
    merger.close()

    return send_file(output, as_attachment=True)


# PDF SPLIT
@app.route("/split_pdf", methods=["POST"])
def split_pdf():

    file = request.files.get("pdf")

    if not file.filename.lower().endswith(".pdf"):
        return "❌ Upload PDF only"

    reader = PdfReader(file)

    writer = PdfWriter()

    writer.add_page(reader.pages[0])

    output = "split_page1.pdf"

    with open(output, "wb") as f:
        writer.write(f)

    return send_file(output, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)