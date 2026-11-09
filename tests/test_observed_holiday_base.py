#  holidays
#  --------
#  A fast, efficient Python library for generating country, province and state
#  specific sets of holidays on the fly. It aims to make determining whether a
#  specific date is a holiday as fast and flexible as possible.
#
#  Authors: Vacanza Team and individual contributors (see CONTRIBUTORS file)
#           dr-prodigy <dr.prodigy.github@gmail.com> (c) 2017-2023
#           ryanss <ryanssdev@icloud.com> (c) 2014-2017
#  Website: https://github.com/vacanza/holidays
#  License: MIT (see LICENSE file)

from datetime import date
from unittest import TestCase
from unittest.mock import call, patch

from holidays.calendars.gregorian import MON, SUN
from holidays.observed_holiday_base import ObservedHolidayBase, ObservedRule


class TestObservedHolidayBase(TestCase):
    SUNDAY = date(2024, 5, 12)
    MONDAY = date(2024, 5, 13)
    SUN_TO_NONE = ObservedRule({SUN: None})
    MON_TO_TUE = ObservedRule({MON: +1})

    def setUp(self):
        self.ohb = ObservedHolidayBase(observed_rule=ObservedRule({MON: None}))
        self.ohb.observed_label = "%s (Observed Label)"
        self.ohb._populate(2024)

    def test_get_observed_date(self):
        self.assertIsNone(self.ohb._get_observed_date(self.SUNDAY, rule=self.SUN_TO_NONE))

    def test_observed_rules(self):
        self.assertEqual(
            (False, None),
            self.ohb._add_observed(
                self.ohb._add_holiday("Test Holiday", self.SUNDAY), rule=self.SUN_TO_NONE
            ),
        )

        self.assertEqual(
            (True, date(2024, 5, 14)),
            self.ohb._add_observed(
                self.ohb._add_holiday("Test Holiday", self.MONDAY), rule=self.MON_TO_TUE
            ),
        )

        self.assertEqual(
            dict(self.ohb),
            {
                date(2024, 5, 13): "Test Holiday",
                date(2024, 5, 14): "Test Holiday (Observed Label)",
            },
            self.ohb,
        )

    def _add_estimated_observed(self, estimated_label, observed_label, observed_estimated_label):
        ohb = ObservedHolidayBase(observed_rule=ObservedRule({SUN: +1}))
        ohb.estimated_label = estimated_label
        ohb.observed_label = observed_label
        ohb.observed_estimated_label = observed_estimated_label
        ohb._populate(2024)
        ohb._add_observed(ohb._add_holiday(estimated_label % "Test Holiday", self.SUNDAY))
        return ohb

    def test_observed_estimated_label(self):
        self.assertEqual(
            dict(
                self._add_estimated_observed(
                    "%s (estimated)", "%s (observed)", "%s (observed, estimated)"
                )
            ),
            {
                self.SUNDAY: "Test Holiday (estimated)",
                self.MONDAY: "Test Holiday (observed, estimated)",
            },
        )

    def test_observed_estimated_label_fullwidth_parentheses(self):
        self.assertEqual(
            dict(self._add_estimated_observed("%s（推定）", "%s（补假）", "%s（补假，推定）")),
            {
                self.SUNDAY: "Test Holiday（推定）",
                self.MONDAY: "Test Holiday（补假，推定）",
            },
        )

    def test_observed_without_estimated_label(self):
        with patch.object(self.ohb, "tr", wraps=self.ohb.tr) as tr:
            self.ohb._add_observed(
                self.ohb._add_holiday("Test Holiday", self.MONDAY), rule=self.MON_TO_TUE
            )

        self.assertNotIn(call(""), tr.call_args_list)
        self.assertEqual(self.ohb[date(2024, 5, 14)], "Test Holiday (Observed Label)")
