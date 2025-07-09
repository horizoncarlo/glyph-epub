const shell = require("terminal-kit").terminal;
const shellStringWidth = require("terminal-kit").stringWidth;
const EpubLib = require("epub");
const { convert } = require("html-to-text");

const fs = require('fs');
const path = require('path');
const logPath = path.join(__dirname, 'debug.log');
function debug(message) {
  const timestamp = new Date().toISOString();
  const line = `[${timestamp}] ${message}\n`;
  fs.appendFileSync(logPath, line);
}
debug("START NEW INSTANCE");

const book = new EpubLib("./books/The-White-Company_Conan-Doyle.epub");
// slowTyping() and spinner() are cool functions, not sure we have a use

const SHELL_HEIGHT_RESERVED = 1; // Number of lines reserved for UI elements, such as the bottom status line

const conversionOptions = {
  // preserveNewlines: true,
  // wordwrap: Math.floor(shell.width * 0.95),
  wordwrap: null,
};

let fullChapter = null;
let currentChapterIndex = null;
let currentPageText = null;
let currentLineIndex = null; // If a number we are paging within a chapter

shell.on("resize", (width, height) => {
  loadChapter();
});

let showingHelp = false;
let exitCount = 0;
shell.on("key", (name, matches, data) => {
  if (showingHelp) {
    showingHelp = false;
    loadChapter();
    return;
  }
  
  /* TODO Ideas
   Table of Contents - also maybe jump? - use a singleColumnMenu
   Better status line at the bottom
   Custom line wrap width, toggle on then input field of number which replaces screen.width wrap
     Do shell.wrapColumn({ width: 30 }); once outside of loadChapter. width = null resets to terminal width
   Loading from in the app (using .fileInput?) and as a command line argument
   If images / links are parsed consistently try to load them or make them clickable?
   */
  switch (name) {
    case "HOME":
      currentLineIndex = null;
      loadChapter();
      break;
    case "END":
      currentLineIndex = fullChapter?.length - 1;
      loadChapter();
      break;
    case "CTRL_HOME":
      currentLineIndex = null;
      currentChapterIndex = 0;
      loadChapter();
      break;
    case "CTRL_END":
      currentLineIndex = null;
      currentChapterIndex = book.flow?.length;
      loadChapter();
      break;
    case "PAGE_UP":
    case "LEFT":
      if (currentLineIndex === null) {
        currentLineIndex = -1; // This will force us back a chapter
      } else {
        currentLineIndex -= shell.height - SHELL_HEIGHT_RESERVED;
      }
      loadChapter();
      break;
    case "PAGE_DOWN":
    case "RIGHT":
      if (currentLineIndex === null) {
        currentChapterIndex++;
      } else {
        currentLineIndex += shell.height - SHELL_HEIGHT_RESERVED;
      }
      loadChapter();
      break;
    case "UP":
      currentLineIndex--;
      loadChapter();
      break;
    case "DOWN":
      currentLineIndex++;
      loadChapter();
      break;
    case "/":
    case "f":
    case "F":
      statusLine().brightYellow("Search feature still in progess"); // TODO Search/find with match highlighting in current page (only?)
      break;
    case "?":
    case "h":
    case "H":
      // TODO Keep Help updated as hotkeys are added
      shell.clear();
      shell.moveTo(1, 2);
      shell.table( [
          [ 'Hotkey', 'Functionality' ],
          [ 'Page Up or Left', 'Up/back a ^/page^' ],
          [ 'Page Down or Right', 'Down/forward a ^/page^' ],
          [ 'Up', 'Up a single ^/line^' ],
          [ 'Down', 'Down a single ^/line^' ],
          [ 'Home', 'Start of the ^/chapter^' ],
          [ 'End', 'End of the ^/chapter^' ],
          [ 'Ctrl+Home', 'Start of the ^/document^' ],
          [ 'Ctrl+End', 'End of the ^/document^' ],
          [ 'F or /', 'Find text in the ^/page^' ],
          [ 'Ctrl+C or Q or Esc', 'Exit the application' ],
          [ 'H or ?', 'This help - you found it!' ]
        ], {
          contentHasMarkup: true,
          hasBorder: true,
          borderChars: 'lightRounded',
          borderAttr: { color: 'blue' },
          firstRowTextAttr: { bold: true },
          width: Math.min(80, Math.ceil(shell.width * 0.75)),
          fit: true   // Activate all expand/shrink + wordWrap
        }
      );
      statusLine().yellow('Press').bold(' any ').yellow('key to return to the document...');
      
      showingHelp = true;
      break;
    case "ESCAPE":
    case "q":
    case "Q":
      exitCount++;
      if (exitCount === 1) {
        statusLine()
          .yellow("Press ")
          .bold(name.charAt(0).toUpperCase() + name.toLowerCase().substring(1))
          .yellow(" again to exit...");
      } else if (exitCount > 1) {
        shell.processExit(0);
      }
      break;
    // TODO Open file...nice in theory to use the built in, but it's a bit janky, and it'd be fun instead to make our own
    // case "o":
    // case "O":
    // case "SHIFT_O":
    //   shell.clear();
    //   shell(`Open a file from ${os.homedir()}`);
    //   shell.fileInput(
    //     { baseDir: os.homedir() } ,
    //     function( error , input ) {
    //       if ( error )
    //       {
    //         shell.red.bold("\nAn error occurs: " + error + "\n");
    //       }
    //       else
    //       {
    //         shell.green("\nYour file is '%s'\n" , input);
    //       }
    //     }
    //   );
    //   break;
    case "CTRL_C":
      shell.red("Exiting...");
      shell.processExit(0);
      break;
    default:
      debug("key pressed=" + name);
      exitCount = 0;
  }
});

