from flask import Flask, render_template, request, send_file
from pdf2image import convert_from_bytes
from PIL import Image

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


# PDF → IMAGE
@app.route("/pdf_to_image", methods=["POST"])
def pdf_to_image():

    file = request.files.get("pdf")

    if not file or not file.filename.lower().endswith(".pdf"):
        return "❌ File not supported. Please upload a valid PDF."

    try:
        images = convert_from_bytes(file.read(), dpi=300)
    except:
        return "❌ File not supported. Please upload a valid PDF."

    img_path = "page1.jpg"

    images[0].save(img_path, "JPEG", quality=95)

    return send_file(img_path, as_attachment=True)


# IMAGE → PDF
@app.route("/image_to_pdf", methods=["POST"])
def image_to_pdf():

    files = request.files.getlist("images")

    if not files:
        return "❌ No images uploaded."

    image_list = []

    try:
        for file in files:
            img = Image.open(file).convert("RGB")
            image_list.append(img)
    except:
        return "❌ File not supported. Please upload valid images."

    pdf_path = "output.pdf"

    image_list[0].save(
        pdf_path,
        save_all=True,
        append_images=image_list[1:]
    )

    return send_file(pdf_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)