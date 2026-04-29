from django.http import Http404, HttpResponse
from django.shortcuts import render

from .logic import CALC_FUNCTIONS
from .registry import CALCULATOR_MAP, CALCULATORS


def calculator_index(request):
    # Used standalone; the financial_tools_page renders the grid
    return render(request, 'calculators/index.html', {'calculators': CALCULATORS})


def calculator_detail(request, slug):
    calc = CALCULATOR_MAP.get(slug)
    if not calc:
        raise Http404

    return render(request, 'calculators/detail.html', {'calc': calc})


def calculator_submit(request, slug):
    calc = CALCULATOR_MAP.get(slug)
    if not calc:
        raise Http404

    if request.method != 'POST':
        return HttpResponse(status=405)

    fn = CALC_FUNCTIONS.get(slug)
    if fn:
        results = fn(request.POST)
    else:
        results = {'error': 'Calculator not yet implemented.'}

    return render(request, 'calculators/partials/_result.html', {
        'calc': calc,
        'results': results,
    })
