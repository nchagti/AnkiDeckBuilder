def default_anagrams_css():
    return """
  @font-face {
      font-family: myfont;
      src: url("_protiles.ttf");
    }

  /* ---------- Set up ---------- */
  .card {        
    --tile-size: 40px;
    --tile-gap: 2px;
    --tile-radius: 4px;

    --tile-face: #441b82;
    --tile-edge: #280f4d;
    --tile-text: #f7f7f7;
    --tile-shadow: rgba(22, 7, 43, 0.25);
  }

  .nightMode.card {
    /* Dark tiles */
    --tile-face: #381754;
    --tile-edge: #250f38;
    --tile-text: #f7f7f7;
    --tile-shadow: rgba(21,5,33,0.35);
  }

  a {
  text-decoration: none;
  display: block;
  }

  /* ---- Rack container for when i get my shit together ---- */
  .rack {
      position: relative;
      width: 100%;
      height: calc(var(--tile-size) * 1.2);
      padding-top: 5px;
      display: flex;
      justify-content: center;
      align-items: center;
    }


    /* ---------- Tile row ---------- */
    .tiles {
      position: relative;
      display: flex;
      justify-content: center;
      gap: var(--tile-gap);
    }

  /* ---------- Individual tile ---------- */
  .tile {
    width: calc(var(--tile-size) * 1.1);
    height: calc(var(--tile-size) * 1.1);
    border-radius: var(--tile-radius);

    display: grid;
    place-items: center;
              
    font-family: myfont;
    font-size: calc(var(--tile-size) * 1);
    line-height: 1;
    color: var(--tile-text);
    letter-spacing: 0em ;

    background:
    linear-gradient(to bottom,
      rgba(255,255,255,0.05) 0%,
      rgba(255,255,255,0.0) 30%,
      var(--tile-face) 30%),
    var(--tile-face);

  box-shadow:
    0 4px 6px var(--tile-shadow),
    inset 0 1px 0 rgba(249, 245, 252, 0.2),
    inset 0px -1px 0px rgba(20, 5, 40, 0.3),
    inset 1px 0px 1px 0px rgba(243, 235, 240, 0.2),
    inset -1px 0px 1px 0px rgba(243, 235, 240, 0.2);
    
    border-top: 3px solid rgba(180, 150, 255, 0.35);
  }

  .nightMode .tile {
    background:
    linear-gradient(to bottom,
      rgba(240,240,240,0.05) 0%,
      rgba(240,240,240,0.0) 30%,
      var(--tile-face) 30%),
    var(--tile-face);

    box-shadow:
      0 4px 6px var(--tile-shadow),
      inset 0 1px 0 rgba(240, 225, 252, 0.2),
      inset 0px -1px 0px rgba(22, 5, 36, 0.3),
      inset 1px 0px 1px 0px rgba(183, 157, 204, 0.2),
      inset -1px 0px 1px 0px rgba(183, 157, 204, 0.2);

    border-top: 3px solid rgba(155, 107, 194, 0.35);
  }

  .letter {
    padding-top: 5px;
    padding-left: 5px;
  }

  /* ---------- Buttons ---------- */
  .controls {
    width: 100%; 
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    gap: 0.6em;
    margin-top: 0.5em;
  }


  .rack, .controls {
  box-sizing: border-box;
  }

  .ctrl-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: calc(var(--tile-size) * 0.95);
    height: calc(var(--tile-size) * 0.95);
    border-radius: 6px;
    border: 1.5px solid rgba(0, 0, 0, 0.15);
    background: rgba(0, 0, 0, 0.08);
    color: #555;
    cursor: pointer;
    transition: background 0.15s, border-color 0.15s, transform 0.1s;
    padding: 0;
  }

  .ctrl-btn svg {
    width: calc(var(--tile-size) * 0.45);
    height: calc(var(--tile-size) * 0.45);
  }

  .ctrl-btn:hover {
    background: rgba(0, 0, 0, 0.14);
    border-color: rgba(0, 0, 0, 0.3);
    color: #222;
  }

  .nightMode .ctrl-btn {
    border: 1.5px solid rgba(255, 255, 255, 0.25);
    background: rgba(255, 255, 255, 0.08);
    color: #ccc;
  }

  .nightMode .ctrl-btn:hover {
    background: rgba(255, 255, 255, 0.18);
    border-color: rgba(255, 255, 255, 0.45);
    color: #fff;
  }

  .ctrl-btn:active {
    transform: scale(0.92);
  }

  .tile.hint-active {
    box-shadow:
      0 4px 6px var(--tile-shadow),
      inset 0 1px 0 rgba(249, 245, 252, 0.2),
      inset 0px -1px 0px rgba(20, 5, 40, 0.3),
      inset 1px 0px 1px 0px rgba(243, 235, 240, 0.2),
      inset -1px 0px 1px 0px rgba(243, 235, 240, 0.2);
    
    border-top: 3px solid rgba(180, 150, 255, 0.35);
    transform: translateY(-12px);
  }
  .nightMode .tile.hint-active {
    box-shadow:
      0 4px 10px var(--tile-shadow),
      inset 0 1px 0 rgba(240, 225, 252, 0.2), /* the tiny strip of light between the top edge and the tile face */
      inset 0px -1px 0px rgba(22, 5, 36, 0.3), /* inner shadow at the bottom */
      inset 1px 0px 1px 0px rgba(183, 157, 204, 0.2), /* light on the left */
      inset -1px 0px 1px 0px rgba(183, 157, 204, 0.2); /*light on the right */

    border-top: 3px solid rgba(155, 107, 194, 0.35);
    transform: translateY(-12px);
  }

    /* ----- Back of card ----- */

    .entry-table {
    font-family: 'MS Shell Dlg 2', Tahoma, sans-serif;
    font-size: 18px;
    display: grid;
    grid-template-columns: minmax(3ch, max-content) 
                            minmax(1ch, max-content) 
                            minmax(4ch, max-content) 
                            minmax(1ch, max-content) 
                            1fr;
    gap: 0.15em;
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
    padding-left: 0.7em;
    }

    .col.anagram {
    text-align: center;
    white-space: pre-wrap;
    padding-left: 0.25em;
    }

    .col.back {
    text-align: left;
    white-space: pre-wrap;
    padding-left: 0.25em;
    }

    .col.definition {
    white-space: pre-wrap;
    word-break: normal;
    overflow-wrap: break-word;
    text-align: left;
    padding-left: 0.9em;
    }
    """

