from django.core.management.base import BaseCommand
from toybox.models import *


class Command(BaseCommand):
    help = 'Update toy tally with borrowed weeks x current toy cost. Only updates loan cost tally that are empty and have been previously borrowed'
    firstRun = True

    def _update_toy_tally(self):
        toyList = Toy.objects.all()
        total_toys=Toy.objects.count()

        count=0
        for toy in toyList:
            if toy.borrow_counter > 0 and (toy.rent_tally == 0 or toy.rent_tally == None):
                toy.rent_tally = toy.borrow_counter * toy.loan_cost
                toy.save()
                count=count+1
                print("toy "+str(count)+" updated: " + toy.name)

        print(str(count)+" out of " + str(total_toys)+" toys updated")




    def handle(self, *args, **options):
        self._update_toy_tally()

