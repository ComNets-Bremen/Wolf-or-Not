from django.core.management.base import BaseCommand, CommandError
from simplelabel.models import Image, Dataset, Poll

class Command(BaseCommand):
    help = 'Show some statistics for the current dataset'

    def add_arguments(self, parser):
        parser.add_argument('datasetid', type=int, help="The id of the checked dataset")

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Datasetid: " + str(options["datasetid"])))
        dataset = Dataset.objects.filter(pk=options["datasetid"])
        self.stdout.write(self.style.SUCCESS("Dataset: " + str(dataset)))
        num_ips = Poll.objects.filter(poll_image__image_dataset=options["datasetid"]).values("poll_ip").distinct().count()
        self.stdout.write(self.style.SUCCESS("From different IPs: " + str(num_ips)))
        num_polls = Poll.objects.filter(poll_image__image_dataset=options["datasetid"]).count()
        self.stdout.write(self.style.SUCCESS("Number polls: " + str(num_polls)))
        num_images = Image.objects.filter(image_dataset=options["datasetid"]).count()
        self.stdout.write(self.style.SUCCESS("Number images: " + str(num_images)))