def custom_colors_css():
    return """
    
    /* COLORS FOR ANAGRAM TAGS */
    .anagrams_1 {
    background-color: #fdf4ec; /* orange */
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
    background-color: 	#f9ece8; /* peach */
    border: 2px solid 	#e6ccc1;
    padding: 8px;
    border-radius: 6px;
    }

    .anagrams_10 {
    background-color: #eef6ee; /* sage */
    border: 2px solid #cfe3d0;
    padding: 8px;
    border-radius: 6px;
    }

    .anagrams_11 {
    background-color: #f8ebeb; /* rose-red */
    border: 2px solid #fdaaaa;
    padding: 8px;
    border-radius: 6px;
    }

    .anagrams_12 {
    background-color: 	#f0f8f9; /* soft teal */
    border: 2px solid 	#bfe3e7;
    padding: 8px;
    border-radius: 6px;
    }

    .anagrams_13 {
    background-color: 	#f8f2eb; /* ochre */
    border: 2px solid 	#fad2a4;
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
    background-color: #f4ebfc; /* purple */
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
    background-color: #f7e7e7; /* rose-red */
    border: 2px solid #fdaaaa;
    padding: 8px;
    border-radius: 6px;}

    .nightMode .anagrams_12 {
    color: black;
    background-color: #ddf6f6; /* blue */
    border: 2px solid #91c0c4;
    padding: 8px;
    border-radius: 6px;}

    .nightMode .anagrams_13 {
    color: black;
    background-color: 	#f8f2eb; /* ochre */
    border: 2px solid 	#fad2a4;
    padding: 8px;
    border-radius: 6px;
    }
    """

def custom_anagrams_css():
    return default_anagrams_css() + "\n\n" + custom_colors_css()

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