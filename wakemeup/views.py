from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'wakemeup/index.html')

def create_contract(request):
    return render(request, 'wakemeup/create_contract_modal.html')

def create_contract_new(request):
    return render(request, 'wakemeup/create_contract_modal_new.html')
