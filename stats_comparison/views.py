from django.shortcuts import render
import wbgapi as wb
import plotly.express as px
import pandas as pd
from .models import Country, Indicator, StatisticValue
import json
from django.db.models import Q

def index(request):
    # Get all available indicators
    indicators = Indicator.objects.all().order_by('name')
    countries = Country.objects.all().order_by('name')
    
    context = {
        'indicators': indicators,
        'countries': countries,
        'error': None
    }
    
    if request.method == 'POST':
        try:
            # Get selected indicators and countries
            indicator1 = request.POST.get('indicator1')
            indicator2 = request.POST.get('indicator2')
            selected_countries = request.POST.getlist('countries')
            
            if not indicator1 or not indicator2 or not selected_countries:
                raise ValueError("Please select both indicators and at least one country")
            
            # Get data for the selected indicators
            data1 = StatisticValue.objects.filter(
                indicator__code=indicator1,
                country__code__in=selected_countries,
                value__isnull=False  # Exclude null values
            ).select_related('country')
            
            data2 = StatisticValue.objects.filter(
                indicator__code=indicator2,
                country__code__in=selected_countries,
                value__isnull=False  # Exclude null values
            ).select_related('country')
            
            if not data1 or not data2:
                raise ValueError("No data available for the selected combination")
            
            # Create pandas DataFrame for plotting
            data_list = []
            for d1 in data1:
                d2 = data2.filter(country=d1.country, year=d1.year).first()
                if d2:
                    data_list.append({
                        'Country': f"{d1.country.name} ({d1.year})",
                        'Value1': float(d1.value) if d1.value is not None else None,
                        'Value2': float(d2.value) if d2.value is not None else None
                    })
            
            if not data_list:
                raise ValueError("No matching data points found for the selected combination")
            
            df = pd.DataFrame(data_list)
            
            # Get indicator names for the plot
            ind1_name = Indicator.objects.get(code=indicator1).name
            ind2_name = Indicator.objects.get(code=indicator2).name
            
            # Create scatter plot
            fig = px.scatter(
                df,
                x='Value1',
                y='Value2',
                text='Country',
                labels={
                    'Value1': ind1_name,
                    'Value2': ind2_name
                },
                title=f'Comparison of {ind1_name} vs {ind2_name}'
            )
            
            # Customize the layout
            fig.update_traces(
                textposition='top center',
                marker=dict(size=10)
            )
            
            plot_div = fig.to_html(full_html=False)
            context['plot'] = plot_div
            
        except Exception as e:
            context['error'] = str(e)
    
    return render(request, 'stats_comparison/index.html', context)
