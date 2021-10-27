import PyPDF2
ANNOT_KEY = '/Annots'
ANNOT_FIELD_KEY = '/T'
ANNOT_VAL_KEY = '/V'
ANNOT_RECT_KEY = '/Rect'
SUBTYPE_KEY = '/Subtype'
WIDGET_SUBTYPE_KEY = '/Widget'


def write_fillable_pdf(input_pdf_path, output_pdf_path, data_dict):
    template_pdf = PyPDF2.PdfReader(input_pdf_path)
    annotations = template_pdf.pages[0][ANNOT_KEY]

    for annotation in annotations:
        if annotation[SUBTYPE_KEY] == WIDGET_SUBTYPE_KEY:
            if annotation[ANNOT_FIELD_KEY]:
                key = annotation[ANNOT_FIELD_KEY][1:-1]
                if key in data_dict.keys():
                    del annotation['/AP']

                    annotation.update(PyPDF2.PdfDict(DA='{}'.format('/Fo2Form 12 Tf 0 g')))
                    annotation.update(PyPDF2.PdfDict(V='{}'.format(data_dict[key])))

    PyPDF2.PdfWriter().write(output_pdf_path, template_pdf)
