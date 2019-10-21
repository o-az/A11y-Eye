#!/usr/local/bin/env python3
import sys
import time
import platform

from axe_selenium_python import Axe
from selenium import webdriver

# All standard tags
all_tags = 'wcag2a', 'wcag2aa', 'wcag21aa', 'wcag244', 'wcag311', 'section508',\
           'best-practice', 'section508.22.a', 'experimental', 'cat.aria'


class LinkException(Exception):
    pass


class Parser:
    def __init__(self):
        pass

    @staticmethod
    def parse_link(link):
        if not link:
            raise LinkException('You need to provide a link')
        if 'http://' not in link or 'https://' not in link:
            return 'https://' + link
        else:
            LinkException(f'Link is not formatted correctly -> {link}')


class Driver:
    # In order to make parameters optional, they're set to None
    # Why? Because default is Chrome, so no need to explicitly state
    # If Firefox is desired, then explicitly state 'firefox' down in A11y class
    def __init__(self, driver=None, dynamic_link=None, options=None, path=None):
        """ By default it will be pointing to chromedriver, using
            the browser options for Chrome browser and using Chrome
            driver unless explicitly telling it 'firefox'
        """
        self.driver = driver
        self.dynamic_link = dynamic_link
        self.options = options
        self.path = path

        # Link of web-page to be aXe-d
        self.link = sys.argv[1] if len(sys.argv) > 1 else self.dynamic_link

        # Selenium requires 'https://' so check if provided, if not then prepend it or give error
        self.link = Parser.parse_link(self.link)
        self.driver_setup().get(self.link)

    def driver_path(self):
        if self.driver == 'firefox':
            self.path = '/Users/omarbinsalamah/PycharmProjects/a11y-axe/drivers/geckodriver'
        else:
            self.path = '/Users/omarbinsalamah/PycharmProjects/a11y-axe/drivers/chromedriver'
        return self.path

    def driver_options(self):
        if self.driver == 'firefox':
            self.options = webdriver.FirefoxOptions()
        else:
            self.options = webdriver.ChromeOptions()
            chrome_arguments = ["disable-infobars", "--disable-extensions", "--headless"]
            for argument in chrome_arguments:
                self.options.add_argument(argument)
            self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
        return self.options

    def driver_setup(self):
        if self.driver is 'firefox':
            self.driver = webdriver.Firefox(options=self.driver_options(), executable_path=self.driver_path())
        else:
            self.driver = webdriver.Chrome(options=self.driver_options(), executable_path=self.driver_path())
        return self.driver


class A11y(Driver):

    def __init__(self, browser=None, link=None):
        """
        :param browser: Optionally specify to 'firefox' or ignore it and it'll default to chrome.
        :param link: When using it as a method, specify the link to the web-page you want to test
        # Like this: A11y('firefox', 'www.act.org').run_axe(), or leave the first parameter empty
        """
        super().__init__(driver='firefox') if len(sys.argv) > 3 and sys.argv[3] == 'firefox' \
            else super().__init__(driver=browser, dynamic_link=link)

        self.full_report = []
        self.parsed_report = []
        self.tags = []

    """ 
    You can pass tags in a string separated by commas for example, "wcag2aa, section508".
    If you don't pass anything, it will test for wcag2aa only
    """
    def scan_tags(self):
        if len(sys.argv) > 2:
            self.tags += [tag for tag in sys.argv[2].split(', ')]
        else:
            self.tags += []

        # Compare tags provided vs. standard tags declared in beginning of file
        # if nothing in common then raise error
        if len(self.tags) > 0 and not bool(set(all_tags) & set(self.tags)):
            raise ValueError(f"{sys.argv[2]} is not a valid tag\nTry from: {all_tags}")

        return self.tags

    # Extract only the relevant information from the report
    def parse_report(self, report):
        relevant_info = 'description', 'help', 'helpUrl', 'impact', 'tags'
        parsed = [{key: value for key, value in violation.items() for info in relevant_info if key == info}
                  for violation in report]
        self.parsed_report += parsed

    def run_axe(self):
        axe = Axe(self.driver)
        axe.inject()
        results = axe.run()

        # If no tags provided then attach all violations to report
        if not self.scan_tags():
            [self.full_report.append(violation) for violation in results['violations']]

        # Loop through violations that contain tags provided and attach them to report
        else:
            self.full_report = [violation for violation in results['violations']
                                if not set(violation['tags']).isdisjoint(self.scan_tags())]

        self.parse_report(self.full_report)
        # axe.write_results(
        #         self.full_report, f'{platform.uname()[1]}-{time.strftime("%Y%m%d-%H%M%S")}.json')
        axe.write_results(
                self.parsed_report, f'{platform.uname()[1]}-{time.strftime("%Y%m%d-%H%M%S")}.json')
        self.driver.close()


def main():
    A11y().run_axe()


""" If this file is being run as a script, then include the info
    below: how long the aXe test took to execute. """
if __name__ == '__main__':
    start = time.time()
    sys.stdout.write('Starting Axe Accessibility Test ...\n')
    main()
    sys.stdout.write(
            f"Execution time {(time.time() - start).__round__(2)} Seconds")
    sys.stdout.write('\nFinished Axe Accessibility Test')
