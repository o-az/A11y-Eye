### Run accessibility check either (1) through the Command Line; (2) or as a method in your Python script

#### Decide what violation standards you want to test against or test against all standards
- Clone this repo `$ git clone https://github.com/omar-aziz/a11y-eye`
- Install the required pip modules from `requirements.txt`
- Fix the path in `executable_path` to point to your local webdriver of choice (chromedriver/geckodriver)

### Two ways to run the accessibility test:
#### (1) Through Command Line:
`python a11y.py --url [webpage link] --tags [tags] --browser [webdriver]`

Example:
`$ python a11y.py --url https://www.example.com --tags 'wcag2aa, best-practice' --browser chrome`
-   (Here tag could be any of the Accessibility Standard)
-   If you don't add tags, it will test against all tags
-   All arguments are optional except for `--url`

#### (2) As a method:
-   Import the a11y.py file in your python file,
-   Add the following at top of your file:
```
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from a11y import A11y
```
-   Add `A11y('web-page-URL-here').run_axe()` whereever in your code,
-   You can also optionally use firefox: `A11y('act.org', 'firefox').run_axe()`


For more info on accessibility and aXe, see [Axe API Docs](https://www.deque.com/axe/axe-for-web/documentation/api-documentation/)