function loadChapter() {
  if (currentLineIndex !== null) {
    if (currentLineIndex >= fullChapter?.length) {
      currentLineIndex = null;
      currentChapterIndex++;
    }
    if (currentLineIndex < 0) {
      currentLineIndex = null;
      currentChapterIndex--;
      
      // If we have a cached count of the number of lines, we leverage that to move to the end of the previous chapter
      if (typeof book.flow?.[currentChapterIndex]?.numLines === 'number') {
        // TODO Currently going back a chapter puts us near the end, like a single line change by pressing UP, but we also should go back a whole page via PAGE_UP in the same way
        // currentLineIndex = Math.min(0, book.flow[currentChapterIndex].numLines - shell.height - SHELL_HEIGHT_RESERVED);
        currentLineIndex = book.flow[currentChapterIndex].numLines;
      }
    }
  }
  
  if (currentChapterIndex < 0) {
    debug("Cannot page back further, reached zero end of chapter index=" + currentChapterIndex);
    currentChapterIndex = 0;
  }
  else if (currentChapterIndex > book.flow?.length) {
    debug("Ran out of chapters to move to with index=" + currentChapterIndex + " vs " + book.flow.length);
    currentChapterIndex = book.flow.length;
  }
  
  shell.hideCursor();
  
  const currentChapterObj = getChapterObj();
  book.getChapter(currentChapterObj?.id, (err, html) => {
    const chapterText = convert(html, conversionOptions);
    fullChapter = manualWrap(chapterText);
    
    currentChapterObj.numLines = fullChapter?.length;
    
    debug("Current line index is " + currentLineIndex + " vs count " + fullChapter?.length);

    // We need to page within our chapter
    if (fullChapter?.length > shell.height - SHELL_HEIGHT_RESERVED) {
      if (currentLineIndex === null) {
        currentLineIndex = 0;
      }

      debug(`From line index=${currentLineIndex} and to=${currentLineIndex + shell.height - SHELL_HEIGHT_RESERVED} in chapter index=${currentChapterIndex} (${currentChapterObj.id})`);
      currentPageText = fullChapter
        .slice(
          currentLineIndex,
          currentLineIndex + shell.height - SHELL_HEIGHT_RESERVED
        )
        .join("\n");
    }
    // The entire chapter will fit in a single window
    else {
      debug("Entire chapter (" + currentChapterIndex + ") fits on one page");
      currentLineIndex = null;
      currentPageText = chapterText;
    }

    shell.clear();
    shell.noFormat(currentPageText); // Do noFormat() instead of wrap() because as part of our line calculations we are manually wrapping
    
    updateStatusLine();
    
    shell.hideCursor();
  });
}

function manualWrap(text) {
  // Manual wrapping is necessary because we need the _actual_ displayed lines for our paging
  const charWidth = 1;
  const resultLines = [];
  const paragraphs = text.split('\n');
  
  for (const paragraph of paragraphs) {
    // Handle cases where an original line was empty or contained only whitespace
    if (paragraph.trim().length === 0) {
      resultLines.push('');
      continue;
    }
    
    // Split the paragraph into words - using /\s+/ handles multiple spaces and tabs
    // Filter out any empty strings that might result from multiple spaces
    const words = paragraph.split(/\s+/).filter(word => word.length > 0);
    
    // If a paragraph had no actual words (just spaces) use an empty line
    if (words.length === 0) {
        resultLines.push('');
        continue;
    }
    
    let currentLine = '';
    let currentLineWidth = 0;
    
    for (const word of words) {
      const wordWidth = shellStringWidth(word);
      
      // Case 1: The current line is empty (first word on a new line)
      if (currentLine.length === 0) {
        currentLine = word;
        currentLineWidth = wordWidth;
      }
      // Case 2: Adding the word (with a leading space) fits on the current line
      else if (currentLineWidth + charWidth + wordWidth <= shell.width) {
        currentLine += ' ' + word;
        currentLineWidth += charWidth + wordWidth;
      }
      // Case 3: Adding the word (with a leading space) does NOT fit but the word itself fits on a new line
      else if (wordWidth <= shell.width) {
        resultLines.push(currentLine);
        currentLine = word;
        currentLineWidth = wordWidth;
      }
      // Case 4: The word itself is longer than the terminal width, so it must be broken
      else {
        if (currentLine.length > 0) {
          resultLines.push(currentLine);
        }
        
        currentLine = '';
        currentLineWidth = 0;

        for (const char of word) {
          if (currentLineWidth + charWidth <= shell.width) {
            currentLine += char;
            currentLineWidth += charWidth;
          } else {
            resultLines.push(currentLine);
            currentLine = char;
            currentLineWidth = charWidth;
          }
        }
      }
    }
    
    if (currentLine.length > 0) {
      resultLines.push(currentLine);
    }
  }

  return resultLines;
}

function getChapterObj() {
  return book.flow?.[currentChapterIndex];
}

function statusLine(msg) {
  const toReturn = shell.moveTo(1, shell.height).eraseLine();
  if (msg) {
    return toReturn.wrap(msg);
  }
  return toReturn;
}

function updateStatusLine() {
  statusLine().magenta(
    `Status: w${shell.width}/h${shell.height}, line=${currentLineIndex ?? 0} of ${fullChapter?.length} in chapter=${currentChapterIndex} (${getChapterObj()?.id})`
  );
}

book.on("end", function () {
  shell.windowTitle(book.metadata.title);

  if (!book.flow?.length) {
    shell.red("No chapters found in book");
    shell.processExit(-1);
    return;
  }

  if (currentChapterIndex === null) {
    currentChapterIndex = 0;
  }

  loadChapter();
});

// shell.fullscreen();
// shell.grabInput({ mouse: "button" });
shell.grabInput();
book.parse();
