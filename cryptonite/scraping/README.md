# Getting the data
To respect the intellectual property of the crosswords' authors, we provide a script for downloading the data. Follow these step to use it:

1. purchase a subscription for [The Telegraph](https://puzzles.telegraph.co.uk/subscribe?icid=puzzles_reg_subnavbar) and [The Times](https://globalstore.thetimes.co.uk/?ILC=INTL-TNL_The_Times-Conversion_Page-Homepage-2020).


2. Update the Telegraph authentication fields in the Cryptonite [config](https://github.com/aviaefrat/cryptonite/blob/main/configs/scraping/cryptonite_v1.json):

   a. Go to the [Telegraph crossword page](https://puzzles.telegraph.co.uk/crossword-puzzles/cryptic-crossword).

   b. Open the developer tools (`Ctrl+Shift+I`).

   c. Locate the Telegraph cookies (`Storage->Cookies`). They should be listed under the domain "https://puzzles.telegraph.co.uk". 

   d. Copy the values of the `details` and `rememberme` cookies to the corresponding fields in the Telegraph authentication [config].


3. Similarly, update the Times authentication:

   a. Go to the [Times crossword page](https://www.thetimes.co.uk/puzzleclub/crosswordclub/) and locate the Times cookies.

   b. Copy the values of the `acs_tnl` and `sacs_tnl` cookies to the corresponding fields in the Times authentication config.

   c. Locate the cookie whose name starts with "remember_puzzleclub_".

   d. In the config file, set the value of "remember_puzzleclub_key" to the _name_ of this cookie and "remember_puzzleclub_value" to the _value_ of this cookie. 


4. Run the scraper:
   ```
   python -m cryptonite.scraping.scraper
   ```