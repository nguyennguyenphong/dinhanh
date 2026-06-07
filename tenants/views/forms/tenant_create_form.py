from django import forms
from tenants.models.tenants import Tenant

class TenantCreateForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = ['code', 'name', 'plan', 'currency', 'is_active', 'domain']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'w-full border-[1.5px] border-gray-200 rounded-md bg-white transition-all hover:border-blue-400 focus:border-blue-500 focus:ring-0 dark:bg-slate-800 dark:border-slate-700 dark:text-gray-200 px-4 py-3 text-sm',
                                           'placeholder': 'Enter tenant code'}),
            'name': forms.TextInput(attrs={'class': 'w-full border-[1.5px] border-gray-200 rounded-md bg-white transition-all hover:border-blue-400 focus:border-blue-500 focus:ring-0 dark:bg-slate-800 dark:border-slate-700 dark:text-gray-200 px-4 py-3 text-sm',
                                           'placeholder': 'Enter tenant name'}),
            'plan': forms.Select(attrs={'class': 'w-full border-[1.5px] border-gray-200 rounded-md bg-white transition-all hover:border-blue-400 focus:border-blue-500 focus:ring-0 dark:bg-slate-800 dark:border-slate-700 dark:text-gray-200 px-4 py-3 text-sm'}),
            'domain': forms.TextInput(attrs={'class': 'w-full border-[1.5px] border-gray-200 rounded-md bg-white transition-all hover:border-blue-400 focus:border-blue-500 focus:ring-0 dark:bg-slate-800 dark:border-slate-700 dark:text-gray-200 px-4 py-3 text-sm',
                                           'placeholder': 'Enter tenant domain'}),
            # ''
        }

    def clean_code(self):
        """Ensure the code is uppercase and unique."""
        code = self.cleaned_data.get('code', '').upper()
        if Tenant.objects.filter(code=code).exists():
            raise forms.ValidationError("This tenant code already exists.")
        return code