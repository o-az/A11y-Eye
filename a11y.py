#!/usr/local/bin/env python3
import contextlib
import time
import sys
import os

from axe_selenium_python import Axe
from selenium import webdriver

impact_levels = [sys.argv[0]]


class A11y:

	def __init__(self):
		self.report = []
		options = webdriver.ChromeOptions()
		options.add_argument("disable-infobars")
		options.add_argument("--disable-extensions")
		options.add_argument("--headless")
		self.driver = \
			webdriver.Chrome(options=options, executable_path='/Users/omarbinsalamah/webdrivers/chromedriver')
		self.driver.get(sys.argv[1])

	def test(self):
		axe = Axe(self.driver)
		axe.inject()
		results = axe.run()

		for violation in results["violations"]:
			if sys.argv[2] in violation["tags"]:
				self.report.append(violation)

		axe.write_results(self.report, 'a11y.json')
		self.driver.close()


# assert len(results["violations"]) == 0, axe.report(results["violations"])


def no_stdout():
	run = A11y()
	with open(os.devnull, 'w') as devnul:
		with contextlib.redirect_stdout(devnul):
			run.test()


def main():
	no_stdout()


if __name__ == '__main__':
	start = time.time()
	sys.stdout.write('Started Axe Accessibility Test\n')
	main()
	sys.stdout.write(f"Execution time {(time.time() - start).__round__(2)} ss")
	sys.stdout.write('\nFinished Axe Accessibility Test')
