from django.core.management.base import BaseCommand
from toybox.models import *


class Command(BaseCommand):
    help = 'Reset test data in the database'
    firstRun=True

    def _reset_membertype(self):
        
        MemberType.objects.filter(name="Public").delete()

        MemberType.objects.update_or_create(name="Public",
                                            fee="30",
                                            deposit=30,
                                            membership_period=MemberType.YEARLY)
       
        MemberType.objects.filter(name="Play Group").delete()
        MemberType.objects.update_or_create(name="Play Group",
                                            fee=200,
                                            deposit=100,
                                            membership_period=MemberType.YEARLY)

    def _reset_loantype(self):

        LoanType.objects.filter(name="Standard").delete()

        self.lt_standard, created = LoanType.objects.update_or_create(name="Standard",
                                            loan_period_max=6,
                                            loan_cost=0.5,
                                            overdue_fine=0.5,
                                            missing_piece_fine=0.5,
                                            missing_piece_refund=0.5,
                                            loan_deposit=0.0)

        LoanType.objects.filter(name="Outdoor Toy").delete()

        self.lt_outdoor, created = LoanType.objects.update_or_create(name="Outdoor Toy",
                                            loan_period_max=6,
                                            loan_cost=2.0,
                                            overdue_fine=2.0,
                                            missing_piece_fine=0.5,
                                            missing_piece_refund=0.5,
                                            loan_deposit=5.0)

    def _reset_members(self):
        YEARS = 365
        mt_public = MemberType.objects.get(name="Public")
        mt_playgrp = MemberType.objects.get(name="Play Group")
       
        Member.objects.filter(name="John Doh").delete()
        self.m_johndoh, created = Member.objects.update_or_create(name="John Doh",
                                                                  address="1 example place",
                                                                  phone_number1="0404233322",
                                                                  type=mt_public,
                                                                  join_date=datetime.datetime.now() )

        Child.objects.update_or_create(name="Alice",
                                       date_of_birth=datetime.datetime.now() - datetime.timedelta(
                                           days=(3.5 * YEARS)),
                                       parent=self.m_johndoh)

        Child.objects.update_or_create(name="Brian",
                                       date_of_birth=datetime.datetime.now() - datetime.timedelta(
                                           days=(1 * YEARS)),
                                       parent=self.m_johndoh)
       
        Member.objects.filter(name="John Smith").delete()
        self.m_johnsmith, created = Member.objects.update_or_create(name="John Smith",
                                                                    address="2 example place",
                                                                    phone_number1="0444222333",
                                                                    email_address="john.smith@adapt.net",
                                                                    type=mt_public,
                                                                    partner="James Smith",
                                                                    volunteer=True,
                                                                    join_date=datetime.datetime.now() - datetime.timedelta(
                                                                        days=307))

        Child.objects.update_or_create(name="Huey",
                                       date_of_birth=datetime.datetime.now() - datetime.timedelta(
                                           days=(1 * YEARS)),
                                       parent=self.m_johnsmith)

        Child.objects.update_or_create(name="Dewey",
                                       date_of_birth=datetime.datetime.now() - datetime.timedelta(
                                           days=(1 * YEARS)),
                                       parent=self.m_johnsmith)

        Child.objects.update_or_create(name="Louie",
                                       date_of_birth=datetime.datetime.now() - datetime.timedelta(
                                           days=(1 * YEARS)),
                                       parent=self.m_johnsmith)
       
        Member.objects.filter(name="Alice Catcher").delete()
        self.m_alicecatcher, created = Member.objects.update_or_create(name="Alice Catcher",
                                                                       address="12 allweather st",
                                                                       phone_number1="0297573443",
                                                                       phone_number2="0413 123 321",
                                                                       email_address="alice_catcher47@my.fresh.domain.com.au",
                                                                       type=mt_public,
                                                                       partner="Eric Catcher",
                                                                       balance="4.30",
                                                                       committee_member=True,
                                                                       join_date=datetime.datetime.now() - datetime.timedelta(
                                                                           days=1037))

        Child.objects.update_or_create(name="Elizabeth Jayne",
                                       date_of_birth=datetime.datetime.now() - datetime.timedelta(
                                           days=(6 * YEARS)),
                                       parent=self.m_alicecatcher)
       
        Member.objects.filter(name="Olivia Stone").delete()
        Member.objects.update_or_create(name="Olivia Stone",
                                        address="45/104 Northebourne Avenue, Canberra",
                                        phone_number1="0453 989 990",
                                        type=mt_public,
                                        balance="23",
                                        volunteer=True,
                                        # active=False,
                                        join_date=datetime.datetime.now() - datetime.timedelta(days=360),
                                        membership_end_date=datetime.datetime.now())

        Member.objects.filter(name="Majura Play Group").delete()
        self.m_majpg, created = Member.objects.update_or_create(name="Majura Play Group",
                                                                address="44 Irvine st Watson",
                                                                phone_number1="0423 54 5566",
                                                                phone_number2="02 77 889 455",
                                                                type=mt_playgrp,
                                                                balance="-12",
                                                                join_date=datetime.datetime.now() - datetime.timedelta(days=100),
                                                                membership_end_date=datetime.datetime.now() + datetime.timedelta(days=265))

    def _reset_toybrand(self):
        self.tb_mandd, created = ToyBrand.objects.update_or_create(name="Mellisa & Doug")
        self.tb_fp, created = ToyBrand.objects.update_or_create(name="Fisher Price")
        self.tb_wow, created = ToyBrand.objects.update_or_create(name="WOW")
        self.tb_brio, created = ToyBrand.objects.update_or_create(name="Brio")
        self.tb_unk, created = ToyBrand.objects.update_or_create(name="Unknown")

    def _reset_toycategory(self):
        self.tc_big, created = ToyCategory.objects.update_or_create(name="Big")
        self.tc_img, created = ToyCategory.objects.update_or_create(name="Imaginative")
        self.tc_puz, created = ToyCategory.objects.update_or_create(name="Puzzle")
        self.tc_con, created = ToyCategory.objects.update_or_create(name="Construction")
        self.tc_out, created = ToyCategory.objects.update_or_create(name="Outside")

    def _reset_toypackaging(self):
        self.tp_pt, created = ToyPackaging.objects.update_or_create(name="Plastic Tub")
        self.tp_net, created = ToyPackaging.objects.update_or_create(name="Net")
        self.tp_none, created = ToyPackaging.objects.update_or_create(name="None")
        self.tp_case, created = ToyPackaging.objects.update_or_create(name="Case")
        self.tp_bag, created = ToyPackaging.objects.update_or_create(name="Bag")

    def _reset_toys(self):
       
        Toy.objects.filter(code="B1").delete()
        self.t_b1, created = Toy.objects.update_or_create(code="B1",
                                                          name="Roller Coaster",
                                                          brand=self.tb_unk,
                                                          member_loaned=None,
                                                          max_age=6,
                                                          min_age=2,
                                                          num_pieces=7,
                                                          state=Toy.AVAILABLE,
                                                          category=self.tc_big,
                                                          packaging=self.tp_bag,
                                                          loan_type=self.lt_standard,
                                                          image="toy_images/51JFER2cZpL._SY300__6bqlMzq.jpg")

       
        Toy.objects.filter(code="I13").delete()
        self.t_i13, created = Toy.objects.update_or_create(code="I13",
                                                           name="Pirate costume",
                                                           brand=self.tb_unk,
                                                           member_loaned=None,
                                                           max_age=5,
                                                           min_age=4,
                                                           num_pieces=4,
                                                           state=Toy.AVAILABLE,
                                                           category=self.tc_img,
                                                           packaging=self.tp_bag,
                                                           loan_type=self.lt_standard,
                                                           image="toy_images/kids-captain-black-pirate-costume_Dk0e1gc.jpg")
       
        Toy.objects.filter(code="P5").delete()
        self.t_p5, created = Toy.objects.update_or_create(code="P5",
                                                          name="Monkey Puzzle",
                                                          brand=self.tb_mandd,
                                                          member_loaned=None,
                                                          max_age=4,
                                                          min_age=1,
                                                          num_pieces=24,
                                                          state=Toy.AVAILABLE,
                                                          category=self.tc_puz,
                                                          packaging=self.tp_none,
                                                          loan_type=self.lt_standard,
                                                          image="toy_images/Supplies-26-letter-digital-wooden-font-b-puzzle-b-font-building-font-b-monkey_9FCx2kM.jpg")

       
        Toy.objects.filter(code="O2").delete()
        self.t_o2, created = Toy.objects.update_or_create(code="O2",
                                                          name="Train",
                                                          brand=self.tb_fp,
                                                          member_loaned=None,
                                                          max_age=6,
                                                          min_age=3,
                                                          state=Toy.AVAILABLE,
                                                          category=self.tc_out,
                                                          packaging=self.tp_none,
                                                          loan_type=self.lt_outdoor,
                                                          image="toy_images/6-30108_8917.jpg")

        Toy.objects.filter(code="O3").delete()
        self.t_o3, created = Toy.objects.update_or_create(code="O3",
                                                          name="Train 2",
                                                          brand=self.tb_fp,
                                                          member_loaned=None,
                                                          max_age=6,
                                                          min_age=3,
                                                          state=Toy.AVAILABLE,
                                                          category=self.tc_out,
                                                          packaging=self.tp_none,
                                                          loan_type=self.lt_outdoor,
                                                          image="toy_images/6-30108_8917.jpg")

    def _reset_toy_history(self):
        ToyHistory.objects.filter(toy=self.t_i13,
                             issue_type=Toy.MINOR_MISSING_PIECE,
                             member=self.m_johnsmith).delete()
        ToyHistory.objects.update_or_create(toy=self.t_i13,
                                       issue_type=Toy.MINOR_MISSING_PIECE,
                                       member=self.m_johnsmith)

        ToyHistory.objects.filter(toy=self.t_b1,
                             issue_type=Toy.ISSUE_NONE,
                             member=self.m_alicecatcher).delete()
        ToyHistory.objects.update_or_create(toy=self.t_b1,
                                       issue_type=Toy.ISSUE_NONE,
                                       member=self.m_alicecatcher)

        ToyHistory.objects.filter(toy=self.t_p5,
                             issue_type=Toy.BROKEN_REPAIRABLE,
                             member=self.m_alicecatcher).delete()
        ToyHistory.objects.update_or_create(toy=self.t_p5,
                                       issue_type=Toy.BROKEN_REPAIRABLE,
                                       member=self.m_alicecatcher)

    def _reset_transactions(self):
        Transaction.objects.filter(#volunteer_reporting=self.m_johnsmith,
                                   member=self.m_alicecatcher,
                                   transaction_type=Transaction.BORROW_FEE,
                                   amount=2.5).delete()
        Transaction.objects.update_or_create(#volunteer_reporting=self.m_johnsmith,
                                             member=self.m_alicecatcher,

                                             transaction_type=Transaction.BORROW_FEE,
                                             amount=2.5)

        Transaction.objects.filter(#volunteer_reporting=self.m_johnsmith,
                                   transaction_type=Transaction.MEMBER_DONATION,
                                   amount=10).delete()
        Transaction.objects.update_or_create(#volunteer_reporting=self.m_johnsmith,
                                             transaction_type=Transaction.MEMBER_DONATION,
                                             amount=10)

        Transaction.objects.filter(#volunteer_reporting=self.m_johnsmith,
                                   member=self.m_johndoh,
                                   transaction_type=Transaction.LATE_FEE,
                                   amount=1).delete()
        Transaction.objects.update_or_create(#volunteer_reporting=self.m_johnsmith,
                                             member=self.m_johndoh,
                                             transaction_type=Transaction.LATE_FEE,
                                             amount=1)

        Transaction.objects.filter(#volunteer_reporting=self.m_johnsmith,
                                   member=self.m_johndoh,
                                   transaction_type=Transaction.MEMBERSHIP_FEE,
                                   amount=20).delete()
        Transaction.objects.update_or_create(#volunteer_reporting=self.m_johnsmith,
                                             member=self.m_johndoh,
                                             transaction_type=Transaction.MEMBERSHIP_FEE,
                                             amount=20)

    def _reset_config(self):
        Config.objects.filter(key="loan_durations").delete()
        Config.objects.update_or_create(key="loan_durations",
                                            value="12",
                                            help="Single digit number of weeks in a string, eg 126",
                                            )

        Config.objects.filter(key="default_loan_duration").delete()
        Config.objects.update_or_create(key="default_loan_duration",
                                            value="2",
                                            help="Default time a toy is borrowed in weeks eg 2",
                                            )

        Config.objects.filter(key="max_toys").delete()
        Config.objects.update_or_create(key="max_toys",
                                          value="4",
                                          help="Maximum number of toys a member can borrow at once eg 4",
                                          )




    def handle(self, *args, **options):

        self._reset_membertype()
        self._reset_loantype()
        self._reset_members()
        self._reset_toybrand()
        self._reset_toycategory()
        self._reset_toypackaging()
        self._reset_toys()
        self._reset_toy_history()
        self._reset_transactions()
        self._reset_config()
