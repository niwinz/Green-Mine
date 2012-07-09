from django import forms

class DocumentForm(forms.Form):
    title = forms.CharField(max_length=200)
    document = forms.FileField(required=True)

    def __init__(self, *args, **kwargs):
        super(DocumentForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['required'] = 'true'
        self.fields['document'].widget.attrs['required'] = 'true'
