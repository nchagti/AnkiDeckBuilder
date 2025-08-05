# Anki Deck Builder

Build study decks using Anki — the most flexible, customizable, and intelligent flashcarding tool available.

## Why Anki?

Anki combines the **best of the three major study tools** word game players already use:

1. It has a **Desktop** & **Mobile** app like **Zyzzyva**, so you can keep studying offline.
2. Like **Xerafin**, you can study on a web-based interface like AnkiWeb so you don't have to download an app—__and__ Anki will automatically schedule what you have to study next so you don't have to keep manually adding new words to your cardbox every week. 
3. Anki's **FSRS algorithm** was the original inspiration behind **WordVault** __and__ it has an optimizer that uses machine learning to learn your memory patterns and to find parameters that best fit your review history  

If that's not enough, unlike other tools:
* Anki lets you upload **100k+ questions** per deck.
* Using the Anki Deck Builder, you can study **anagrams, leave values, __and__ definitions**.
* You **won't be penalized for missing a day or week of studying** — the FSRS reschedules your flashcards intelligently.

## Getting the most out of Anki

### 1. **Main Decks, Subdecks, and Filtering**

Since the FSRS is best trained on a global context, it is a good idea to **create a Main Deck** with a __lot__ of questions and, within that Main Deck, **multiple subdecks** with different types of questions. 

The Anki Deck Builder **automatically generates tags and fields** for each deck type, allowing you to filter questions using Anki's powerful search tool for targeted study.

- **Subdecks — Prioritize what you study**:
    - Use the tags or fields to create subdecks including subsets of words that you want to focus on.
        - **For example**, if you know you want to learn the top 1000 probability 7- and 8-letter bingos and JQXZ words, but you want to prioritize the bingos, then you can use the tags to create three subdecks within your Main Deck: one with the bingos, one with the JQXZ words, and one with all other words in your Main Deck.
    
- **Fields by deck type**: Use these fields to search filter your decks
   - __Anagrams Deck__: question, answer, length, number of anagrams, number of vowels, number of unique letters, point value, probability orders, playability orders, number of anagrams 
   - __Leaves Deck__: leave, leave value, leave value range 
   - __Definitions Deck__: word, definition 
   

- **Tags by deck type**: Use these fields to search and filter your decks
   - __Anagrams Deck__: length, number of anagrams, number of vowels, probability order (individual), probabliity order (range), playability order (individual), playability order (range), part of speech, alternate spelling, contains jqxz 
   - __Leaves Deck__: length, number of blanks, leave value range 
   - __Definitions Deck__: part of speech, alternate spellings, inner hook 

### 2. **Visual and Algorithmic Customizability**

Customize the **appearance**, **behavior** and **organization** of your study decks:

* **Visuals**:

  - The Anki Deck Builder provides **Zyzzyva-style formatting by default**
  - It also includes **optional** color-coding for 
      - Alphagram answers by anagram count
      - Leaves by the leave-value range, and
      - (soon) Definitions by part of speech
  
  - The **Anki** app lets you easily **customize** fonts, colors, and highlights — no coding required!

* **Review Behavior**:

  * With **Anki**, you can control how many words you want to study every day, just today, or by a particular deck 
  * You can even set different schedules by the day of the week (e.g., fewer cards on weekends)!

* **Organization**:
  * Create your own tags and use the hierarchical tags (`category::subcategory`) to keep decks organized
  * Use subdecks to categorize *types* of questions and prioritize them as you see fit
  * Use flags to mark questions that you want to come back to later

### 3. **Never Restart Your Cardbox Again**

Miss a day or a week of studying? No problem.

* You’ll never be shown more new words than your set daily limit!
* Just change your daily limit if you want to see more words
* The FSRS algorithm will automatically adjust to your schedule — no manual rescheduling needed


## How to Use the Deck Generator

It's pretty simple to create your own deck. To create the deck from the example above, follow these steps: 
1. Create a text file with all words you want to study. This will be the content of your Main Deck, so you should include __all__ the words you want to study. 
2. **For Windows**, download the zipped file from the latest Release and extract `Anki.Deck.Builder.exe` to an accessible location like your Downloads folder. 

   **For MacOS and Linux**, clone the repo and run `cli_make_deck.py`. 

3. Upload your `.txt` file with with one alphagram or word per line and your lexicon database (`.db`) file. 

   I recommend using the [2nd ed. CSW24 Crowdsourced Definitions](https://github.com/jvc56/CrowdsourcedDefs/blob/main/editions/2/CSW24.zip), but you can find your preferred lexicon database file in the following common locations:
    - Windows (Collins Zyzzyva): `C:\Users\<your name>\.collinszyzzyva\lexicons`
    - Windows (NASPA Zyzzyva): `C:\Users\<your name>\Zyzzyva\lexicons`
    - MacOS and Linux (Collins Zyzzyva): ```~/.collinszyzzyva/lexicons`
    - MacOS and Linux (NASPA Zyzzyva): ```~/Zyzzyva/lexicons```
  
4. Choose if you would like the custom color-coding by number of anagrams, the location where you'd like to save your Anki deck, and click `Create Deck`. This will generate a `.apkg` file. 
        
5. Open **Anki**, click `Import File`, and choose the deck (`.apkg`) that you just generated. 

6. **After** importing your deck, click `Create Deck`. Name this deck `<YourMainDeckName>::<FirstSubdeckName>`. This will create an empty subdeck for your Main Deck. 

7. Select your Main deck and click on Browse. In the search field, use the tags or fields to start filtering your deck. In this case, use the following search: `deck:<YourMainDeckName> tag:len7::prob::1-500 OR tag:len7::prob::501-1000 OR tag:len8::prob::1-500 OR tag:len8::prob::501-1000`

8. Select all questions (`Ctrl + A` on Windows or `Cmd + A` on MacOS), right click on the questions, and click `Change Deck`. Choose the subdeck that you just created to move all top 1000 probable 7 and 8-letter words into it.

9. Repeat steps 6-8 to create a subdeck for your JQXZ words. In the search bar, use the query `deck:<YourMainDeckName> tag:len*::jqxz` to find all JQXZ words of all lengths. Move them to your second subdeck.

10. Repeat steps 6-8 to create a third subdeck for all other words in your deck. In the search bar, use the query `deck:<YourMainDeckName> -tag:len7::prob::1-500 AND -tag:len7::prob::501-1000 AND -tag:len8::prob::1-500 AND -tag:len8::prob::501-1000 AND -tag:len*::jqxz`. Move all of these words to your third subdeck.

11. For each subdeck, change the daily new word limit and daily review limit, making sure that the limit for the bingos is greater than that for the JQXZ words, and the limit for the JQXZ words is greater than the limit for all other words in your third subdeck. This will ensure that you're seeing more high probability words than you see JQXZ words, and more JQXZ words than all other words.

12. Make sure that the daily new word limit and review limit for the main deck **either totals or is more than the limits for the subdecks combined**. Suspend low-priority words or change the daily new word limit for the subdeck with all other words to 0 until you're ready to study them. 

13. Adding more questions to existing decks later? No problem.

- Upload another file using the **same Deck name** to append words to an existing deck.


## Importing your Cardbox from Zyzzyva/Xerafin

It will eventually be possible to take your Xerafin or Zyzzyva cardbox and to import it into Anki while keeping your metadata intact.

> *Personally, I didn’t need this —  if enough people would like the Zyzzyva/Xerafin-to-Anki import feature, I might put some work into it.*

