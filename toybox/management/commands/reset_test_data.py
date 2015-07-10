from django.core.management.base import BaseCommand
from toybox.models import *


class Command(BaseCommand):
    help = 'Populate the database with some test data'

    def _add_membertype(self):
        MemberType.objects.update_or_create(name="Public",
                                            fee="30",
                                            membership_period=0)

        MemberType.objects.update_or_create(name="Play Group",
                                            fee=200,
                                            membership_period=1)

    def _add_members(self):
        YEARS = 365
        mt_public = MemberType.objects.get(name="Public")
        mt_playgrp = MemberType.objects.get(name="Play Group")

        self.m_johndoh, created = Member.objects.update_or_create(name="John Doh",
                                                                  address="1 example place",
                                                                  phone_number1="0404233322",
                                                                  type=mt_public,
                                                                  join_date=timezone.now() - datetime.timedelta(days=7))

        Child.objects.update_or_create(name="Alice",
                                       date_of_birth=timezone.now() - datetime.timedelta(
                                           days=(3.5 * YEARS)),
                                       parent=self.m_johndoh)

        Child.objects.update_or_create(name="Brian",
                                       date_of_birth=timezone.now() - datetime.timedelta(
                                           days=(1 * YEARS)),
                                       parent=self.m_johndoh)

        self.m_johnsmith, created = Member.objects.update_or_create(name="John Smith",
                                                                    address="2 example place",
                                                                    phone_number1="0444222333",
                                                                    email_address="john.smith@adapt.net",
                                                                    type=mt_public,
                                                                    partner="James Smith",
                                                                    volunteer=True,
                                                                    join_date=timezone.now() - datetime.timedelta(
                                                                        days=307))

        Child.objects.update_or_create(name="Huey",
                                       date_of_birth=timezone.now() - datetime.timedelta(
                                           days=(1 * YEARS)),
                                       parent=self.m_johnsmith)

        Child.objects.update_or_create(name="Dewey",
                                       date_of_birth=timezone.now() - datetime.timedelta(
                                           days=(1 * YEARS)),
                                       parent=self.m_johnsmith)

        Child.objects.update_or_create(name="Louie",
                                       date_of_birth=timezone.now() - datetime.timedelta(
                                           days=(1 * YEARS)),
                                       parent=self.m_johnsmith)

        self.m_alicecatcher, created = Member.objects.update_or_create(name="Alice Catcher",
                                                                       address="12 allweather st",
                                                                       phone_number1="0297573443",
                                                                       phone_number2="0413 123 321",
                                                                       email_address="alice_catcher47@my.fresh.domain.com.au",
                                                                       type=mt_public,
                                                                       partner="Eric Catcher",
                                                                       balance="4.30",
                                                                       committee_member=True,
                                                                       join_date=timezone.now() - datetime.timedelta(
                                                                           days=1037))

        Child.objects.update_or_create(name="Elizabeth Jayne",
                                       date_of_birth=timezone.now() - datetime.timedelta(
                                           days=(6 * YEARS)),
                                       parent=self.m_alicecatcher)

        Member.objects.update_or_create(name="Olivia Stone",
                                        address="45/104 Northebourne Avenue, Canberra",
                                        phone_number1="0453 989 990",
                                        type=mt_public,
                                        balance="23",
                                        volunteer=True,
                                        active=False,
                                        join_date=timezone.now() - datetime.timedelta(days=360))

        self.m_majpg, created = Member.objects.update_or_create(name="Majura Play Group",
                                                                address="44 Irvine st Watson",
                                                                phone_number1="0423 54 5566",
                                                                phone_number2="02 77 889 455",
                                                                type=mt_playgrp,
                                                                balance="-12",
                                                                join_date=timezone.now() - datetime.timedelta(days=100))

    def _add_toybrand(self):
        self.tb_mandd, created = ToyBrand.objects.update_or_create(name="Mellisa & Doug")
        self.tb_fp, created = ToyBrand.objects.update_or_create(name="Fisher Price")
        self.tb_wow, created = ToyBrand.objects.update_or_create(name="WOW")
        self.tb_brio, created = ToyBrand.objects.update_or_create(name="Brio")
        self.tb_unk, created = ToyBrand.objects.update_or_create(name="Unknown")

    def _add_toycategory(self):
        self.tc_big, created = ToyCategory.objects.update_or_create(name="Big")
        self.tc_img, created = ToyCategory.objects.update_or_create(name="Imaginative")
        self.tc_puz, created = ToyCategory.objects.update_or_create(name="Puzzle")
        self.tc_con, created = ToyCategory.objects.update_or_create(name="Construction")
        self.tc_out, created = ToyCategory.objects.update_or_create(name="Outside")

    def _add_toypackaging(self):
        self.tp_pt, created = ToyPackaging.objects.update_or_create(name="Plastic Tub")
        self.tp_net, created = ToyPackaging.objects.update_or_create(name="Net")
        self.tp_none, created = ToyPackaging.objects.update_or_create(name="None")
        self.tp_case, created = ToyPackaging.objects.update_or_create(name="Case")
        self.tp_bag, created = ToyPackaging.objects.update_or_create(name="Bag")

    def _add_toys(self):
        self.t_b1, created = Toy.objects.update_or_create(code="B1",
                                                          description="Roller Coaster",
                                                          toy_brand=self.tb_unk,
                                                          member_loaned=self.m_alicecatcher,
                                                          max_age=6,
                                                          min_age=2,
                                                          num_pieces=7,
                                                          state=Toy.BORROWED,
                                                          category=self.tc_big,
                                                          packaging=self.tp_bag)

        self.t_i13, created = Toy.objects.update_or_create(code="I13",
                                                           description="Pirate costume",
                                                           toy_brand=self.tb_unk,
                                                           member_loaned=None,
                                                           max_age=5,
                                                           min_age=4,
                                                           num_pieces=4,
                                                           state=Toy.NOT_IN_SERVICE,
                                                           availability_state=Toy.MAJOR_NOTABLE_ISSUE,
                                                           category=self.tc_img,
                                                           packaging=self.tp_bag)

        self.t_p5, created = Toy.objects.update_or_create(code="P5",
                                                          description="Monkey Puzzle",
                                                          toy_brand=self.tb_mandd,
                                                          member_loaned=None,
                                                          max_age=4,
                                                          min_age=1,
                                                          num_pieces=24,
                                                          state=Toy.AT_TOY_LIBRARY,
                                                          availability_state=Toy.AVAILABLE,
                                                          category=self.tc_puz,
                                                          packaging=self.tp_none)

        self.t_o2, created = Toy.objects.update_or_create(code="O2",
                                                          description="Plastic Car",
                                                          toy_brand=self.tb_fp,
                                                          member_loaned=None,
                                                          max_age=6,
                                                          min_age=3,
                                                          state=Toy.AT_TOY_LIBRARY,
                                                          availability_state=Toy.AVAILABLE,
                                                          category=self.tc_out,
                                                          packaging=self.tp_none)

    def _add_issues(self):
        Issue.objects.update_or_create(toy=self.t_i13,
                                       issue_type=Issue.MAJOR_MISSING_PIECE,
                                       member_involved=self.m_johnsmith)

        Issue.objects.update_or_create(toy=self.t_b1,
                                       issue_type=Issue.REPAIRED,
                                       member_involved=self.m_alicecatcher)

        Issue.objects.update_or_create(toy=self.t_p5,
                                       issue_type=Issue.RETURNED_MISSING_PIECE,
                                       member_involved=self.m_alicecatcher)

    def _add_transactions(self):
        Transaction.objects.update_or_create(volunteer_reporting=self.m_johnsmith,
                                             member=self.m_alicecatcher,
                                             toy=self.t_b1,
                                             transaction_type=Transaction.HIRE_CHARGE,
                                             amount=2.5)

        Transaction.objects.update_or_create(volunteer_reporting=self.m_johnsmith,
                                             transaction_type=Transaction.DONATION,
                                             amount=10)

        Transaction.objects.update_or_create(volunteer_reporting=self.m_johnsmith,
                                             member=self.m_johndoh,
                                             toy=self.t_i13,
                                             transaction_type=Transaction.FINE,
                                             amount=1)

        Transaction.objects.update_or_create(volunteer_reporting=self.m_johnsmith,
                                             member=self.m_johndoh,
                                             transaction_type=Transaction.MEMBERSHIP,
                                             amount=20)

    def handle(self, *args, **options):
        self._add_membertype()
        self._add_members()
        self._add_toybrand()
        self._add_toycategory()
        self._add_toypackaging()
        self._add_toys()
        self._add_issues()
        self._add_transactions()