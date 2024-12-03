from django.core.management.base import BaseCommand
import wbgapi as wb
from stats_comparison.models import Country, Indicator, StatisticValue
from django.db import transaction
import pandas as pd
import time

class Command(BaseCommand):
    help = 'Fetches data from World Bank API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Print detailed debugging information'
        )

    def debug_print(self, message, debug_enabled):
        if debug_enabled:
            self.stdout.write(self.style.SUCCESS(message))

    def handle(self, *args, **options):
        debug = options.get('debug', False)
        
        # Step 1: Fetch and save countries
        self.stdout.write('Step 1: Fetching countries...')
        try:
            countries = list(wb.economy.list())  # Convert generator to list
            self.debug_print(f"Retrieved {len(countries)} countries from API", debug)
            
            country_count = 0
            with transaction.atomic():
                for country in countries:
                    try:
                        # Skip aggregate regions and other non-country entries
                        # Check for both prefix and specific conditions
                        is_country = (
                            # Not starting with region/aggregate prefixes
                            not any(country['id'].startswith(prefix) for prefix in 
                                 ('REG', 'INX', 'EMU', 'EAS', 'ECS', 'EUU', 'ARB', 'CEB', 'CSS', 'EAP', 
                                  'ECA', 'EAR', 'FCS', 'HIC', 'HPC', 'IBD', 'IBT', 'IDA', 'IDB', 'IDX', 
                                  'LAC', 'LCN', 'LDC', 'LIC', 'LMC', 'LMY', 'LTE', 'MEA', 'MIC', 'MNA', 
                                  'NAC', 'OED', 'OSS', 'PRE', 'PSS', 'PST', 'SAS', 'SSA', 'SSF', 'SST', 
                                  'TEA', 'TEC', 'TLA', 'TMN', 'TSA', 'TSS', 'UMC', 'WLD')) and
                            # Must be exactly 3 characters (standard country code length)
                            len(country['id']) == 3 and
                            # Must have a proper region assigned
                            country.get('region', 'Unknown') != 'Unknown' and
                            # Additional checks for specific cases
                            not any(x in country['value'].lower() for x in ['region', 'union', 'income', 'aggregate'])
                        )
                        
                        if is_country:
                            Country.objects.update_or_create(
                                code=country['id'],
                                defaults={
                                    'name': country['value'],
                                    'region': country.get('region', 'Unknown')
                                }
                            )
                            country_count += 1
                            if debug:
                                self.debug_print(f"Saved country: {country['id']} - {country['value']}", debug)
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"Error saving country {country.get('id', 'Unknown')}: {str(e)}"))
            
            self.stdout.write(self.style.SUCCESS(f'Successfully saved {country_count} countries'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to fetch countries: {str(e)}'))
            return

        # Step 2: Define and save indicators
        indicators = [
            # Economic indicators
            ('NY.GDP.PCAP.CD', 'GDP per capita (current US$)'),
            ('NY.GDP.MKTP.KD.ZG', 'GDP growth (annual %)'),
            ('FP.CPI.TOTL.ZG', 'Inflation, consumer prices (annual %)'),
            ('NE.EXP.GNFS.ZS', 'Exports of goods and services (% of GDP)'),
            ('BX.KLT.DINV.WD.GD.ZS', 'Foreign direct investment, net inflows (% of GDP)'),
            ('GC.DOD.TOTL.GD.ZS', 'Central government debt (% of GDP)'),
            
            # Social indicators
            ('SP.POP.TOTL', 'Population, total'),
            ('SP.DYN.LE00.IN', 'Life expectancy at birth (years)'),
            ('SE.TER.ENRR', 'School enrollment, tertiary (% gross)'),
            ('SL.UEM.TOTL.ZS', 'Unemployment, total (% of total labor force)'),
            ('SI.POV.GINI', 'GINI index'),
            ('SH.XPD.CHEX.GD.ZS', 'Current health expenditure (% of GDP)'),
            ('SP.URB.TOTL.IN.ZS', 'Urban population (% of total)'),
            
            # Environmental indicators
            ('EN.ATM.CO2E.PC', 'CO2 emissions (metric tons per capita)'),
            ('EG.USE.PCAP.KG.OE', 'Energy use (kg of oil equivalent per capita)'),
            ('ER.FST.TOTL.ZS', 'Forest area (% of land area)'),
            ('EG.ELC.ACCS.ZS', 'Access to electricity (% of population)'),
            ('EN.POP.DNST', 'Population density (people per sq. km)'),
        ]
        
        self.stdout.write('\nStep 2: Saving indicators...')
        saved_indicators = 0
        for code, name in indicators:
            try:
                indicator_info = wb.series.get(code)
                Indicator.objects.update_or_create(
                    code=code,
                    defaults={
                        'name': name,
                        'description': indicator_info.get('sourceNote', '')
                    }
                )
                saved_indicators += 1
                self.debug_print(f"Saved indicator: {code}", debug)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error saving indicator {code}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully saved {saved_indicators} indicators'))

        # Step 3: Fetch and save statistical values
        self.stdout.write('\nStep 3: Fetching statistical values...')
        total_values = 0
        years = list(range(2019, 2024))
        
        for code, name in indicators:
            try:
                self.stdout.write(f'\nProcessing {name}...')
                
                # Add delay to avoid rate limiting
                time.sleep(2)  # Increased delay to 2 seconds
                
                # Fetch data for current indicator
                data = wb.data.DataFrame(code, time=years)
                self.debug_print(f"Raw data shape: {data.shape}", debug)
                
                if debug:
                    self.stdout.write("Sample of raw data:")
                    self.stdout.write(str(data.head()))
                
                # Convert the data to a format that's easier to work with
                df_melted = data.reset_index().melt(
                    id_vars=['economy'],
                    var_name='year',
                    value_name='value'
                )
                
                with transaction.atomic():
                    # Process each row in the melted DataFrame
                    for _, row in df_melted.iterrows():
                        country_code = row['economy']
                        year_str = row['year']
                        value = row['value']
                        
                        try:
                            # Get the country object
                            country = Country.objects.filter(code=country_code).first()
                            if country:
                                # Extract year from YR2019 format
                                year = int(str(year_str).replace('YR', ''))
                                
                                # Check if value is not NaN and can be converted to float
                                if pd.notna(value):
                                    try:
                                        value_float = float(value)
                                        
                                        # Create or update the statistic value
                                        stat_value, created = StatisticValue.objects.update_or_create(
                                            country=country,
                                            indicator_id=code,
                                            year=year,
                                            defaults={'value': value_float}
                                        )
                                        
                                        if created or stat_value.value != value_float:
                                            total_values += 1
                                            if debug:
                                                self.debug_print(
                                                    f"Saved value for {country_code}, {year}: {value_float}",
                                                    debug
                                                )
                                            
                                            if total_values % 100 == 0:
                                                self.stdout.write(f'Saved {total_values} values...')
                                    except (ValueError, TypeError) as e:
                                        self.debug_print(
                                            f"Could not convert value '{value}' to float for "
                                            f"{country_code}, {year}: {str(e)}", debug
                                        )
                        except Exception as e:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'Error processing {country_code}, {year_str}: {str(e)}'
                                )
                            )
                
                self.stdout.write(self.style.SUCCESS(f'Completed processing {name}'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing indicator {code}: {str(e)}'))
        
        # Final report
        self.stdout.write('\nFinal Statistics:')
        self.stdout.write(f'Countries in database: {Country.objects.count()}')
        self.stdout.write(f'Indicators in database: {Indicator.objects.count()}')
        self.stdout.write(f'Statistical values saved: {total_values}')
        
        if total_values > 0:
            self.stdout.write(self.style.SUCCESS('Successfully fetched and saved World Bank data'))
        else:
            self.stdout.write(self.style.WARNING('No statistical values were saved. Check the debug output for errors'))
