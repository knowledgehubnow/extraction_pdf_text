from django.shortcuts import render
from .models import *
from pdfminer.high_level import extract_text
from io import BytesIO


def home_page(request):
    if request.method == "POST":
        pdf_file = request.FILES.get("pdf")  # Use request.FILES to handle file uploads
        if pdf_file:
            try:
                # Check if PDF with the same name exists
                pdf_data = AnalyzePDF.objects.filter(pdf_name=pdf_file).first()
                print(pdf_data)

                if pdf_data is None:
                    # Convert the InMemoryUploadedFile to a BytesIO object
                    pdf_content = pdf_file.read()
                    
                    # Extract text using pdfminer
                    all_text = extract_text(BytesIO(pdf_content))
                    print(all_text)

                    # Save to the database
                    pdf_data = AnalyzePDF(pdf_name=pdf_file, pdf_file=pdf_file, pdf_text=all_text)
                    pdf_data.save()

                    return render(request, "pdf_upload.html", {
                        "pdf_name": pdf_file,
                        "all_text": all_text,
                    })
                else:
                    return render(request, "pdf_upload.html", {
                        "message": "PDF already exists with the same name.",
                        "tag": "danger",
                    })
            except Exception as e:
                print(f"Error reading PDF: {e}")
                return render(request, "pdf_upload.html", {
                    "message": "Something went wrong. Please try again.",
                    "tag": "danger",
                })
        else:
            print("No PDF file uploaded")
            return render(request, "pdf_upload.html", {
                "message": "No PDF file uploaded",
                "tag": "danger",
            })
    return render(request,"pdf_upload.html")


def analyzed_pdf_list(request):
    all_pdf = AnalyzePDF.objects.all()
    return render(request,"analized_pdf_list.html",{
        "all_pdf":all_pdf
    })

def analyzed_pdf_view(request,pdf_id):
    pdf = AnalyzePDF.objects.get(id = pdf_id)
    return render(request,"analyzed_pdf_view.html",{
        "pdf":pdf
    })
