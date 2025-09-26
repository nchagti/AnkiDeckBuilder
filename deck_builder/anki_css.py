def default_anagrams_css():
    return """
    .card {
    font-family: "MS Shell Dlg 2", "Tahoma", sans-serif;
    font-size: 28px;
    text-align: center;
    }

    .entry-table {
    font-family: 'MS Shell Dlg 2', Tahoma, sans-serif;
    font-size: 18px;
    display: grid;
    grid-template-columns: minmax(3ch, max-content) 
                            minmax(3ch, max-content) 
                            minmax(4ch, max-content) 
                            minmax(3ch, max-content) 
                            1fr;
    gap: 0.2em;
    margin-bottom: 1em;
    width: 100%;
    }

    .entry-row {
    display: contents;
    }

    .col.order {
    text-align: center;
    }

    .col.front {
    text-align: right;
    white-space: pre-wrap;
    padding-right: 0.2em;
    }

    .col.anagram {
    text-align: center;
    white-space: pre-wrap;
    }

    .col.back {
    text-align: left;
    white-space: pre-wrap;
    padding-left: 0.05em;
    padding-right: 0.5em;
    }

    .col.definition {
    white-space: pre-wrap;
    word-break: normal;
    overflow-wrap: break-word;
    text-align: left;
    padding-left: 0.25em;
    }
        """

def custom_anagrams_css():
    return default_anagrams_css() + """

    .anagrams_1 {
    background-color: #fdf4ec;
    border: 2px solid #ffcba4;
    padding: 8px;
    border-radius: 6px;
    }

    .anagrams_2 {
    background-color: #f8f2fc; /* lavender */
    border: 2px solid #e3d2f0;
    padding: 8px;
    border-radius: 6px;
    }

    .anagrams_3 {
    background-color: #fdf3f3; /* rosewater */
    border: 2px solid #f4c6cc;
    padding: 8px;
    border-radius: 6px;
    }

    .anagrams_4 {
    background-color: #f0f8f4; /* mint */
    border: 2px solid #c2f2dd;
    padding: 8px;
    border-radius: 6px;
    }

    .anagrams_5 {
    background-color: #f7f3f0; /* mocha */
    border: 2px solid #daccc3;
    padding: 8px;
    border-radius: 6px;
    }

    .anagrams_6 {
    background-color: #eaf1f7; /* sky blue */
    border: 2px solid #d7eafc;
    padding: 8px;
    border-radius: 6px;
    }

    .anagrams_7 {
    background-color: #faf4e5; /* beige yellow */
    border: 2px solid #f0ddb0;
    padding: 8px;
    border-radius: 6px;
    }

    .anagrams_8 {
    background-color: #efeff7; /* Dusty violet-gray */
    border: 2px solid #d8d7e2;
    padding: 8px;
    border-radius: 6px;
    }

    .anagrams_9 {
    background-color: #eef6ee; /* sage */
    border: 2px solid #cfe3d0;
    padding: 8px;
    border-radius: 6px;
    }

    .anagrams_10 {
    background-color: 	#f9ece8; /* peach */
    border: 2px solid 	#e6ccc1;
    padding: 8px;
    border-radius: 6px;
    }

    .anagrams_11 {
    background-color: 	#f0f8f9; /* soft teal */
    border: 2px solid 	#bfe3e7;
    padding: 8px;
    border-radius: 6px;
    }
    
    /* NIGHTMODE */
    .nightMode .anagrams_1 {
	color: black;
    background-color: #ffe7d3; /* orange */
    border: 2px solid #e8b289;
    padding: 8px;
    border-radius: 6px;
    }

    
    .nightMode .anagrams_2 {
    color: black;
    background-color: #f8eeff; /* purple */
    border: 2px solid #c3a5da;
    padding: 8px;
    border-radius: 6px;
    }

    .nightMode .anagrams_3 {
    color: black;
    background-color: #fff0f0; /* pink */
    border: 2px solid #e7a6af;
    padding: 8px;
    border-radius: 6px;
    }
    
    .nightMode .anagrams_4 {
    color: black;
    background-color: #e3fcf0; /* green */
    border: 2px solid #92d8ba;
    padding: 8px;
    border-radius: 6px;
    }
    
    .nightMode .anagrams_5 {
    color: black;
    background-color: #ffebdb; /* brown */
    border: 2px solid #caa48c;
    padding: 8px;
    border-radius: 6px;
    }

    .nightMode .anagrams_6 {
    color: black;
    background-color: #e3f2ff; /* blue */
    border: 2px solid #7da7cf;
    padding: 8px;
    border-radius: 6px;
    }

    .nightMode .anagrams_7 {
    color: black;
    background-color: #fbf5e5; /* yellow */
    border: 2px solid #d8c18c;
    padding: 8px;
    border-radius: 6px;
    }

    .nightMode .anagrams_8 {
    color: black;
    background-color: #efefff; /* violet-gray */
    border: 2px solid #b2b0ca;
    padding: 8px;
    border-radius: 6px;
    }

    .nightMode .anagrams_9 {
    color: black;
    background-color: #e9fbe9; /* green */
    border: 2px solid #a8d4aa;
    padding: 8px;
    border-radius: 6px;
    }

    .nightMode .anagrams_10 {
    color: black;
    background-color: #f9ece8; /* peach */
    border: 2px solid #d7af9e;
    padding: 8px;
    border-radius: 6px;
    }

    .nightMode .anagrams_11 {
    color: black;
    background-color: #ddf6f6; /* blue */
    border: 2px solid #91c0c4;
    padding: 8px;
    border-radius: 6px;}
    """

