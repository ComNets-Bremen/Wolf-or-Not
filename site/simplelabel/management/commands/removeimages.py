from django.core.management.base import BaseCommand, CommandError
from simplelabel.models import Image

class Command(BaseCommand):
    help = 'Remove images with only few votes'

    def add_arguments(self, parser):
        parser.add_argument('--percentage', default=0.3 , type=float, help="Groups with less than this number of images are removed")
        parser.add_argument('datasetid', type=int, help="The id of the checked dataset")
        parser.add_argument('--divider', default="_", type=str, help="Divider for the text string")
        parser.add_argument('--stepsback', default=1, type=int, help="Take n steps back from the back of the string")


    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Datasetid: " + str(options["datasetid"])))

        ids_to_remove = []
        ids_to_keep   = []

        for i in Image.objects.filter(image_dataset=options["datasetid"]):
            filename = options["divider"].join(i.get_filename().split(options["divider"])[:-options["stepsback"]])
            subimages = Image.objects.filter(image_dataset=options["datasetid"]).filter(image__contains=filename)
            num_subimages = len(subimages)
            num_polls = sum([i.get_number_polls() for i in subimages])
            if  num_polls/num_subimages < options["percentage"]:
                ids_to_remove += subimages
            else:
                ids_to_keep += subimages

        ids_to_remove = list(set(ids_to_remove))

        self.stdout.write(self.style.SUCCESS("Removing " + str(len(ids_to_remove)) + " images. Continue?"))
        while True:
            dec = input("[yY|nN]")
            if dec in ["y", "Y"]:
                for i in ids_to_remove:
                    i.delete()
                self.stdout.write(self.style.SUCCESS("Done"))
                break
            elif dec in ["n", "N"]:
                self.stdout.write(self.style.SUCCESS("Aborting"))
                break
            else:
                self.stdout.write(self.style.SUCCESS("Invalid selection. Please try again"))

