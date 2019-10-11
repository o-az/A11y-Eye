### Run a quick accessibility test with full control
#### Decide what violation standards you want to test against or test against all standards

- Clone this repo `$ git clone https://github.com/omar-aziz/a11y-axe`
- Install the required pip modules from `requirements.txt`

- Fix the path in `executable_path` to point to your local webdriver of choice (chromedriver/geckodriver)

- Run `python a11y.py [webpage link] [tag]` (here tag could be any of the Accessibility Standard)

For more info on accessibility, see [Axe API Docs](https://www.deque.com/axe/axe-for-web/documentation/api-documentation/)


