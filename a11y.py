#!/usr/local/bin/env python3
"""
Author: Omar Bin Salamah                     :
Date Initiated: 10-7-2019                    :
Brief Summary: Run aXe, get JSON file report :
"""

import time
import sys

from axe_selenium_python import Axe
from selenium import webdriver

# Tuple of all standard tags
all_tags = 'wcag2a', 'wcag2aa', 'wcag21aa', 'wcag244', 'wcag311', 'section508', 'best-practice', 'section508.22.a', \
           'experimental', 'cat'


class Driver:
    def __init__(self, driver=None, x=None):
        """ By default it will be pointing to chromedriver, using
            the browser options for Chrome browser and using Chrome
            driver unless explicitly telling it 'firefox'
        """
        self.driver = driver
        self.x = x
        path = '/Users/omarbinsalamah/PycharmProjects/a11y-axe/drivers/geckodriver' if driver == 'firefox' \
            else '/Users/omarbinsalamah/PycharmProjects/a11y-axe/drivers/chromedriver'

        self.options = webdriver.FirefoxOptions() if driver == 'firefox' \
            else webdriver.ChromeOptions()

        if driver is 'firefox':
            self.drive = webdriver.Firefox(options=self.options, executable_path=path)

        else:
            chrome_arguments = ["disabled-infobars", "--disable-extensions", "--headless"]
            for argument in chrome_arguments:
                self.options.add_argument(argument)

            self.drive = webdriver.Chrome(options=self.options, executable_path=path)

        # Link of web-page to be aXe-d
        self.link = sys.argv[1] if len(sys.argv) > 1 \
            else self.x
        # else sys.exit('Error: You did not provide a web-page link')

        self.drive.get(self.link)


class A11y(Driver):

    def __init__(self):
        super().__init__('firefox') if len(sys.argv) > 3 and sys.argv[3] == 'firefox' \
            else super().__init__(x='https://example.com')

        self.full_report = []
        self.parsed_report = []

        """ User provided tags to test against. 
            If none provided, it'll test against all tags
        """
        self.tags = [tag for tag in sys.argv[2].split(', ')] if len(sys.argv) > 2 else []

    # Helper function to parse only the relevant information from the report
    def parse_report(self, report):
        relevant_info = ['description', 'help', 'helpUrl', 'impact', 'tags']
        for info in report:
            for key, value in list(info.items()):
                if key not in relevant_info:
                    info.pop(key, None)
            self.parsed_report.append(info)

    def run_axe(self):
        axe = Axe(self.drive)
        axe.inject()
        results = axe.run()

        # If no tags provided then attach all violations to report
        if len(self.tags) == 0:
            [self.full_report.append(violation) for violation in results['violations']]

        # Compare tags provided vs. standard tags declared in beginning of file
        # if nothing in common then raise error
        elif not bool(set(all_tags) & set(self.tags)):
            raise ValueError(f"\n{sys.argv[2]} is not a valid tag\nSelect one from: {all_tags}")

        # Loop through violations that contain tags provided and attach them to report
        else:
            self.full_report = [violation for violation in results['violations']
                                if not set(violation['tags']).isdisjoint(self.tags)]

        self.parse_report(self.full_report)
        axe.write_results(self.full_report, 'a1y.json')


def main():
    A11y().run_axe()


""" If this file is being run as a script, then include the info
    below: how long the aXe test took to execute. """
if __name__ == '__main__':
    start = time.time()
    sys.stdout.write('Starting Axe Accessibility Test . . .\n')
    main()
    sys.stdout.write(f"Execution time {(time.time() - start).__round__(2)} Seconds")
    sys.stdout.write('\nFinished Axe Accessibility Test')