def default_leaves_css():
    return """.card { 
            font-family: 'MS Shell Dlg 2', Tahoma, sans-serif;
            font-size: 28px;
            text-align: center; 
        }"""

def custom_leaves_css():
    return default_leaves_css() + """
.question-highlight {
        padding-left: 0.6em;
        padding-right: 0.6em;
        border-radius: 4px;
        display: inline-block;
    }

/* NEGATIVE RANGES - red to purple */
.leave_value_less_than_-21 {
  background-color: rgb(70, 0, 88);
  color: white;
} /* deep purple */

.leave_value_-20to-16 {
  background-color: rgb(95, 14, 116);
  color: white;
} /* dark violet */

.leave_value_-15to-11 {
  background-color: rgb(75, 2, 2);
  color: white;
} /* dark red */

.leave_value_-10to-6 {
  background-color: rgb(135, 3, 3);
  color: white;
} /* crimson */

.leave_value_-5to-1 {
  background-color: rgb(251, 52, 52);
  color: black;
} /* light red */

/* NEUTRAL TO POSITIVE - greens to blues */
.leave_value_0-5 {
  background-color: rgb(166, 231, 166);
  color: black;
} /* pale green */

.leave_value_6-10 {
  background-color: rgb(98, 187, 98);
  color: black;
}

.leave_value_11-15 {
  background-color: rgb(30, 120, 30);
  color: white;
} /* foresty? green */

.leave_value_16-20 {
  background-color: rgb(0, 55, 0);
  color: white;
} /* dark green */

.leave_value_21-25 {
  background-color: rgb(0, 88, 75);
  color: white;
} /* bluer-green */

.leave_value_26-30 {
  background-color: rgb(0, 68, 78);
  color: white;
} /* dark teal */

.leave_value_31-35 {
  background-color: rgb(3, 29, 70);
  color: white;
} /* deeper blue */

.leave_value_greater_than_36 {
  background-color: rgb(25, 9, 62);
  color: white;
} /* midnight blue */"""


def default_defs_css():
    return """
        .card {
            font-family: "MS Shell Dlg 2", "Tahoma", sans-serif;
            font-size: 24px;
            text-align: center;
        }

        .definition-answer {
            text-align: left;
            font-size: 18px;
            white-space: pre-wrap;
            font-family: 'MS Shell Dlg 2', Tahoma, monospace;
        }
        """

def custom_defs_css():
    return default_defs_css() + """
    """