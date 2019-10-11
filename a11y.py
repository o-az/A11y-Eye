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
all_tags = 'wcag2a', 'wcag2aa', 'wcag21aa', 'section508', 'best-practice', 'experimental'


class Driver:
    def __init__(self, driver=None):
        """ By default it will be pointing to chromedriver, using
            the browser options for Chrome browser and using Chrome
            driver unless explicitly telling it 'firefox'
        """
        path = '/Users/omarbinsalamah/PycharmProjects/a11y-axe/drivers/geckodriver' if driver == 'firefox' \
            else '/Users/omarbinsalamah/PycharmProjects/a11y-axe/drivers/chromedriver'

        self.options = webdriver.FirefoxOptions() if driver == 'firefox' \
            else webdriver.ChromeOptions()

        if driver is 'firefox':
            self.drive = webdriver.Firefox(
                options=self.options,
                executable_path=path)

        else:
            self.options.add_argument("disable-infobars")
            self.options.add_argument("--disable-extensions")
            self.options.add_argument("--headless")
            self.drive = webdriver.Chrome(
                options=self.options,
                executable_path=path)

        # Link of site to be aXed ;)
        self.link = sys.argv[1]
        self.drive.get(self.link)


class A11y(Driver):
    def __init__(self):

        # For Firefox, change to super().__init__('firefox')
        super().__init__()

        """ Change the tags to whatever you want to test against """
        self.report, self.tags = [], ['best-practice']

    def run_axe(self):
        axe = Axe(self.drive)
        axe.inject()
        results = axe.run()

        # If no tags provided then attach all violations to report
        if len(self.tags) == 0:
            for violation in results['violations']:
                self.report.append(violation)

        # Compare tags provided vs. standard tags declared in beginning of file
        # if nothing in common then raise error
        elif not bool(set(all_tags) & set(self.tags)):
            raise ValueError('Typo: Double check the tags you provided')

        # Loop through violations that contain tags provided and attach them to report
        else:
            self.report = [violation for violation in results['violations']
                           if not set(violation['tags']).isdisjoint(self.tags)]

        axe.write_results(self.report, 'a11y.json')
        self.drive.close()


def main():
    A11y().run_axe()


""" If this file is being run as a script, then include the info
    below: how long the aXe test took to execute. """
if __name__ == '__main__':
    start = time.time()
    sys.stdout.write('Started Axe Accessibility Test\n')
    main()
    sys.stdout.write(f"Execution time {(time.time() - start).__round__(2)} Seconds")
    sys.stdout.write('\nFinished Axe Accessibility Test')
