from django.core.management.base import BaseCommand
from stats_comparison.models import Country, Indicator, StatisticValue

class Command(BaseCommand):
    help = 'Check database contents'

    def handle(self, *args, **options):
        # Check Countries
        country_count = Country.objects.count()
        self.stdout.write(f"Number of Countries: {country_count}")
        if country_count > 0:
            self.stdout.write("\nSample Countries:")
            for country in Country.objects.all()[:5]:
                self.stdout.write(f"- {country.code}: {country.name} ({country.region})")

        # Check Indicators
        indicator_count = Indicator.objects.count()
        self.stdout.write(f"\nNumber of Indicators: {indicator_count}")
        if indicator_count > 0:
            self.stdout.write("\nAll Indicators:")
            for indicator in Indicator.objects.all():
                self.stdout.write(f"- {indicator.code}: {indicator.name}")

        # Check Statistics
        stats_count = StatisticValue.objects.count()
        self.stdout.write(f"\nNumber of Statistical Values: {stats_count}")
        if stats_count > 0:
            self.stdout.write("\nSample Statistics:")
            for stat in StatisticValue.objects.select_related('country', 'indicator')[:5]:
                self.stdout.write(
                    f"- {stat.country.name}, {stat.indicator.name}, "
                    f"Year: {stat.year}, Value: {stat.value}"
                )
