#!/usr/local/bin/env python3
import re
import sys
import time
import argparse
from selenium import webdriver
from axe_selenium_python import Axe
# Tuple of all standard a11y tags
all_tags = 'wcag2a', 'wcag2aa', 'wcag21aa', 'wcag244', 'wcag311', 'wcag143', 'best-practice', \
    'section508', 'section508.22.a', 'section508.22.i', 'experimental', 'cat'


class LinkException(Exception):
    pass


class TagException(Exception):
    pass
# Coming: regex to check if link is valid
# to provide more meaningful Error message


class LinkCheck:
    def __init__(self):
        pass

    @staticmethod
    def check_link(link):
        if not link:
            raise LinkException("You need to provide a link: \
                If you're running from CLI -> --url web-page-link \
                If you're running as import -> Axe('your-link-here').run_axe()")
        elif '.' not in link:
            raise LinkException(f'Link is not formatted correctly -> {link}')
        elif 'http://' not in link or 'https://' not in link:
            return 'https://' + link
        else:
            raise LinkException('Check link you provided')


class Driver:
    """
    In order to make parameters optional, they're set to None
    Reason: Because default is Chrome, so no need to explicitly state
    If Firefox is desired, then explicitly state 'firefox' down in A11y class
    or when using as a method. I,e,. A11y('example.com', 'firefox').run_axe()
    """

    def __init__(
            self,
            driver=None,
            dynamic_link=None,
            options=None,
            path=None):
        """ By default it will be pointing to chromedriver, using
            the browser options for Chrome browser and using Chrome
            driver unless explicitly calling 'firefox'
        """
        self.driver = driver
        self.options = options
        self.path = path
        # The URL for when it's used as a stand alone with CLI arguments
        self.url_argument = args.url
        # The URL for when it's used as an imported file
        self.dynamic_link = dynamic_link
        # Link of web-page to be aXe-d
        self.link = self.url_argument if self.url_argument else self.dynamic_link
        self.link = LinkCheck.check_link(self.link)
        self.driver_setup().get(self.link)

    def driver_path(self):
        if self.driver is not None and self.driver.lower() == 'firefox':
            self.path = 'C:/Users/salalmao/repos/a11y-axe/drivers/geckodriver.exe'
        else:
            self.path = 'C:/Users/salalmao/repos/a11y-axe/drivers/chromedriver.exe'
        return self.path

    def driver_options(self):
        if self.driver is not None and self.driver.lower() == 'firefox':
            self.options = webdriver.FirefoxOptions()
        else:
            self.options = webdriver.ChromeOptions()
            # Add pop-up disabler arg option
            chrome_arguments = [
                "disable-infobars",
                "--disable-extensions",
                "--headless"]
            for argument in chrome_arguments:
                self.options.add_argument(argument)
            self.options.add_experimental_option(
                'excludeSwitches', ['enable-logging'])
            self.options.add_experimental_option(
                "useAutomationExtension", False)
        return self.options

    def driver_setup(self):
        if self.driver is not None and self.driver == 'firefox':
            self.driver = webdriver.Firefox(
                options=self.driver_options(),
                executable_path=self.driver_path())
        else:
            self.driver = webdriver.Chrome(
                options=self.driver_options(),
                executable_path=self.driver_path())
        return self.driver


class A11y(Driver):
    def __init__(self, link=None, browser=None):
        # # The tag/s and browser for when it's used as a stand alone with CLI arguments
        self.tags_argument = args.tags
        self.broswer_argument = args.browser
        """
        :param browser: Optionally specify to 'firefox' or ignore it and it'll default to chrome.
        :param link: When using it as a method, specify the link to the web-page you want to test
        # Like this: A11y(''www.example.com', 'firefox').run_axe(), or leave the 2nd parameter empty
        """
        if self.broswer_argument == 'firefox':
            super().__init__(driver='firefox')
        elif browser is not None and browser == 'firefox':
            super().__init__(driver='firefox', dynamic_link=link)
        else:
            super().__init__(dynamic_link=link)
        self.full_report = []
        self.parsed_report = []
        self.tags = []
    """
    In command line, you can pass tags in a string separated by commas for example, "wcag2aa, section508",
    or you can run as a method and it will by default test for wcag2aa. I,e,. Axe('example.com').run_axe()
    If you don't pass anything, it will test for wcag2aa only
    """

    def scanned_tags(self):
        if self.tags_argument:
            self.tags += [tag for tag in self.tags_argument.split(', ')]
        else:
            self.tags = ['wcag2aa']
        # Compare tags provided vs. standard tags declared in beginning of file
        # if nothing in common then raise error
        if len(self.tags) > 0 and not bool(set(all_tags) & set(self.tags)):
            raise TagException(
                f"{self.tags} is not a valid tag. Try from: {all_tags}")
        return self.tags
    """
    Not all info in the aXe report concern us. This function checks the relevant_info,
    loops through the report (which is a list of dicts) and within each dict,
    it loops through the keys and checks if key matches any info from relevant_info
    """

    def parse_report(self, report):
        relevant_info = 'description', 'help', 'helpUrl', 'impact', 'tags'
        parsed = [{key: value for key, value in violation.items(
        ) for info in relevant_info if key == info} for violation in report]
        self.parsed_report += parsed
    # Convenient, readable file name generator
    @staticmethod
    def file_name(name):
        formatted_name = re.sub('https|http|www.|:|/|=|[?]', '', name)
        date_time = time.strftime("%Y%m%d-%H%M%S")
        return formatted_name + date_time + '.json'

    def run_axe(self):
        axe = Axe(self.driver)
        axe.inject()
        results = axe.run()
        # If no tags provided then attach all violations to report
        if not self.scanned_tags():
            [self.full_report.append(violation)
             for violation in results['violations']]
        # Loop through violations that contain tags provided and attach them to
        # report
        else:
            [self.full_report.append(violation) for violation in results['violations']
             if not set(violation['tags']).isdisjoint(self.scanned_tags())]
        if len(self.full_report) == 0:
            self.parsed_report.append(
                {"No a11y violations found for the following tags": list(set(self.scanned_tags()))})
        else:
            self.parse_report(self.full_report)
        axe.write_results(self.parsed_report, self.file_name(self.link))
        self.driver.close()


def main():
    A11y().run_axe()


""" Command Line Arguments for when running file directly """
parser = argparse.ArgumentParser(description='aXe accessibility script')
parser.add_argument(
    "--url",
    help="Specify web-page link you want to run aXe on")
parser.add_argument(
    "--browser",
    help="Chrome by default but you can optionally use firefox")
parser.add_argument("--tags", help="Provide tags you want to test against. \
                    If multiple then surround by quotes 'wcag2aa, best-practice'")
args = parser.parse_args()
""" If this file is being run as a script, then allow for CLI arguments. """
if __name__ == '__main__':
    start = time.time()
    sys.stdout.write('Starting Axe Accessibility Test ...\n')
    parser
    aXe = A11y()
    aXe.run_axe()
    sys.stdout.write(
        f"Execution time {(time.time() - start).__round__(2)} Seconds")
    sys.stdout.write('\nFinished Axe Accessibility Test')
